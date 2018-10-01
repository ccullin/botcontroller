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
        self.connect(broker, keepalive=120)
        self.loop_start()        
        
    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            log.debug("connected OK Returned code= {}".format(rc))
            for bot in self.botController.bots:
                log.debug("subscribing to {} for event and response".format(bot))
                self.subscribe(bot+'/event')
                self.subscribe(bot+'/response')
        else:
            log.debug("Bad connection Returned code= {}".format(rc))
    
    def on_disconnect(self, client, userdata, rc):
        log.debug("disconnected with code: {}".format(rc))

    def __on_response(self, client, userdata, message):
        log.debug("response received {}".format(str(message.payload.decode("utf-8"))))
        log.debug("response topic= {}".format(message.topic))
        msg = message.payload.decode("utf-8")
        #msgDict = json.loads(msg)
        msgDict = json.loads(msg.replace("'", '"'))
        self.botController.sendMessage(**msgDict)
 
    def __on_event(self, client, userdata, message):
        log.debug("event received {}".format(str(message.payload.decode("utf-8"))))
        log.debug("event topic= {}".format(message.topic))
        msg = message.payload.decode("utf-8")
        topic = message.topic
        sender = topic.split("/")
        # jsonMsg = json.loads(msg.replace("'", '"'))
        # msgDict = json.loads(msg)
        self.botController.sendEvent(sender[0], msg)

    def on_message(self, client, userdata, message):
        log.debug("message received {}".format(str(message.payload.decode("utf-8"))))
        log.debug("message topic= {}".format(message.topic))
        log.debug("message qos= {}".format(message.qos))
        log.debug("message retain flag= {}".format(message.retain))
        
