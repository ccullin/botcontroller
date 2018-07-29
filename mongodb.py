from pymongo import MongoClient
import logging

log = logging.getLogger(__name__)


class Mongodb():

    def __init__(self, host='192.168.0.15', port=27017,
                 db='twitter_oauth', collection='bots'):
        self.client = MongoClient(host, port)
        self.safe = self.client[db][collection]


    def getAllKeys(self):
        keys = self.safe.find({ 'name': { '$exists': True }})
        if keys:
            return keys
        return None
    
    
    def getKeys(self, name):
        # name = kwargs.get('name', None)
        # screen_name = kwargs.get('screen_name',None)
        # if name != None:
        return(self.safe.find_one({ 'name': name }))
        # else:
        #     return(self.safe.find_one({'screen_name': screen_name}))

    # def isBot(self, **kwargs):
    #     botId = kwargs.get('botId', None)
    #     botname = kwargs.get('botname',None)
    #     if botId != None:
    #         return(self.safe.find_one({ 'uid': botId }))
    #     else:
    #         return(self.safe.find_one({'name': botname}))
 
    
    def storeKey(self, session):
        print('session on database side ', session)
        self.safe.update_one({'screen_name': session['screen_name']}, {'$set': 
                                {'uid': session['uid'],
                                'name': session['name'],
                                'ACCESS_KEY': session['ACCESS_KEY'],
                                'ACCESS_SECRET': session['ACCESS_SECRET']
                                }},
                            upsert=True)

    # def addName(self, name, screen_name):
    #     self.safe.update_one({'screen_name': screen_name}, {'$set': {'name': name}}, upsert=True)



    def deleteKey(self, name):
        self.safe.delete({'name': name})

    
    def getBotConfig(self, name):
        bot = self.safe.find_one({'name': name})
        if bot:
            return bot['data']
        return None

        
    def close(self):
        self.client.close()
        