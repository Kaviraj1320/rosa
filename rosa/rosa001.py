
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
from gtts import gTTS 
import json 
import os 
import threading
import logging
from logging.handlers import RotatingFileHandler
import requests
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
syrenpin = 23
ledpin = 24
GPIO.setup(syrenpin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(ledpin, GPIO.OUT, initial=GPIO.HIGH)
# Our "on message" event
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(funcName)s(%(lineno)d) %(message)s')
#FORMAT = '%(asctime)-15s %(levelname)s %(filename)s %(message)s'
#logging.basicConfig(format=FORMAT,level=logging.DEBUG,filename='example.log')
logFile = '/home/katomaran/wemas.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=10*1024*1024, 
                                 backupCount=5, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.DEBUG)

log = logging.getLogger('root')
log.setLevel(logging.DEBUG)

log.addHandler(my_handler)
def logging(message):

	data = { "version": "1.1", "host": "wemas", "short_message": message,"time":time.time() "level": 5, "_some_info": "foo" }
	r = requests.post(url = 'https://graylog-gelf.katomaran.tech/gelf', json = data)
	
	

ourClient = mqtt.Client(client_id="Rosa8") # Create a MQTT client objecttts   
ourClient.username_pw_set("6384037102", "katomaran2015$")
ourClient.connect("159.65.152.75", 1883) # Connect to the test MQTT broker
ourClient.subscribe("message8") # Subscribe to the topic AC_unit

def translate(value, leftMin, leftMax, rightMin, rightMax):
   try:
      leftSpan = leftMax - leftMin
      rightSpan = rightMax - rightMin
      valueScaled = float(value - leftMin) / float(leftSpan)
      return rightMin + (valueScaled * rightSpan)
   except Exception as e:
      message(str(e)) 
      

def lighton(stop):
   while True :
      try:
         GPIO.output(ledpin, GPIO.LOW)
         time.sleep(1)
         GPIO.output(ledpin, GPIO.HIGH)
         time.sleep(1)
         if stop(): 
            break
      except Exception as e:
         log.debug("lighton : "+str(e)) 

def soundon(revdata):
   try:
      data=revdata
      if(data["Syren"]["status"] == "on" ):
         GPIO.output(syrenpin, GPIO.LOW)
         time.sleep(data["Syren"]["duration"])
         GPIO.output(syrenpin, GPIO.HIGH)
   except Exception as e:
      log.debug("translate : "+str(e)) 
   
def lastsound(data):
   try:
      if(data["Syren"]["status"] == "on" ):
         GPIO.output(syrenpin, GPIO.LOW)
         time.sleep(2)
         GPIO.output(syrenpin, GPIO.HIGH)
   except Exception as e:
      log.debug("lastsound : "+str(e)) 


def voiceon(revdata):
   try:
      data=revdata
      volume = translate(data["Speech"]["volume"],0,100,-6000,1000)   
      language = 'en'
      if (data["Speech"]["voicespeed"] == "slow") :
         speech = gTTS(text = data["Speech"]["message"], lang = language, slow = True)
         #print("hai")
      else:
         speech = gTTS(text = data["Speech"]["message"], lang = language, slow = False)
      #print("hi")  
      speech.save("/home/katomaran/text.mp3")

      i=0
      while i < data["Speech"]["repeat"]:
         try:
            str1="omxplayer --vol "  
            str2=" /home/katomaran/text.mp3"
            cmd = str1 + str(volume)
            cmd= cmd + str2
            os.system(cmd)
            i=i+1
         except Exception as e:
            log.debug("voiceon: number of time voice play : "+str(e))
   except Exception as e:
      log.debug("voiceon : "+str(e))

def getSerialid():
   # Extract serial from cpuinfo file
   cpuserial = "0000000000000000"
   try:
      f = open('/proc/cpuinfo', 'r')
      for line in f:
         if line[0:6] == 'Serial':
            cpuserial = line[10:26]
      f.close()
   except:
      cpuserial = "ERROR000000000"
   return cpuserial

def messageFunction(client, userdata, message):
   topic = str(message.topic)
   rec_json = str(message.payload.decode("utf-8"))
   text = str(rec_json)
   data= json.loads(text)
   print(data)
   try:
      if(data["Serialid"] == getSerialid()):
         stop_threads = False
         t1 = threading.Thread(target=lighton , args=(lambda : stop_threads, ))
         t1.start()
         soundon(data)
         voiceon(data)
         #lastsound(data)
         stop_threads = True
   except Exception as e:
      log.debug("messageFunction : "+str(e))
         
         
ourClient.on_message = messageFunction # Attach the messageFunction to subscription
ourClient.loop_forever() #


