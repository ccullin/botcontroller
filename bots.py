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
        self.api = webAPI(self.config)

    def run(self):
        self.api.registerController()
        for bot, config in self.config.get('bots').items():
            self.bots[bot] = Bot(bot, config)
            r = self.api.subscribeBot(**self.bots[bot].credentials)
            log.debug("subscrition response code = '{}".format(r))
            log.debug("subscribe {}/event".format(bot))
            log.debug("subscribe {}/response".format(bot))
            self.mqtt.subscribe(bot+'/event')
            self.mqtt.subscribe(bot+'/response')

    def newCommand(self, command):
        log.debug('command = {}'.format(command))
        botWebName = command.get('recipient')
        # if self.keysDB.isBot(botname = bot):
        bot = self.keysDB.getBotName(botWebName)
        if bot:
            log.debug('publish: {}/command msg: {}'.format(bot, str(command)))
            r=self.mqtt.publish(bot+'/command', str(command))
            log.debug("response: '{}'".format(r))
        else:
            log.error("BotWebName '{}' not found".format(botWebName))
            log.debug("dump of self.bots: {}".format(self.bots))

    def sendMessage(self, message, sender, recipientId):
        log.debug("sending '{}', to '{}' from '{}'".format(message, recipientId, sender))
        log.debug("keys {}".format(self.bots[sender].credentials))
        self.api.sendMessage(messageText=message, recipientId=recipientId, **self.bots[sender].credentials)

    def sendEvent(self, message, sender, recipientId):
        log.debug("sending '{}', to '{}' from '{}'".format(message, recipientId, sender))
        for admin, adminId in self.bots[sender].admins.items():
            self.api.sendMessage(messageText=message, recipientId=adminId, **self.bots[sender].credentials)

    def updateDB(self, webName, credentials):
        for bot in self.bots:
            if bot.webName == webName:
                self.keysDB.storeConfig(bot, webName, credentials)
                return('Successfully updated config')
        return('device not config for botCOntroller, See system administrator')

class Bot(object):
    def __init__(self, name, config):
        self.name = name
        self.webName = config.get('webName')
        self.__getConfig()
        self.config = config
        self.admins = config.get('admins')
        self.users = config.get('users')

    def __getConfig(self):
        db = Mongodb()
        self.credentials = db.getBotConfig(name=self.name)
        log.debug(self.name)
        log.debug(self.credentials)
        db.close()


class BotException(Exception):
    def __init__(self, message, error):
        super().__init__(message)
        self.error = error
        