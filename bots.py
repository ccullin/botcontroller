import requests
import json
import logging

#local imports
from Twitter import webAPI
from mongodb import Mongodb
from mqtt import MQTT

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class BotController(object):
    def __init__(self, config):
        self.broker = config.get('mqtt_host')
        self.name = config.get('name')
        self.keysDB = Mongodb(**config.get('mongodb'))
        self.bots = {}
        self.config = config.get('webAPI')
        self.api = webAPI(self.config)

    def run(self):
        self.api.registerController()
        for bot, config in self.config.get('bots').items():
            self.bots[bot] = Bot(bot, config, self.keysDB)
            r = self.api.subscribeBot(**self.bots[bot].credentials)
            log.debug("subscription response code = '{}".format(r))
        self.mqtt = MQTT(self.broker, name=self.name, botController=self)
    
    def newCommand(self, command):
        log.debug('command = {}'.format(command))
        botWebName = command.get('recipient')
        bot = self.keysDB.getBotName(botWebName)
        log.debug("webName= {}, bot= {}".format(botWebName, bot))
        if bot:
            r=self.mqtt.publish(bot+'/command', str(command))
            log.debug("response: '{}'".format(r))
        else:
            log.error("BotWebName '{}' not found".format(botWebName))

    def sendMessage(self, message, sender, recipientId):
        bot = self.keysDB.getBotName(sender)
        log.debug("sending message: {} {} {} {}".format(bot, sender, recipientId, message))
        self.api.sendMessage(messageText=message, recipientId=recipientId, **self.bots[bot].credentials)

    def sendEvent(self, sender, message):
        for admin, adminId in self.bots[sender].admins.items():
            log.debug("sending message: {} {} {} {}".format(sender, message, admin, adminId))
            self.api.sendMessage(messageText=message, recipientId=adminId, **self.bots[sender].credentials)

    def updateDB(self, webName, credentials):
        for bot in self.bots:
            if self.bots[bot].webName == webName:
                self.keysDB.storeConfig(bot, webName, credentials)
                return('Successfully updated config')
        return('device not config for botCOntroller, See system administrator')

class Bot(object):
    def __init__(self, name, config, db):
        self.name = name
        self.webName = config.get('webName')
        self.db = db
        self.__getConfig()
        self.config = config
        self.admins = config.get('admins')
        self.users = config.get('users')

    def __getConfig(self):
        self.credentials = self.db.getBotConfig(name=self.name)
        

class BotException(Exception):
    def __init__(self, message, error):
        super().__init__(message)
        self.error = error
        