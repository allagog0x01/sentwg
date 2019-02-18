# coding=utf-8
from .helpers import get_sessions
from .helpers import update_session_data
from .wireguard import wireguard
import json
import logging
with open("./log_configuration.json", 'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)

logging.config.dictConfig(config_dict)


logger = logging.getLogger("__name__")
