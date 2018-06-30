# Note
The application works but I am cleaning it up and documenting it for publication.

# Synopsis

Twitter is retiring the streaming interface in faviour of webhooks through the new Account Activity API.  I use the streaming API as an interface to IoT devices
to send them commands via Direct Messages, and for the devices to send notifications, also via Direct Messages.

with the move to the Account Activity API and webhooks a public interface is required nad rather than open up all IoT devices this application prodives a
the public interface and interfaces to the IoT devices via REST APIs.

This application provides a webhook interface for Twitter to Post account activity to and it includes the following functions:
- WebHook registration
- Subscription to defined accounts
- Twitter Login for accounts to authorize this application to access their Twitter account
- Fowarding of received Twitter Direct Messages snet to IoT devices
- Fowarding of IoT notification events to defined twitter users via Direct Messages
 


# Code Example

Show what the library does as concisely as possible, developers should be able to figure out **how** your project solves their problem by looking at the code example. Make sure the API you are showing off is obvious, and that your code is short and concise.

# Motivation

Driven by Twitters decision to retire the streaming interface in favour of the Account activity Webhook API.

# Overview
uses Flask to provide the REST structure and the Flask-OAuth library to handle the oauth_1 authenication with Twitter. The basic flow is:
1. the webhook is registered with Twitter
2. Try to subsribe to define IoT devices
3. If this fails the admin needs to access the applicatoins via a browswer and will be redirect to Twitter Login to authorize the application.
4. Authoirzed token and secreates are stored in a MongoDB
4. Incoming Direct Messages are treaded as IoT commans and Posted to the IoT devices
5. IoT status events are sent to all dedined admistrators

# Installation & setup

python requirements are defined in requirements.txt
Other requirements include:

1. Publically accessible application on port 443.
Twitter requires a publically accessible webhook and this applicaton is for mydomain.com:443 and
I have it hosted on the DMZ.  For this a dynamic DNS or static IP is required along with SSL certifictes.
for the SSL certificate I used [letsencrypt](https://letsencrypt.org/getting-started/)

2. Define environment variables for
- 'CONSUMER_KEY', 'CONSUMER_SECRET', 'ACCESS_KEY', 'ACCESS_SECRET', which are the keys
for the application configured in apps.twitter.com
- 'ENVNAME', which is the development environment name configured in developer.twitter.com
- 'WEBHOOK_URL', which is the Webhook url is twitter uses to post events.

3. Configure the app at apps.twitter.com.  Most important is the 'callback URL' and you need to include two.
-  'https://mydomain.com/webhook/twitter' used for Twitter to post to.  This is the same as the environment vaiable above.
-  'https://mydomain.com/webhook/twitter/oauth-authorized' used as part of login authenitcation
-  set permissions to 'Read, Write and Access direct messages'

4.  Configure 'bot-config.py' with your IoT device or Bot details.  example config:
`bot_config ={
    "device1" : {                                   # A simple label. e.g. 'thermostat'
        "screen_name": "security_123",              # Twitter screen_name of the device
        "webhook": "http://192.168.0.10/webhook",   # webhook url of the device.  
        "users": ["chris_cullin"]                   # lit of Twitter users that can send commands to device
    },
    "device2" : {
        "screen_name": "stock_trader",
        "webhook": "http://192.168.0.11/webhook",
        "users": ["chris_cullin"]
    },
}`



Note:  the application provides a public notification and control interface for all IoT devices and bots on 
the internal home network.  As such it is exposed to both the internet and internal and securing the
the hosting server is important, but I'll leave that to you.

This code is provided as an example and not intended to be directly used in your environment.


# API Reference

The application has internal and external APIs.
External APIs interface to Twitter and comprise the 1) the Account Activity and login APIs, 2) the requests
API implemented by twitterAPI

Internal APIs interface to IoT device and bots on the home network, and include 1) request to post to devices,
and 2) a webhook for devices to send notifications to.

## External API
#### Twitter Account Activity and login API
- mydomain.com/webhook/twitter/login
  Browser url for user to login into twitter and authoize this application.
  For example - the home thermostat has a twitter account and you must do a onetime login at this url
  to authorize the application.  Authorization tokens are then stored in a MongoDB

- mydomain.com/webhook/twitter/oauth-authorized
  Call back URL as part of Twiiter login. Performs the authorization tokens to MongoDB

- mydomain.com/webhook/twitter ['GET']
  provides the CRC challenge response for Twitter authenitcation

- mydomain.com/webhook/twitter ['POST']
  the actual webhook that Twitter posts all account activity to.  This application is looking for
Direct Messages sent from one of the Admins to one of the Iot devices/Bots.

#### The TwitterAPI is used to send Twitter request,
- Create WebHook
- Subscribe to Account Activity
- send Diret Messages


## Internal API
#### The Request library is use to send requests to the IoT devices and bots
- send Command.  Ths is a POSt to a webhook implemented in the IoT device

#### Webhook for IoT devices to post notifications to
- mydomain.com/webhook/bot

# Tests
Describe and show how to run the tests with code examples.

# Acknowledgements

reference the sample code used for webhooks

# License

A short snippet describing the license (MIT, Apache, etc.)
