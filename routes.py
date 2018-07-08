# #!/usr/bin/wnv python3
from flask import Flask, request, url_for, jsonify
from flask_oauth import OAuth
from http import HTTPStatus
import hashlib, hmac, base64, json
from time import sleep
import logging

#local imports
import Twitter
from mongodb import Mongodb
from config import config

log = logging.getLogger(__name__)

log.debug("run app")
app = Flask(__name__)



#user login requirements
oauth = OAuth()

# Get the Consumer tokens for this application.
api_tokens = config.get('controller').get('api_tokens')

twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url= 'https://api.twitter.com/oauth/access_token',
    authorize_url=    'https://api.twitter.com/oauth/authorize',
    consumer_key=api_tokens.get('CONSUMER_KEY'),
    consumer_secret=api_tokens.get('CONSUMER_SECRET')
)


#generic index route    
@app.route('/webhook')
def default_route():        
    #return send_from_directory('www', 'index.html') 
    return "you are on the webhook base URL"


@app.route('/webhook/twitter/login')
def twitter_login():
    """
        not called from anywhere.  Users access this webpage to register
        and allow the webhook bot account access.  For example the tradebot
        needs to grant permission to Webhook bot to send and receive tweets
    """

    try:
        return twitter.authorize(callback=url_for('oauth_authorized',
            next=request.args.get('next') or request.referrer or None))
    except Exception as e:
        log.exception(e)
        log.debug("url callback = {}".format(url_for('oauth_authorized')))
        return("url callback = {}".format(url_for('oauth_authorized')))





@app.route('/webhook/twitter/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    """
        Callback function.  Called by Twitter after user logs in
    """
    log.debug('in oauth_authorized after callback')

    if resp is None:
        return(u'You denied the request to sign in.')

    log.debug('response= {}'.format(resp))
    oauth_keys = {
        'uid': resp['user_id'],
        'screen_name': resp['screen_name'],
        'oauth_token': resp['oauth_token'],
        'oauth_token_secret': resp['oauth_token_secret']
    }
    
    # Save keys to DB.
    keys = Mongdb()
    keys.storeKey(oauth_keys)
    keys.close()
    return ("all done") 


@twitter.tokengetter
def get_twitter_token():
      return None


@app.route("/webhook/twitter", methods=["GET"])
def webhook_challenge():
    """
       The GET method for webhook should be used for the CRC check.
       Called by Twitter as part of the webhook registration exchange.
    """
    log.debug("in web_challenge")
    validation = hmac.new(
    	key=bytes(api_tokens.get('CONSUMER_SECRET'), 'utf-8'),
    	msg=bytes(request.args.get('crc_token'), 'utf-8'),
    	digestmod=hashlib.sha256
    )
    digested = base64.b64encode(validation.digest())
    response = {'response_token': 'sha256=' + format(str(digested)[2:-1])}
    log.debug('responding to CRC call')
    return json.dumps(response)   
  

# Thsi is the Webhook Twitters posts and subscribed events to.
@app.route("/webhook/twitter", methods=["POST"])
def twitterEventReceived():
    log.debug("POST request")	
    requestJson = request.get_json()

    # Ignore evenerything that is not a direct message.
    if 'direct_message_events' in requestJson.keys():
        eventType = requestJson['direct_message_events'][0].get("type")
        messageObject = requestJson['direct_message_events'][0].get('message_create', {})
        senderId = messageObject.get('sender_id')
        recipientId = messageObject.get('target').get('recipient_id')
        
        # If event type isnt new message then ignore.
        if eventType != 'message_create':
            return ('', HTTPStatus.OK)
        
        messageText = messageObject.get('message_data').get('text')
        users = requestJson.get('users')
        sender = users.get(senderId).get('screen_name')
        recipient = users.get(recipientId).get('screen_name')
        
        log.debug("sender name: {}, id: {}".format(sender, senderId))
        log.debug("recipient name: {}, id: {}".format(recipient, recipientId))
        
        keys = Mongodb()
        # Check if message sent to one of the configured and registers bots.
        if keys.isBot(recipientId):
            command = {"command": messageText, "sender": sender, "senderId": senderId, "recipient": recipient}      
            r = app.config['botController'].newCommand(command)
        else:
            r = HTTPStatus.NOT_FOUND
        keys.close()
        return ('', r)
    else:
        # Event type not supported so just ignore
        return ('', HTTPStatus.OK)


# Webhook to receive events from alarm
@app.route("/webhook/alarm", methods=["POST"])
def alarmEventReceived():
    log.debug("POST request")	
    requestJson = request.get_json()
    msg = requestJson.get('message')
    sender = requestJson.get('sender')
    recipientId = requestJson.get('recipientId')
    log.debug("request: {}".format(requestJson))
    
    # Forward venet to botController so it can send out as the bot.
    app.config['botController'].sendDirectMessage(msg, sender, recipientId)
    return ('', HTTPStatus.OK)


