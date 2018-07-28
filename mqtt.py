import paho.mqtt.client as mqtt
import logging

# local imports
import logger

# logger for this module
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class MQTT(mqtt.Client):
    def __init__(self, broker, name):
        super().__init__(name)
        # client=mqtt.Client("botcontroller")
        # self.on_connect=self.onconnect
        # self.on_message=self.onmessage
        self.connect(broker)
        self.counter=0
        self.loop_start()        
        
    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("connected OK Returned code=",rc)
        else:
            print("Bad connection Returned code=",rc)
    
    
    def on_message(self, client, userdata, message):
        print("message received " ,str(message.payload.decode("utf-8")))
        print("message topic=",message.topic)
        print("message qos=",message.qos)
        print("message retain flag=",message.retain)
        
        
