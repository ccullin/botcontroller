from pymongo import MongoClient
import logging

log = logging.getLogger(__name__)


class Mongodb():

    def __init__(self, host='192.168.0.15', port=27017,
                 db='twitter_oauth', collection='keys'):
        self.client = MongoClient(host, port)
        self.safe = self.client[db][collection]


    def getAllKeys(self):
        keys = self.safe.find({ 'name': { '$exists': True }})
        if keys:
            return keys
        return None
    
    
    def getKeys(self, screen_name):
        return(self.safe.find_one({ 'name': screen_name }))


    def isBot(self, userID):
        return(self.safe.find_one({ 'uid': userID }))
 

    
    def storeKey(self, session):
        print('session on database side ', session)
        self.safe.update_one({'name': session['screen_name']}, {'$set': 
                                {'uid': session['uid'],
                                'name': session['screen_name'],
                                'oauth_token': session['oauth_token'],
                                'oauth_token_secret': session['oauth_token_secret']
                                }},
                            upsert=True)


    def deleteKey(self, screen_name):
        self.safe.delete({'name': screen_name})
        return

    
    def getBotConfig(self, botName):
        bot = self.safe.find_one({'name': botName})
        if Bot:
            return Bot['data']
        return None

        
    def close(self):
        self.client.close()
        