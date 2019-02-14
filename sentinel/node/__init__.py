# coding=utf-8
from .controllers import add_tx
from .controllers import get_free_coins
from .controllers import list_node
from .controllers import update_node
from .controllers import update_session
from .controllers import update_sessions
from .node import node
import logging
import logging.config
import json

with open("./sentwg/log_configuration.json", 'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)
 
logging.config.dictConfig(config_dict)
 
# Log that the logger was configured
logger = logging.getLogger("__name__")