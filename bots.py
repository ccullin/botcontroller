import requests
from http import HTTPStatus
import logging

#local imports
import Twitter
from mongodb import Mongodb

log = logging.getLogger(__name__)


class BotController(object):
    def __init__(self, config):
        self.bots = {}
        self.keysDB = Mongodb()
        self.__load_config(config)

        
    def __load_config(self, config):
        self.bot_config =   config.get('bots')
        self.api_tokens =   config.get('controller').get('api_tokens')
        self.access_tokens = config.get('controller').get('access_tokens')
        self.webhook =      config.get('controller').get('webhook')

    
    def __create_webhook(self):
        r = Twitter.create_webhook(**self.webhook, **self.api_tokens, **self.access_tokens)
        if r != HTTPStatus.OK:
            log.error("webhook registration failed.  Error: {}".format(r))
            exit()
        return r

        
    def run(self):
        self.__create_webhook()
        for bot, config in self.bot_config.items():
            self.bots[config.get('screen_name')] = Bot(config, self.keysDB)
            if self.bots[config.get('screen_name')].access_tokens != {}:
                log.debug("before call")
                log.debug(self.bots[config.get('screen_name')].access_tokens)
                self.registerBot(config.get('screen_name'))
    
            
    def newCommand(self, command):
        log.debug('command = {}'.format(command))
        bot = command.get('recipient')
        if bot in self.bots:
            r = self.bots[bot].sendCommand(command)
        else:
            log.error("Bot '{}' not found".format(bot))
            log.debug("dump of self.bots: {}".format(self.bots))
            r = ('', HTTPStatus.NOT_FOUND)
        return (r)
    
            
    def registerBot(self, name):
        if self.bots[name].access_tokens != None:
            # self.bots[name].webhook_subscribe()
            r = Twitter.webhook_subscribe(**self.webhook, **self.api_tokens, **self.bots[name].access_tokens)
            if r == 348:
                log.warning("Webhook access to {} not permitted".format(self.name))
                log.warning("Go to /login to authorize this app to access bot account")
            return r

    
    def sendDirectMessage(self, msg, sender, recipientId):
        if self.bots[sender].access_tokens != None:
            log.debug("sending '{}', to '{}' from '{}'".format(msg, recipientId, sender))
            if recipientId == "admins":
                for admin, adminId in self.bots[sender].admins.items():
                    r = Twitter.sendDirectMessage(msg, adminId, **self.api_tokens, **self.bots[sender].access_tokens)
            else:
                Twitter.sendDirectMessage(msg, recipientId, **self.api_tokens, **self.bots[sender].access_tokens)
            return ('', HTTPStatus.OK)
        return ('Invalid bot config.', HTTPStatus.INTERNAL_SERVER_ERROR)



class Bot(object):
    def __init__(self, config, keysDB):
        self.name = config.get('screen_name')
        self.url = config.get("webhook")
        self.db = keysDB
        self.admins = config.get("admins")
        self.access_tokens = {}
        self.__getKeys()


    def __getKeys(self):
        keys = self.db.getKeys(self.name)
        if keys != None:
            access_key = keys.get('oauth_token')
            access_secret = keys.get('oauth_token_secret')
            self.access_tokens = {"ACCESS_KEY": access_key, "ACCESS_SECRET": access_secret}
            return
        log.warning("error retrieving keys.  Check webhook has subscribed to user {}".format(self.name))
    
    
    def sendCommand(self, command):
        log.debug("sending url: {} command: {}".format(self.url, command))
        r = requests.post(self.url, json=command)
        log.debug("request url is: {}".format(r.url))
        log.debug("response is: {}".format(r.text))
        if r.status_code != 200:
            log.info("Error processing command.  errorno: {}, {}".format(r.status_code, r.text))
        return (r.text, r.status_code)
