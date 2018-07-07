#!/usr/bin/wnv python3
from time import sleep
from threading import Thread
import ssl
import sys, signal

# local imports
from routes import app
from bots import BotController
from config import config
from logger import log

class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def service_shutdown(signum, frame):
    log.info('Caught signal %d' % signum)
    raise ServiceExit



def main():
    # Register the signal handlers
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)
    
    try:
        botController = BotController(config)
        
        # Start Flask web service in a thread so its non blocking
        app_thread = Thread(target=start_app, name='flask-app', args=(config.get('app'), botController), daemon=True)
        app_thread.start()

        botController.run()
        while True:
            sleep(2)

    except ServiceExit:
        log.info("Shutting Down")
        sys.exit(0)
    
        
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
    main()

    