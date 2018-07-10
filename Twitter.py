from TwitterAPI import TwitterAPI
from http import HTTPStatus
import json
import logging

#local imports

log = logging.getLogger(__name__)


def sendDirectMessage(messageText, userID, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET):
    log.debug("send msg: {} to user: {}".format(messageText, userID))
    twitterAPI = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    message = {
        "event": {
            "type": "message_create", 
            "message_create": {
                "target": {
                    "recipient_id": userID
                }, 
                "message_data": {
                    "text": messageText
                }
            }
        }
    }
    
    log.debug("message text:")
    log.debug(json.dumps(message))
    r = twitterAPI.request('direct_messages/events/new', json.dumps(message))
    log.debug("response code: {}".format(r.status_code))

    return r.status_code      


def create_webhook(WEBHOOK_URL, ENVNAME, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET):
    """
        initiates the OAUTH 1.0 dance with twitter.  Twitter will POST a
        CRC Token confirmation request which this server needs to respond to.
        Hence the request is run asynchronously
    """

    log.debug("create webhook request")
    twitterAPI = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    r = twitterAPI.request('account_activity/all/:%s/webhooks' % ENVNAME, {'url': WEBHOOK_URL}, None, "POST")
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



def webhook_subscribe(WEBHOOK_URL, ENVNAME, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET):
    twitterAPI = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    r = twitterAPI.request('account_activity/all/:%s/subscriptions' % ENVNAME, None, None, "POST")
    log.debug (r.status_code)
    return r.status_code