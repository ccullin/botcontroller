bot_config ={
    "general bot name" : {
        "screen_name": "twitter screen_name of bot",
        "webhook": "url of the bots webhook",
        "users": ["screen_name of admin 1", "admin 2"]
    },
    "thermostat" : {
        "screen_name": "mithermostat",
        "webhook": "http://192.168.1.15/webhook",
        "users": ["chris_cullin",]
    },
    "controller": {
        "api_tokens": {
            "CONSUMER_KEY": "from apps.twitter",
            "CONSUMER_SECRET": "from apps.twitter",
        },
        "access_tokens": {
            "ACCESS_KEY": "from apps.twitter",
            "ACCESS_SECRET": "from apps.twitter",
        },
        "webhook": {
            "WEBHOOK_URL": "https://mydomain.com/webhook/twitter",
            "ENVNAME": "environment name from developer.twitter account activity API setup",
        },
    },
    "app": {
        "SSL_CERT": "directory path of SSL Cert",
        "SSL_KEY":  "directoty path of SSL key",
    },
}