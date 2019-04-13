
# Overview

I use Twitter as the web interface into home automation bots and Twitter is retiring the streaming interface in faviour
of webhooks through the new Account Activity API.  This botController provides an Abstracted web interface and implements
MQTT for local interface to home bots.

The implemented web interface is Twitter Account Activity API using webhooks, but it is possible to implement other 
web interfaces, for example discord, SMS, email or webpage.

With the move to the Account Activity API and webhooks a public interface is required and rather than open up all IoT devices 
this application prodives the public https interface and communicates to the home IoT devices via MQTT.

This application provides a webhook interface for Twitter to Post account activity to and it includes the following functions:
- WebHook registration
- Subscription to defined Twitter accounts (each bot has a Twitter handle)
- Twitter Login for accounts to authorize this application to access their Twitter account
- Fowarding of received Twitter Direct Messages sent to IoT devices from defined users
- Fowarding of IoT notification events to defined twitter administrators via Direct Messages
 

# Code overview
uses Flask to provide the REST structure and the Flask-OAuth library to handle the oauth_1 authenication with Twitter. The basic flow is:
1. the webhook is registered with Twitter
2. Try to subsribe to twitter accounts for defined IoT devices
3. If this fails the admin needs to access the applicatoins via a browswer and will be redirect to Twitter Login to authorize the application.
4. Authoirzed tokens and secrets are stored in a MongoDB
4. Incoming Direct Messages are treaded as IoT commands and send to IoT devices over MQTT.  IOT devices reponses are
send as Direct Messages back to sender
5. IoT status events are sent to all defined device admistrators via Direct Message

# Installation & setup

1. clone to '/usr/local/src/botController'
2. pip3 install -r requirements.txt
3. execute './setup.sh'
   - moves files to correct directories
   - sets the file permissions and
   - configures 'alarmMonitor' to run on boot
4. run 'sudo service botController start'

A Docker image is also available on [dockerhub](https://hub.docker.com/u/homebots/dashboard/).
to run this docker image.
1. sudo docker pull homebots/botcontroller
2. see docker readme for details on how to run


Other requirements include:

1. Publically accessible application on port 443.
Twitter requires a publically accessible webhook and this applicaton is for mydomain.com:443 and
I have it hosted on the DMZ.  For this a dynamic DNS or static IP is required along with SSL certifictes.
for the SSL certificate I used [letsencrypt](https://letsencrypt.org/getting-started/)

2. Configure the app at apps.twitter.com.  Most important is the 'callback URL' and you need to include two.
-  'https://mydomain.com/webhook/twitter' used for Twitter to post to.  This is the same as the environment vaiable above.
-  'https://mydomain.com/webhook/twitter/oauth-authorized' used as part of login authenitcation
-  set permissions to 'Read, Write and Access direct messages'

3.  Configure 'config.py' with your IoT device or Bot details.  example config:
```
config ={
    "mqtt_host": "ip address or hostname of the mqtt broker",
    "name": "name of this botcontroller",
    "SSL_cert": {
        "SSL_CERT": "/etc/letsencrypt/live/mydomain/fullchain.pem",
        "SSL_KEY":  "/etc/letsencrypt/live/mydomain/privkey.pem",
    },
    "mongodb": {
        "host": "ip address or hostname of mongodb",
        "port": "port number for mongodb",
    },
    "webAPI": {
        "type": "Twitter",
        "bots": {
            "Twittier sacreen name of bot 1" : {
                "name": "e.g. alarmbot",
                "users": ["screen_name1", "screen_name2"],
                "admins": {
                    "screen name of admin 1": "Twitter UID ",
                    "screen name of admin 2": "Twitter UID",
                },
            },
            "screen name of bot 2" : {
                "name": "local name of bot 2, same as configured in bot",
                "users": ["screen_name1", "screen_name2"],
                "admins": {
                    "screen name of admin 1": "Twitter UID ",
                    "screen name of admin 2": "Twitter UID",
                },
            },
        },
        "api_tokens": {
            "CONSUMER_KEY": "xxxxxx from apps.twitter.com",
            "CONSUMER_SECRET": "xxxxxx from apps.twitter.com",
        },
        "access_tokens": {
            "ACCESS_KEY": "xxxx from apps.twitter.com",
            "ACCESS_SECRET": "xxxx from apps.twitter.com",
        },
        "webhook": {
            "WEBHOOK_URL": "https://mydomain/webhook/twitter from app.twitter.com",
            "ENVNAME": "dev - conigured at developer.twitter.com",
        },
    },
}
```



Note:  the application provides a public notification and control interface for all IoT devices and bots on 
the internal home network.  As such it is exposed to both the internet and internal network and securing the
the hosting server is important, but I'll leave that to you.

This code is provided as an example and not intended to be directly used in your environment.


# API Reference

The application has internal and external APIs.
External APIs interface to Twitter and comprise the 1) the Account Activity and login APIs, 2) the requests
API implemented by twitterAPI

Internal interface to IoT devices is MQTT.  Incomming commands will be posted to 'bot name'/command
(for example 'alarmbt/command'), and the botContoller will subscribe to 'bot name'/response and 'bot name'/event.

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
Direct Messages sent from one of the Users to one of the Iot devices/Bots.

#### The TwitterAPI is used to send Twitter request,
- Create WebHook
- Subscribe to Account Activity
- send Diret Messages


## Internal API
#### The Request library is use to send requests to the IoT devices and bots
- public to topic 'bot name'/command

#### MQTT topic for IoT devices to post notifications to
- subscribe to topic 'bot name'/event
- subscribe to topic 'bot name'/response


# Acknowledgements

developed in collaboration with [Sam Cullin](https://samcullin.github.io/)
