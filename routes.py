#!/usr/bin/wnv python3
from flask import Flask, request, send_from_directory, make_response, Blueprint, \
redirect, url_for, g, flash, render_template, jsonify
from http import HTTPStatus
from flask_oauth import OAuth
import hashlib, hmac, base64, os, logging, json
import Twitter
import ssl
# from TwitterAPI import TwitterAPI
from time import sleep
from mongodb import Mongodb

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(threadName)s - %(module)s - %(lineno)d:  %(message)s')
console.setFormatter(formatter)
log.addHandler(console)


CONSUMER_KEY = os.getenv('CONSUMER_KEY', None)
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET', None)

# ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', None)
# ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET', None)

#The environment name for the beta is filled below. Will need changing in future		
ENVNAME = os.getenv('ENVNAME', None)
WEBHOOK_URL = os.getenv('WEBHOOK_URL', None)


#CURRENT_USER_ID = os.getenv('CURRENT_USER_ID', None)

log.debug("run app")
app = Flask(__name__)


#user login requirements
oauth = OAuth()

# Use Twitter as example remote application
twitter = oauth.remote_app('twitter',
    # unless absolute urls are used to make requests, this will be added
    # before all URLs.  This is also true for request_token_url and others.
    base_url='https://api.twitter.com/1.1/',
    #base_url='https://www.miplace.com',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url= 'https://api.twitter.com/oauth/access_token',
    authorize_url=    'https://api.twitter.com/oauth/authorize',
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
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
    # next_url = request.args.get('next') or url_for('index')
    # log.debug("requests.get: {}, index: {}, mext_url: {}".format(
    #     requests.args.get('next'),
    #     url_for('index'),
    #     next_url))
        
    if resp is None:
        return(u'You denied the request to sign in.')
        #return redirect(next_url)
 
    print('response= {}'.format(resp))
    oauth_keys = {
        'uid': resp['user_id'],
        'screen_name': resp['screen_name'],
        'oauth_token': resp['oauth_token'],
        'oauth_token_secret': resp['oauth_token_secret']
    }
    
    #keys = app.config['keys']
    keys = Mongdb()
    keys.storeKey(oauth_keys)
    # app.config['keys'].store(oauth_keys)
    # app.config['botContoller'].webhook_subscribe(screen_name)
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
    #log.debug("request = ", request)
    log.debug("crc token= ", request.args.get('crc_token'))
    log.debug("Consumer_SECRET= ", CONSUMER_SECRET)
    

    validation = hmac.new(
	key=bytes(CONSUMER_SECRET, 'utf-8'),
	msg=bytes(request.args.get('crc_token'), 'utf-8'),
	digestmod=hashlib.sha256
    )

    digested = base64.b64encode(validation.digest())

    response = {
        'response_token': 'sha256=' + format(str(digested)[2:-1])
    }
    log.debug('responding to CRC call')

    return json.dumps(response)   
  
  
        
#The POST method for webhook should be used for all other API events
@app.route("/webhook/twitter", methods=["POST"])
def twitterEventReceived():
    
    # def processEvent(app, command):
    #     app.config['botController'].newCommand(command)
        
    
    log.debug("POST request")	
    print("POST request")
    requestJson = request.get_json()

    # Ignore evenerything that i snot a direct message.
    if 'direct_message_events' in requestJson.keys():
        #dump to console for debugging purposes
        # print("dump of request json")
        # print(json.dumps(requestJson, indent=4, sort_keys=True))
                          
        #DM recieved, process that
        eventType = requestJson['direct_message_events'][0].get("type")
        messageObject = requestJson['direct_message_events'][0].get('message_create', {})
        senderId = messageObject.get('sender_id')
        recipientId = messageObject.get('target').get('recipient_id')
        
        #event type isnt new message so ignore
        if eventType != 'message_create':
            return ('', HTTPStatus.OK)
        
        messageText = messageObject.get('message_data').get('text')
        
        users = requestJson.get('users')
        sender = users.get(senderId).get('screen_name')
        recipient = users.get(recipientId).get('screen_name')
        
        log.debug("sender name: {}, id: {}".format(sender, senderId))
        log.debug("recipient name: {}, id: {}".format(recipient, recipientId))
        
        #keys = app.config['keys']
        keys = Mongodb()
        if keys.isBot(recipientId):
            command = {"command": messageText, "sender": sender, "senderId": senderId, "recipient": recipient}      
            r = app.config['botController'].newCommand(command)
            #thread.start_new_thread(processEvent, (app, command))
        else:
            r = HTTPStatus.NOT_FOUND
        keys.close()
        return ('', r)

    else:
        #Event type not supported
        return ('', HTTPStatus.OK)
    
    return ('', HTTPStatus.OK)



        
#Notification from alarm
@app.route("/webhook/alarm", methods=["POST"])
def alarmEventReceived():
    log.debug("POST request")	
    requestJson = request.get_json()
    msg = requestJson.get('message')
    sender = requestJson.get('sender')
    recipientId = requestJson.get('recipientId')
    
    print("request: {}".format(requestJson))
    app.config['botController'].sendDirectMessage(msg, sender, recipientId)
    return ('', HTTPStatus.OK)


