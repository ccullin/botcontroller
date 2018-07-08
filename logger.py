import logging
from logging.handlers import RotatingFileHandler, QueueHandler


# Configure root logger the root for all module loggers.
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARNING)

# Define logging to console.
console = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(threadName)s - %(module)s - %(lineno)d:  %(message)s')
console.setFormatter(formatter)
root_logger.addHandler(console)

# Define logging to file.  Use same format as console.
logfile = RotatingFileHandler('/var/log/webhook.log', maxBytes=5096, backupCount=5)
logfile.setFormatter(formatter)
root_logger.addHandler(logfile)
