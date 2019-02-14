from .session import end_session
from .session import update_session_status
import logging
import logging.config
import json

with open("./log_configuration.json", 'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)
 
logging.config.dictConfig(config_dict)
 
# Log that the logger was configured
logger = logging.getLogger("__name__")