# coding=utf-8
import json

from .routes import routes
from ..config import COSMOS_URL
from ..utils import fetch
import logging
logger = logging.getLogger(__name__)

def call(name, data):
    url = COSMOS_URL + routes[name]['route']
    method = routes[name]['method']

    if name == 'verify_hash':
        url += '/{}'.format(data['hash'])
    elif name == 'get_balance':
        url += '/{}'.format(data['address'])

    try:
        response = None
        if method == 'GET':
            response = fetch().get(url)
        elif method == 'POST':
            response = fetch().post(url, json=data)
        
        invalid_msg = {
                           'code': 2,
                           'message': 'Response data success is False.',
                           'error': str(response.content)
                       }

        if response and response.status_code == 200:
            if name == 'generate_seed':
                return None, {
                    'success': True,
                    'seed': response.content.decode()
                }
            elif name in ['get_keys', 'get_balance', 'verify_hash']:
                data = json.loads(response.content.decode())
                data.update({'success': True})
                return None, data
            else:
                data = response.json()
                if data['success']:
                    return None, data
                logger.warning(invalid_msg)
                return invalid_msg, None
        
        logger.warning(invalid_msg)
        return invalid_msg, None

    except Exception as error:
        logger.exception(error)
        return str(error), None
