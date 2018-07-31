import paho.mqtt.client as mqtt
import json
import logging

# local imports
import logger

# logger for this module
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class MQTT(mqtt.Client):
    def __init__(self, broker, name, botController):
        super().__init__(name)
        self.botController = botController
        self.message_callback_add("+/response", self.__on_response)
        self.message_callback_add("+/event", self.__on_event)
        self.connect_async(broker)
        self.loop_start()        
        
    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("connected OK Returned code=",rc)
        else:
            print("Bad connection Returned code=",rc)
    
    def __on_response(self, client, userdata, message):
        log.debug("message received {}".format(str(message.payload.decode("utf-8"))))
        log.debug("message topic= {}".format(message.topic))
        msg = message.payload.decode("utf-8")
        jsonMsg = json.loads(msg.replace("'", '"'))
        self.botController.sendMessage(**jsonMsg)
 
    def __on_event(self, client, userdata, message):
        log.debug("message received {}".format(str(message.payload.decode("utf-8"))))
        log.debug("message topic= {}".format(message.topic))
        msg = message.payload.decode("utf-8")
        jsonMsg = json.loads(msg.replace("'", '"'))
        self.botController.sendEvent(**jsonMsg)

    def on_message(self, client, userdata, message):
        log.debug("message received {}".format(str(message.payload.decode("utf-8"))))
        log.debug("message topic= {}".format(message.topic))
        log.debug("message qos= {}".format(message.qos))
        log.debug("message retain flag= {}".format(message.retain))
        
