config ={
    "mqtt_host": "hostname or ip address of the mqtt broker",
    "name": "name to assign to this bot controller, eg. botcontroller",
    "SSL_cert": {
        "SSL_CERT": "/etc/letsencrypt/live/mydomain.com/fullchain.pem",
        "SSL_KEY":  "/etc/letsencrypt/live/mydomain.com/privkey.pem",
    },
    "mongodb": {
        "host": "hostname or ip address of mongodb",
        "port": port number of mpngodb,
    },
    "webAPI": {
        "type": "Twitter",
        "bots": {
            "alarmbot" : {
                "webName": "Twitter name of bot 1",
                "users": ["Twitter name of user 1", "Twitter name of user 2"],
                "admins": {
                    "Twitter user 1": "user id",
                    "Twitter user 2": "user id",
                },
            },
            "tradebot" : {
                "webName": "Twitter name of bot 2",
               "users": ["Twitter name of user 1", "Twitter name of user 2"],
                "admins": {
                    "Twitter user 1": "user id",
                    "Twitter user 2": "user id",
                },            },
        },
        "api_tokens": {
            "CONSUMER_KEY": "xxxxxxxxxxxxxxxxxxxxx",
            "CONSUMER_SECRET": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
        },
        "access_tokens": {
            "ACCESS_KEY": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "ACCESS_SECRET": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        },
        "webhook": {
            "WEBHOOK_URL": "botcontroller webhook url that TWitter should call",
            "ENVNAME": "Twitter API environment name",
        },
    },
}
