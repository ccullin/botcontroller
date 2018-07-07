import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(threadName)s - %(module)s - %(lineno)d:  %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
