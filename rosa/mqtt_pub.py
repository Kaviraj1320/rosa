import paho.mqtt.client as mqtt
import json

def on_publish(client,userdata,result):
    print("data published")
    pass
client = mqtt.Client("P1")
client.username_pw_set(username="6384037102", password="katomaran2015$")
client.connect("159.65.152.75", 1883)
client.on_publish = on_publish

entry_data = json.dumps({"Serialid":"00000000b4064ffd","data":{"Speech":{"message":"welcome to interlace.","repeat":2,"voicespeed":"fast","volume":100},"Syren":{"status":"on","duration":3}},"device":"health_checkup"})
#,"settings":{"username":"6384037102","password":"katomaran2015$","broker":"159.65.152.75","port":1883,"sendtopic":"message8","rec_topic":"star"}
#entry_data = json.dumps({"Status":"what","Serialid":"00000000b4064ffd"})
#entry_data = json.dumps({"Status":"config","Serialid":"00000000b4064ffd"})
#entry_data=json.dumps({"Status":"config","Serialid":"00000000b4064ffd","username":"6384037102","password":"katomaran2015$","broker":"159.65.152.75","port":1883,"sendtopic":"message8","rec_topic":"star"})
entry_data = json.dumps({"Serialid":"00000000b4064ffd","device":"shutdown"})
print(entry_data)
ret= client.publish("message8",entry_data)

print(ret)
