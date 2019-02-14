# coding=utf-8
from .fetch import fetch
from .middlewares import ValidateRequest, JSONTranslator
import logging
import logging.config
import json

with open("./sentwg/log_configuration.json", 'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)
 
logging.config.dictConfig(config_dict)
 
# Log that the logger was configured
logger = logging.getLogger("__name__")