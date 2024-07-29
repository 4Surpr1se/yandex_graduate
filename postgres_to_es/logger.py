import logging
import os
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('ELT_Service')
logger.setLevel(logging.INFO)

if not os.path.exists('logs'):
    os.makedirs('logs')

handler = RotatingFileHandler('logs/elt_service.log', backupCount=5)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
