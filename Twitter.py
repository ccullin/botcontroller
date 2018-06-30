from TwitterAPI import TwitterAPI

import os
import logging
from http import HTTPStatus
import json

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(threadName)s - %(module)s - %(lineno)d:  %(message)s')
console.setFormatter(formatter)
log.addHandler(console)


#replace these with a database query
CONSUMER_KEY = os.environ.get('CONSUMER_KEY', None)
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET', None)
ENVNAME = os.environ.get('ENVNAME', None)
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', None)


def run_async(func):
    """
        run_async(func)
            function decorator, intended to make "func" run in a separate thread (asynchronously).
            Returns the created Thread object

            E.g.:
            @run_async
            def task1():
                do_something
    """
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        print("starting function {} as a thread".format(func))
        func_hl = Thread(target = func, args = args, kwargs = kwargs, daemon=True)
        func_hl.start()
        return func_hl
    return async_func
    

 
#@run_async
def sendDirectMessage(messageText, userID, ACCESS_KEY, ACCESS_SECRET):
    """
        Access tokens define which Bot is sending the messsage.  the recipient will be the Twitter user
        that sent a command to a bot, or the admins for event notification.
    """
        
    log.debug("send msg: {} to user: {}".format(messageText, userID))
    # ACCESS_KEY = os.environ.get('ACCESS_KEY')
    # ACCESS_SECRET = os.environ.get('ACCESS_SECRET')
    log.debug("tokens: {}, {}".format(ACCESS_KEY, ACCESS_SECRET))
    twitterAPI = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)


    #messageJson = '{"event": {"type": "message_create", "message_create": {"target": {"recipient_id": "chris_cullin"}, "message_data": {"text": "' + messageText + '"}}}}'
    messageJson = '{"event": {"type": "message_create", "message_create": {"target": {"recipient_id": "' + userID + '"}, "message_data": {"text": "' + messageText + '"}}}}'
    #           = '{"event": {"type": "message_create", "message_create": {"target": {"recipient_id": "' + userID + '"}, "message_data": {"text":"Hello World!"}}}}'
    

    r = twitterAPI.request('direct_messages/events/new', messageJson)
    log.debug("response code: {}".format(r.status_code))
    return r.status_code      



#@run_async
def create_webhook(ACCESS_KEY, ACCESS_SECRET):
    """
        initiates the OAUTH 1.0 dance with twitter.  Twitter will POST a
        CRC Token confirmation request which this server needs to respond to.
        Hence the request is run asynchronously
    """

    log.debug("create webhook request")
    twitterAPI = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    log.debug("webhook create url: " + 'account_activity/all/:%s/webhooks' % ENVNAME + '\nurl:' + WEBHOOK_URL)
    r = twitterAPI.request('account_activity/all/:%s/webhooks' % ENVNAME, {'url': WEBHOOK_URL}, None, "POST")
    
    # log.debug ("webhook create response code = {}".format(r.status_code))
    # message = json.loads(r.text)
    # log.debug ("webhook create response text = {}".format(message))
    # log.debug(type(message))
    # log.debug("attempt to get message: {}".format(message.get("errors")))
    # message2 = message.get("errors")
    # log.debug("attempt to get message2: {}".format(message2[0].get("message")))
    # log.debug("attempt to get message3: {}".format(message.get('errors')[0].get('message')))
    
    text = json.loads(r.text)
    message = text.get('errors')[0].get('message')
    #log.debug ("webhook create response = ", r)
    
    if r.status_code == 200:
        return r.status_code

    if message == "Too many resources already created.":
        log.debug("message is: {}".format(message))
        return 200
    else:
        log.error("unepexpected return code: {}".format(r.status_code))
        log.error("response: {}".format(r.text))
        return r.status_code



def webhook_subscribe(ACCESS_KEY, ACCESS_SECRET):
    twitterAPI = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)

    r = twitterAPI.request('account_activity/all/:%s/subscriptions' % ENVNAME
                            , None, None, "POST")

    #TODO: check possible status codes and convert to nice messages
    log.debug (r.status_code)
    return r.status_code