# coding=utf-8
import time
from multiprocessing import Process
from thread import start_new_thread

from sentinel.config import DEFAULT_GAS
from sentinel.config import VERSION
from sentinel.cosmos import call as cosmos_call
from sentinel.helpers import end_session
from sentinel.helpers import update_session_status
from sentinel.node import get_free_coins
from sentinel.node import list_node
from sentinel.node import node
from sentinel.node import update_node
from sentinel.node import update_sessions
from sentinel.server import APIServer
from sentinel.vpn import get_sessions
from sentinel.vpn import update_session_data
from sentinel.vpn import wireguard
from sentinel.config import LIMIT_1GB
from sentinel.db import db

import logging
import logging.config
import json
with open("log_configuration.json", 'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)
logging.config.dictConfig(config_dict)

logger = logging.getLogger(__name__)


def alive_job():
    while True:
        try:
            update_node('alive')
        except Exception as err:
            logger.exception(err)

        time.sleep(30)


def sessions_job():
    extra = 5
    while True:
        try:
            sessions = get_sessions()
            sessions_len = len(sessions)
            if (sessions_len > 0) or (extra > 0):
                update_sessions(sessions)
                extra = 5 if sessions_len > 0 else extra - 1
        except Exception as err:
            logger.exception(err)

        time.sleep(5)


def api_server_process():
    while True:
        try:
            options = {
                'bind': '0.0.0.0:{}'.format(node.config['api_port']),
                'loglevel': 'debug'
            }
            APIServer(options).run()
        except Exception as err:
            logger.exception(err)

        time.sleep(5)


if __name__ == '__main__':
    print('')
    account_name = raw_input('Please enter account name: ')
    account_password = raw_input('Please enter account password: ')
    print('')
    node.update_info('config', {
        'account_name': account_name,
        'account_password': account_password,
    })

    if node.config['account']['address'] is None:
        error, resp = cosmos_call('generate_seed', None)
        if error:
            logger.exception(error)
            exit(1)
        else:
            error, resp = cosmos_call('get_keys', {
                'seed': str(resp['seed']),
                'name': node.config['account']['name'],
                'password': node.config['account']['password']
            })
            if error:
                logger.exception(error)
                exit(2)
            else:
                node.update_info('config', {
                    'account_address': str(resp['address'])
                })
                error = get_free_coins()
                if error is not None:
                    logger.exception(error)
                    exit(3)

    node.update_info('location')
    node.update_info('netspeed')

    if node.config['register']['hash'] is None:
        error, resp = cosmos_call('register_vpn_node', {
            'ip': str(node.ip),
            'upload_speed': int(node.net_speed['upload']),
            'download_speed': int(node.net_speed['download']),
            'price_per_gb': int(node.config['price_per_gb']),
            'enc_method': str(node.config['wireguard']['enc_method']),
            'description': str(node.config['description']),
            'location_latitude': int(node.location['latitude'] * 10000),
            'location_longitude': int(node.location['longitude'] * 10000),
            'location_city': str(node.location['city']),
            'location_country': str(node.location['country']),
            'node_type': 'wireguard',
            'version': VERSION,
            'name': str(node.config['account']['name']),
            'password': str(node.config['account']['password']),
            'gas': DEFAULT_GAS
        })
        if error:
            logger.exception(error)
            exit(4)
        else:
            node.update_info('config', {
                'register_hash': str(resp['hash'])
            })

    if node.config['register']['token'] is None:
        error, resp = list_node()
        if error:
            logger.exception(error)
            exit(5)
        else:
            node.update_info('config', {
                'register_token': str(resp['token'])
            })

    update_node('details')

    wireguard.start()
    api_server = Process(target=api_server_process, args=())
    api_server.start()

    start_new_thread(sessions_job, ())
    start_new_thread(alive_job, ())

    while True:
        parsed_config = wireguard.parse_wg_data()
        

        if len(parsed_config) > 0:
            for peer_data in parsed_config:
                client = db.find_one({'pub_key':peer_data['pub_key'],'status':'CONNECTED'})
                if peer_data['latest_handshake'] < 180 and peer_data['pub_key']:
                    update_session_status(peer_data['pub_key'], 'CONNECTED')

                    update_session_data(peer_data)
                    
                    if client is not None and client['max_usage']['download'] <= client['usage']['download']:
                        update_session_status(
                            peer_data['pub_key'], 'LIMIT_EXCEEDED')

                elif peer_data['latest_handshake'] > 180 or (client is not None and client['max_usage']['download'] <= client['usage']['download']):
                    end, err = end_session(peer_data['pub_key'])
                    if end:

                        logger.warning('session ended')
                    else:
                        logger.exception(error)

                else:
                    update_session_data(peer_data)

        time.sleep(10)
