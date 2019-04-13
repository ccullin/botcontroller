import paho.mqtt.client as mqtt
import json
import logging
import time

#to catch socket conection errors
import errno
from socket import error as socket_error

# local imports
import logger

# logger for this module
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class MQTT(mqtt.Client):
    def __init__(self, broker, name, botController):
        super().__init__(name)
        self.broker = broker
        self.botController = botController
        self.message_callback_add("+/response", self.__on_response)
        self.message_callback_add("+/event", self.__on_event)
        self.on_connect = self.on_connect
        self.on_disconnect = self.on_disconnect
        self.on_unsubscribe = self.on_unsubscribe
        self.setupConnection()
        self.loop_start()        
        
    def setupConnection(self):
        connected = False
        while not connected:
            try:
                self.connect(self.broker)
                connected = True
            except socket_error as serr:
                if serr.errno != errno.ECONNREFUSED:
                    # Not the error we are looking for, re-raise
                    raise serr
                # connection refused
                log.debug("the connection to the MQTT broker was refused")
                time.sleep(10)
                

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
        
    def on_unsubscribe(self, client, userdata, mid):
        log.warning("bot unsubscribed from channel")

    def __on_response(self, client, userdata, message):
        log.debug("response received {}".format(str(message.payload.decode("utf-8"))))
        log.debug("response topic= {}".format(message.topic))
        msg = message.payload.decode("utf-8")
        msgDict = json.loads(msg.replace("'", '"'))
        self.botController.sendMessage(**msgDict)
 
    def __on_event(self, client, userdata, message):
        log.debug("event received {}".format(str(message.payload.decode("utf-8"))))
        log.debug("event topic= {}".format(message.topic))
        msg = message.payload.decode("utf-8")
        topic = message.topic
        sender = topic.split("/")
        self.botController.sendEvent(sender[0], msg)

    def on_message(self, client, userdata, message):
        log.debug("message received {}".format(str(message.payload.decode("utf-8"))))
        log.debug("message topic= {}".format(message.topic))
        log.debug("message qos= {}".format(message.qos))
        log.debug("message retain flag= {}".format(message.retain))
        
