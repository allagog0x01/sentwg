# coding=utf-8
from .calls import call
import logging
import logging.config
import json

with open("./log_configuration.json", 'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)
 
logging.config.dictConfig(config_dict)
 
# Log that the logger was configured
logger = logging.getLogger("__name__")