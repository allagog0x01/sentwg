# coding=utf-8
from .server import APIServer
from .client import DisconnectClient

import logging
import logging.config
import json

with open("./sentwg/log_configuration.json", 'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)
 
logging.config.dictConfig(config_dict)
 
# Log that the logger was configured
logger = logging.getLogger("__name__")
