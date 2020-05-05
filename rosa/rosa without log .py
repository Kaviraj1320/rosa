import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
import json 
import os 
import threading
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
syrenpin = 23
ledpin = 24
GPIO.setup(syrenpin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(ledpin, GPIO.OUT, initial=GPIO.HIGH)
# Our "on message" event

ourClient = mqtt.Client(client_id="Rosa1") # Create a MQTT client objecttts   
ourClient.username_pw_set("6384037102", "katomaran2015$")
ourClient.connect("159.65.152.75", 1883) # Connect to the test MQTT broker
ourClient.subscribe("message") # Subscribe to the topic AC_unit

def translate(value, leftMin, leftMax, rightMin, rightMax):
   leftSpan = leftMax - leftMin
   rightSpan = rightMax - rightMin
   valueScaled = float(value - leftMin) / float(leftSpan)
   return rightMin + (valueScaled * rightSpan)

def lighton(stop):
   while True :
      GPIO.output(ledpin, GPIO.LOW)
      time.sleep(1)
      GPIO.output(ledpin, GPIO.HIGH)
      time.sleep(1)
      if stop(): 
         break

def soundon(revdata):
   data=revdata
   if(data["Syren"]["status"] == "on" ):
      GPIO.output(syrenpin, GPIO.LOW)
      time.sleep(data["Syren"]["duration"])
      GPIO.output(syrenpin, GPIO.HIGH)
   
def lastsound(data):
   if(data["Syren"]["status"] == "on" ):
      GPIO.output(syrenpin, GPIO.LOW)
      time.sleep(2)
      GPIO.output(syrenpin, GPIO.HIGH)


def voiceon(revdata):
   
   data=revdata
   volume = translate(data["Speech"]["volume"],0,100,-6000,1000)
   
   language = 'en'
   if (data["Speech"]["voicespeed"] == "slow") :
      speech = gTTS(text = data["Speech"]["message"], lang = language, slow = True)
      print("hai")
   else:
      speech = gTTS(text = data["Speech"]["message"], lang = language, slow = False)
      print("hi")  
   speech.save("text.mp3")

   i=0
   while i < data["Speech"]["repeat"]:
     str1="omxplayer --vol "  
     str2=" /home/pi/text.mp3"
     cmd = str1 + str(volume)
     cmd= cmd + str2
     os.system(cmd)
     i=i+1

def messageFunction(client, userdata, message):
   topic = str(message.topic)
   rec_json = str(message.payload.decode("utf-8"))
   text = str(rec_json)
   data= json.loads(text)
   stop_threads = False
   t1 = threading.Thread(target=lighton , args=(lambda : stop_threads, ))
   t1.start()
   soundon(data)
   voiceon(data)
   #lastsound(data)
   stop_threads = True
   
ourClient.on_message = messageFunction # Attach the messageFunction to subscription
ourClient.loop_start() #


while(1):
   time.sleep(1) # Sleep for a second''' 
