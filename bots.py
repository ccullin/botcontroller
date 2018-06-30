import requests
import Twitter
import logging
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console = logging.StreamHandler()
log.addHandler(console)



class BotController(object):
    def __init__(self, config, keysDB):
        self.bots = {}
        self.config = config
        self.keysDB = keysDB
        
    def run(self):
        for key, value in self.config.items():
            self.bots[value.get('screen_name')] = Bot(value, self.keysDB)
            self.registerBot(value.get('screen_name'))
    
            
    def newCommand(self, command):
        log.debug('command = {}'.format(command))
        bot = command.get('recipient')
        if bot in self.bots:
            self.bots[bot].sendCommand(command)
        else:
            log.error("Bot '{}' not found".format(bot))
            log.debug("dump of self.bots: {}".format(self.bots))
    
            
    def registerBot(self, name):
        log.debug(name)
        if self.bots[name].access_key != None:
            self.bots[name].webhook_subscribe()
    
    # def sendDirectMessage(self, msg, sendto):
    #     if bot in self.bots:
    #         self.bots[name].sendDirectMessage(msg)
    #     else:
    #         log.error("Bot '{}' not found".format(bot))
    #         log.debug("dump of self.bots: {}".format(self.bots))
            

    

class Bot(object):
    def __init__(self, config, keysDB):
        self.name = config.get('screen_name')
        self.url = config.get("webhook")
        self.db = keysDB
        self.access_key = None
        self.access_secret = None
        self.__getKeys()


    def webhook_subscribe(self):
        r = Twitter.webhook_subscribe(self.access_key, self.access_secret)
        if r == 348:
            log.warning("Webhook access to {} not permitted".format(self.name))
            log.warning("Go to /login to authorize this app to access bot account")
        return r
    
            
    def __getKeys(self):
        keys = self.db.getKeys(self.name)
        if keys != None:
            self.access_key = keys.get('oauth_token')
            self.access_secret = keys.get('oauth_token_secret')
            self.webhook_subscribe()
            return
        log.error("error retrieving keys.  Check webhook has subscribed to user {}".format(self.name))
    
    
    def sendCommand(self, command):
        log.debug("sending url: {} command: {}".format(self.url, command))
        #r = requests.put(self.url, data = command)
        r = requests.get('https://api.github.com/events')

        if r.status_code != 200:
            log.info("Error processing command.  errorno: {}, {}".format(r.status_code, r.text))
            self.sendDirectMessage("Error processing command.  errorno: {}, {}".format(r.status_code, r.text), 
                                    command.get('senderId'))
        else:
            self.sendDirectMessage("Command successful", command.get('senderId'))
        
        
    def sendDirectMessage(self, msg, recipientId):
        log.debug("sending user: {} response".format(recipientId))
        r = Twitter.sendDirectMessage(msg, recipientId, self.access_key, self.access_secret)
        
        if r != 200:
            log.error("ERROR: ", r)
