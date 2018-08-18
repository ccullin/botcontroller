from TwitterAPI import TwitterAPI
from http import HTTPStatus
import json
import logging

#local imports
from webAPI import webAPI_abstract

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class webAPI(webAPI_abstract):
    def __init__(self, config):
        super().__init__()
        self.bots =          config.get('bots')
        self.CONSUMER_KEY =  config.get('api_tokens').get('CONSUMER_KEY')
        self.CONSUMER_SECRET = config.get('api_tokens').get('CONSUMER_SECRET')
        self.ACCESS_KEY =    config.get('access_tokens').get('ACCESS_KEY')
        self.ACCESS_SECRET = config.get('access_tokens').get('ACCESS_SECRET')
        self.access_tokens = config.get('access_tokens')
        self.webhook_url =   config.get('webhook').get('WEBHOOK_URL')
        self.envname =       config.get('webhook').get('ENVNAME')


    def registerController(self):
        """
            initiates the OAUTH 1.0 dance with twitter.  Twitter will POST a
            CRC Token confirmation request which this server needs to respond to.
            Hence the request is run asynchronously
        """
    
        log.debug("create webhook request")
        twitterAPI = TwitterAPI(self.CONSUMER_KEY, self.CONSUMER_SECRET, self.ACCESS_KEY, self.ACCESS_SECRET)
        r = twitterAPI.request('account_activity/all/:%s/webhooks' % self.envname, {'url': self.webhook_url}, None, "POST")
        text = json.loads(r.text)
        message = text.get('errors')[0].get('message')
    
        if r.status_code == HTTPStatus.OK:
            return r.status_code
        elif message == "Too many resources already created.":
            log.debug("message is: {}".format(message))
            return HTTPStatus.OK
        else:
            log.error("unepexpected return code: {}".format(r.status_code))
            log.error("response: {}".format(r.text))
            return r.status_code
        
    def subscribeBot(self, **kwargs):
        twitterAPI = TwitterAPI(self.CONSUMER_KEY, self.CONSUMER_SECRET, kwargs['ACCESS_KEY'], kwargs['ACCESS_SECRET'])
        r = twitterAPI.request('account_activity/all/:%s/subscriptions' % self.envname, None, None, "POST")
        log.debug (r.status_code)
        if r == 348:
            # todo.  sent a notification event.
            log.warning("Webhook access to {} not permitted".format(self.name))
            log.warning("Go to /login to authorize this app to access bot account")
        return r.status_code

    def sendMessage(self, messageText, **kwargs):
        recipientId = kwargs['recipientId']
        log.debug("send msg: '{}' to user: '{}'".format(messageText, recipientId))
        ACCESS_KEY = kwargs.get('ACCESS_KEY', self.ACCESS_KEY)
        ACCESS_SECRET = kwargs.get('ACCESS_SECRET', self.ACCESS_SECRET)
        twitterAPI = TwitterAPI(self.CONSUMER_KEY, self.CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
        
        for i in range(0, len(messageText), 149):
            msgChunk = messageText[i:i+149]
            message = {
                "event": {
                    "type": "message_create", 
                    "message_create": {
                        "target": {
                            "recipient_id": recipientId
                        }, 
                        "message_data": {
                            "text": msgChunk
                        }
                    }
                }
            }
            
            log.debug("message text:")
            log.debug(json.dumps(message))
            r = twitterAPI.request('direct_messages/events/new', json.dumps(message))
            log.debug("response code: {}".format(r.status_code))
            log.debug("response: {}".format(r))
    
        return HTTPStatus.OK     
    