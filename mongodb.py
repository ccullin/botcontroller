from pymongo import MongoClient
import logging

log = logging.getLogger(__name__)


class Mongodb():

    def __init__(self, host='192.168.0.15', port=27017,
                 db='twitter_oauth', collection='bots'):
        self.client = MongoClient(host, port)
        self.safe = self.client[db][collection]


    # def getAllKeys(self):
    #     keys = self.safe.find({ 'name': { '$exists': True }})
    #     if keys:
    #         return keys
    #     return None
    
    
    # def getKeys(self, name):
    #     # name = kwargs.get('name', None)
    #     # screen_name = kwargs.get('screen_name',None)
    #     # if name != None:
    #     return(self.safe.find_one({ 'name': name }))
    #     # else:
    #     #     return(self.safe.find_one({'screen_name': screen_name}))

    # def isBot(self, **kwargs):
    #     botId = kwargs.get('botId', None)
    #     botname = kwargs.get('botname',None)
    #     if botId != None:
    #         return(self.safe.find_one({ 'uid': botId }))
    #     else:
    #         return(self.safe.find_one({'name': botname}))
 
    
    def storeConfig(self, name, webName, config):
        log.debug('update database {} {}, Config: {}'.format(name, webName, config))
        self.safe.update_one({'name': name}, {'$set': {'webName': webName, 'config': config}},upsert=True)
        # self.safe.update_one({'webName': session['name']}, {'$set': 
        #                         {'uid': session['uid'],
        #                         'webName': session['name'],
        #                         'ACCESS_KEY': session['ACCESS_KEY'],
        #                         'ACCESS_SECRET': session['ACCESS_SECRET']
        #                         }},
        #                     upsert=True)

    def getBotName(self, webName):
        bot = self.safe.find_one({'webName': webName})
        if bot:
            return bot['name']
        return None


    # def deleteKey(self, name):
    #     self.safe.delete({'name': name})

    
    def getBotConfig(self, **kwargs):
        name = kwargs.get('name', None)
        webName = kwargs.get('webName', None)
        if name != None:
            bot = self.safe.find_one({'name': name})
            return bot['config']
        else:
            bot = self.safe.find_one({'webName': webName})
            return bot['config']
        
        
    def close(self):
        self.client.close()
        