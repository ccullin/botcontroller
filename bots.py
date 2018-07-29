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
        self.keysDB = Mongodb()
        self.bots = {}
        self.config = config.get('webAPI')
        self.mqtt = MQTT('192.168.0.4', name="botcontroller", botController=self)
        self.api = webAPI(self.config, self.keysDB)

    def run(self):
        self.api.registerController()
        for bot, config in self.config.get('bots').items():
            self.bots[bot] = Bot(config)
            r = self.api.subscribeBot(**self.bots[bot].keys)
            log.debug("sucsription repose code = '{}".format(r))
            self.mqtt.subscribe(self.bots[bot].name+'/event')
            self.mqtt.subscribe(self.bots[bot].name+'/response')

    def newCommand(self, command):
        log.debug('command = {}'.format(command))
        bot = command.get('recipient')
        # if self.keysDB.isBot(botname = bot):
        if bot in self.bots:
            log.debug('bot name: {}'.format(bot))
            r=self.mqtt.publish(self.bots[bot].name+'/command', str(command))
            log.debug("response: '{}'".format(r))
        else:
            log.error("Bot '{}' not found".format(bot))
            log.debug("dump of self.bots: {}".format(self.bots))

    def sendMessage(self, message, sender, recipientId):
        log.debug("sending '{}', to '{}' from '{}'".format(message, recipientId, sender))
        log.debug("keys {}".format(self.bots[sender].keys))
        self.api.sendMessage(messageText=message, recipientId=recipientId, **self.bots[sender].keys)

    def sendEvent(self, message, sender, recipientId):
        log.debug("sending '{}', to '{}' from '{}'".format(message, recipientId, sender))
        for admin, adminId in self.bots[sender].admins.items():
            self.api.sendMessage(messageText=message, recipientId=adminId, **self.bots[sender].keys)


class Bot(object):
    def __init__(self, config):
        self.name = config.get('name')
        self.__getKeys()
        try:
            self.config = config
            self.admins = config.get('admins')
            self.users = config.get('users')
        except:
            log.warning("error retrieving keys.  Check webhook has subscribed to user {}".format(self.name))
            raise BotException("Bot not authorised", None)

    def __getKeys(self):
        db = Mongodb()
        self.keys = db.getKeys(name=self.name)
        log.debug(self.name)
        log.debug(self.keys)
        db.close()


class BotException(Exception):
    def __init__(self, message, error):
        super().__init__(message)
        self.error = error
        