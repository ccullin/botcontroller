from pymongo import MongoClient
import logging

log = logging.getLogger(__name__)


class Mongodb():

    def __init__(self, host='192.168.0.15', port=27017,
                 db='twitter_oauth', collection='bots'):
        self.client = MongoClient(host, port)
        self.safe = self.client[db][collection]
        
    
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
    
    def getBotConfig(self, **kwargs):
        name = kwargs.get('name', None)
        webName = kwargs.get('webName', None)
        if name != None:
            bot = self.safe.find_one({'name': name})
            return bot['config']
        else:
            bot = self.safe.find_one({'webName': webName})
            return bot['config']

    def getWebhookId(self):
        botcontroller = self.safe.find_one({'name':'botcontroller'})
        if botcontroller:
            return botcontroller['config']['webhook_id']
        return None
 
    def storeWebhookId(self, webhook_id):
        self.safe.update_one({'name': 'botcontroller'}, {'$set': {'config': {'webhook_id':webhook_id}}},upsert=True)
 
        
    def close(self):
        self.client.close()
        