from routes import app
import os, logging
import Twitter
from time import sleep
from http import HTTPStatus
from threading import Thread
import ssl

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(threadName)s - %(module)s - %(lineno)d:  %(message)s')
console.setFormatter(formatter)
log.addHandler(console)

from flask import Flask
from bots import BotController
from mongodb import Mongodb
from bot_config import bot_config


def main():

    keys = Mongodb()
    
    botController = BotController(bot_config, keys)
    
    # Start Flask web service in a thread so its non blocking
    app_thread = Thread(target=start_app, name='flask-app', args=(botController,), daemon=True)
    app_thread.start()
    
    ACCESS_KEY = os.environ.get('ACCESS_KEY')
    ACCESS_SECRET = os.environ.get('ACCESS_SECRET')
    r = Twitter.create_webhook(ACCESS_KEY, ACCESS_SECRET)
    
    if r != 200:
        log.error("webhook registration failed.  Error: {}".format(r))
        exit()
    botController.run()
    
        
def start_app(botctl):
    app.config['SECRET_KEY'] = 'thisissupposedtobeasecret'
    app.config['keys'] = Mongodb()
    app.config['botController'] = botctl

    # Define the https SSL context
    SSL_CERT = os.environ.get('SSL_CERT')
    SSL_KEY = os.environ.get('SSL_KEY')
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(SSL_CERT, SSL_KEY)
    
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    app.run(host='0.0.0.0', port=443, debug=True, ssl_context=context, use_reloader=False)



            
if __name__ == "__main__" :

    log.debug("starting main")
    main()
    while True:
        sleep(2)
    
    log.info("program exiting")
    
    