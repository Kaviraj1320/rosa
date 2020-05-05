import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt  # Import the MQTT library
import time  # The time library is useful for delays
from gtts import gTTS
import json
import os
import sys
import threading
import requests
import time

with open('data.txt') as json_file:
    config_data = json.load(json_file)

user_name=config_data["settings"]["username"]
password=config_data["settings"]["password"]
broker=config_data["settings"]["broker"]
port=config_data["settings"]["port"]
sendtopic=config_data["settings"]["sendtopic"]
rec_topic=config_data["settings"]["rec_topic"]
print(user_name)
print(password)
print(broker)
print(port)
print(sendtopic)
print(rec_topic)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
syrenpin = 23
ledpin = 24
GPIO.setup(syrenpin, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(ledpin, GPIO.OUT, initial=GPIO.HIGH)

# Root Path
root_path = "/home/katomaran/"

#get serialid


#graylog
def logging(shot_msg,message):

	logger = { "version": "1", "host": "wemas", "short_message": shot_msg, "full_message": message, "time":time.time(), "level": 5 ,"_user_id": "wemas-rosa008"}
	r = requests.post(url = 'https://graylog-gelf.katomaran.tech/gelf', json = logger)

#volume mapping
def translate(value, leftMin, leftMax, rightMin, rightMax):
    try:
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin
        valueScaled = float(value - leftMin) / float(leftSpan)
        return rightMin + (valueScaled * rightSpan)
    except Exception as e:
        logging("translate  " , str(e))

#red led on/off
def lighton(stop):
    while True:
        try:
            GPIO.output(ledpin, GPIO.LOW)
            time.sleep(1)
            GPIO.output(ledpin, GPIO.HIGH)
            time.sleep(1)
            if stop:
                break
        except Exception as e:
            logging("lighton" , str(e))

#syren on
def soundon(revdata):
    try:
        if revdata["data"]["Syren"]["status"] == "on":
            GPIO.output(syrenpin, GPIO.LOW)
            time.sleep(revdata["data"]["Syren"]["duration"])
            GPIO.output(syrenpin, GPIO.HIGH)
    except Exception as e:
        logging("translate " , str(e))


def lastsound(data):
    try:
        if data["data"]["Syren"]["status"] == "on":
            GPIO.output(syrenpin, GPIO.LOW)
            time.sleep(2)
            GPIO.output(syrenpin, GPIO.HIGH)
    except Exception as e:
        logging("last sound " , str(e))

#text to speech
def voiceon(revdata):
    try:
        data = revdata
        volume = translate(data["data"]["Speech"]["volume"], 0, 100, -6000, 1000)
        language = 'en'
        if data["data"]["Speech"]["voicespeed"] == "slow":
            speech = gTTS(text=data["data"]["Speech"]["message"], lang=language, slow=True)
        else:
            speech = gTTS(text=data["data"]["Speech"]["message"], lang=language, slow=False)
        speech.save(root_path + "text.mp3")
        i = 0
        while i < data["data"]["Speech"]["repeat"]:
            try:
                str1="omxplayer --vol "  
                str2=" /home/katomaran/text.mp3"
                cmd = str1 + str(volume)
                cmd= cmd + str2
                os.system(cmd)
                i=i+1
            except Exception as e:
                log.debug("voiceon: number of time voice play : " + str(e))
    except Exception as e:
        logging("voiceon", str(e))

#device serialid
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

def config(client,data,Serialid):
    if data.get("device"):
        if data["device"] == "health_checkup": 
            reply=(json.dumps({"Serialid":Serialid,"Statusreply":"online"}))
            client.publish(rec_topic, reply)
        elif data["device"] == "shutdown":
            stop_threads = True
            os.system("shutdown now")
        elif data["device"] == "reboot":
            stop_threads = True
            os.system("sudo reboot")
    if data.get("settings"):
        with open('/home/katomaran/data.txt', 'w') as outfile:
            json.dump(data, outfile)

def messageFunction(client, userdata, message):
    #logging.debug("Topic  :  " + str(message.topic))
    data = json.loads(str(message.payload.decode("utf-8")))
    #logging.info(data)
    Serialid=getSerialid()
    try:
        if data.get("Serialid"):
            if data["Serialid"] == Serialid:
                config(client,data,Serialid)
                stop_threads = False
                t1 = threading.Thread(target=lighton, args=(lambda: stop_threads,))
                t1.start()
                soundon(data)
                voiceon(data)
                stop_threads = True
            elif data["Serialid"] == "*":
                reply=(json.dumps({"Serialid":Serialid}))
                client.publish(rec_topic, reply)

    except Exception as e:
        logging("messageFunction" , str(e))

def on_connect(client, userdata, flags, rc):
    print("connected")



def main():
    try:
        ourClient = mqtt.Client(client_id="Rosa8")  # Create a MQTT client objecttts
        ourClient.username_pw_set(user_name, password)
        ourClient.connect(broker, port)  # Connect to the test MQTT broker
        ourClient.on_connect= on_connect 
        ourClient.subscribe(sendtopic)  
        ourClient.on_message = messageFunction 
        ourClient.loop_forever()
    except KeyboardInterrupt:
	    sys.exit(0)
    except Exception as e:
        logging("Main Function" , str(e))
        main()
        


if __name__ == '__main__':
    main()


