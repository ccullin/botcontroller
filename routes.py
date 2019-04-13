# #!/usr/bin/wnv python3
from flask import Flask, request, url_for, jsonify
from flask_oauth import OAuth
from http import HTTPStatus
import hashlib, hmac, base64, json
from time import sleep
import logging

#local imports
import Twitter
from config import config

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

app = Flask(__name__)

# app.logger.setLevel(logging.INFO)
log.info("run app")


#user login requirements
oauth = OAuth()

# Get the Consumer tokens for this application.
api_tokens = config.get('webAPI').get('api_tokens')

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
    log.debug('oauth authorised response= {}'.format(resp))

    if resp is None:
        return(u'You denied the request to sign in.')

    webName = resp['screen_name']
    oauth_keys = {
        'uid': resp['user_id'],
        'ACCESS_KEY': resp['oauth_token'],
        'ACCESS_SECRET': resp['oauth_token_secret']
    }
    
    # Save keys to DB.
    # keys = Mongodb()
    # keys.storeConfig(webName, oauth_keys)
    # keys.close()
    r = app.config['botController'].updateDB(webName, oauth_keys)
    return (r) 


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
  

# This is the Webhook Twitter posts events to for subscribed accounts.
@app.route("/webhook/twitter", methods=["POST"])
def twitterEventReceived():
    log.debug("POST request")	
    requestJson = request.get_json()

    # Ignore evenerything that is not a direct message.
    if 'direct_message_events' not in requestJson.keys():
        # Event type not supported so just ignore
        log.debug("Twitter message is not a Direct Message: Ignoring")
        return ('', HTTPStatus.OK)
        
    # Ignore if not a new message.
    eventType = requestJson['direct_message_events'][0].get("type")
    if eventType != 'message_create':
        log.debug("Twitter message is not a Message Create event:  Ignoring")
        return ('', HTTPStatus.OK)
    
    messageObject = requestJson['direct_message_events'][0].get('message_create', {})
    messageText =   messageObject.get('message_data').get('text')
    senderId =      messageObject.get('sender_id')
    recipientId =   messageObject.get('target').get('recipient_id')

    users =         requestJson.get('users')
    sender =        users.get(senderId).get('screen_name')
    recipient =     users.get(recipientId).get('screen_name')
    command = {"command": messageText, "sender": sender, "senderId": senderId, "recipient": recipient}

    try:
        log.debug("Twitter new command received.  Sending to botcontroller")
        log.debug("new Command is '{}'",command)
        app.config['botController'].newCommand(command)
        r = ('', HTTPStatus.OK)
    except Exception as e:
        log.error("Error sending command: {}".format(e))
        app.config['botController'].sendDirectMessage(msg="Error sending command:  Bot not Found", sender=recipient, recipientId=senderId)
        r = ('Error sending command', HTTPStatus.NOT_FOUND)
    return (r)
