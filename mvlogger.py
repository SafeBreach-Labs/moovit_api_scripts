import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s]  %(message)s')

logging.addLevelName(logging.INFO, "*")
logging.addLevelName(logging.DEBUG, "&")
logging.addLevelName(logging.ERROR, "!")