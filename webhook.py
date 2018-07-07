#!/usr/bin/wnv python3
from time import sleep
from threading import Thread
import ssl

# local imports
from routes import app
from bots import BotController
from config import config
from logger import log




def main():
    botController = BotController(config)
    
    # Start Flask web service in a thread so its non blocking
    app_thread = Thread(target=start_app, name='flask-app', args=(config.get('app'), botController))
    app_thread.start()
    
    botController.run()
    
        
def start_app(config, botctl):
    log.debug(config)
    app.config['SECRET_KEY'] = 'thisissupposedtobeasecret'
    app.config['botController'] = botctl
    SSL_CERT = config.get('SSL_CERT')
    SSL_KEY =  config.get('SSL_KEY')
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(SSL_CERT, SSL_KEY)
    app.run(host='0.0.0.0', port=443, debug=True, ssl_context=context, use_reloader=False, processes=5)



            
if __name__ == "__main__" :
    log.debug("starting main")
    main()
    while True:
        sleep(2)
    log.info("program exiting")
    
    