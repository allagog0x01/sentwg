from .session import end_session
from .session import update_session_status
from .session import limit_exceed_disconnect
import logging
import logging.config
import json

with open("./log_configuration.json", 'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)
 
logging.config.dictConfig(config_dict)
 

logger = logging.getLogger("__name__")