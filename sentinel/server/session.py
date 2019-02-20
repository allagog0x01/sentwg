# coding=utf-8
import json

import falcon
import logging

from ..db import db
from ..helpers import end_session
from ..vpn import wireguard


class AddSessionDetails(object):
    def on_post(self, req, res, account_addr, session_id):

        account_addr = str(account_addr)

        session_id = str(session_id)

        token = str(req.body['token'])
        maxUsage = req.body['maxUsage']
        client = db.clients.find_one_and_update({
            'account_addr': account_addr,
            'session_id': session_id,
            'token': token
        },
            {'$set': {
                'status': 'ADDED_SESSION_DETAILS',
                'max_usage': maxUsage
            }
        }, upsert=True)

        if client is not None:
            message = {
                'success': True,
                'message': 'Session details already added.'
            }

        else:
            message = {
                'success': True,
                'message': 'Session details successfully added.'
            }
        logger = logging.getLogger(__name__)
        logger.warning(message)
        res.status = falcon.HTTP_200
        res.body = json.dumps(message)


class GetVpnCredentials(object):
    def on_post(self, req, res, account_addr, session_id):
        """
        @api {POST} /clients/{account_addr}/sessions/{session_id}/credentials VPN Session credentials
        @apiName GetVpnCredentials
        @apiGroup Session
        @apiParam {String} account_addr Cosmos account address of the client.
        @apiParam {String} session_id Unique session ID.
        @apiParam {String} token Token for communication with node.
        @apiSuccess {Boolean} success Success key.
        @apiSuccess {String[]} ovpn OVPN data.
        """
        account_addr = str(account_addr)
        session_id = str(session_id)

        token = str(req.body['token'])

        pub_key = str(req.body['pub_key'])
        logger = logging.getLogger(__name__)

        client = db.clients.find_one({
            'account_addr': account_addr,
            'session_id': session_id,
            'token': token,
            'status': {'$in':['ADDED_SESSION_DETAILS','SHARED_VPN_CREDS']}
        })
        if client is not None:

            client_vpn_config, pub_key, error = wireguard.add_peer(pub_key)

            if client_vpn_config is not None:
                _ = db.clients.update_one(client,
                                          {'$set': {
                                              'usage': {
                                                  'upload': 0,
                                                  'download': 0
                                              },
                                              'pub_key': pub_key,
                                              'status': 'SHARED_VPN_CREDS'
                                          }
                                          })
                message = {
                    'success': True,
                    'message': 'Successfully SHARED_VPN_CREDS..',
                    'wireguard': client_vpn_config
                }
            elif error == 'Node is busy':
                message = {
                    'success': False,
                    'message': error
                }
                logger.error(error)
            else:

                message = {
                    'success': False,
                    'message': 'peer is not added'
                }
                logger.error(error)
        else:
            message = {
                'success': False,
                'message': 'Invalid Request / Wrong details..'
            }

        logger.warning(message)

        res.status = falcon.HTTP_200
        res.body = json.dumps(message)


class AddSessionPaymentSign(object):
    def on_post(self, req, res, account_addr, session_id):
        """
        @api {POST} /clients/{account_addr}/sessions/{session_id}/sign Add payment signature for the session
        @apiName AddSessionPaymentSigns
        @apiGroup Session
        @apiParam {String} account_addr Cosmos account address of the client.
        @apiParam {String} session_id Unique session ID.
        @apiParam {String} token Token for communication with node.
        @apiParam {Object} signature Info fo the signature.
        @apiParam {String} signature.hash Signature hash.
        @apiParam {Number} signature.index Signature index.
        @apiParam {String} signature.amount Signature amount to be claimed.
        @apiParam {Boolean} signature.final Whether Final signature or not.
        @apiSuccess {Boolean} success Success key.
        """

        account_addr = str(account_addr)
        session_id = str(session_id)
        token = str(req.body['token'])

        logger = logging.getLogger(__name__)

        if req.body['signature']:
            signature = {
                'hash': str(req.body['signature']['hash']),
                'index': int(req.body['signature']['index']),
                'amount': str(req.body['signature']['amount']),
                'final': req.body['signature']['final']
            }
            client = db.clients.find_one({
                'account_addr': account_addr,
                'session_id': session_id,
                'token': token,
                'status': {'$in': ['CONNECTED', 'LIMIT_EXCEEDED']}
            })
            if client is not None:
                _ = db.clients.update(client,
                                      {
                                          '$push': {
                                              'signatures': signature
                                          }
                                      })
                if signature['final'] and client['status'] != 'DISCONNECTED':
                    end, err = end_session(client['pub_key'])

                    if end:
                        message = {
                            'success': True,
                            'message': 'Successfully done payment session ended'
                        }
                        logger.info(message)
                    else:
                        message = {
                            'success': False,
                            'message': 'something went wrong session not ended'
                        }
                        logger.error(err)
                else:
                    message = {
                        'success': True,
                        'message': 'Successfully added payment sign'
                    }
            else:
                message = {
                    'success': False,
                    'message': 'Wrong details.'
                }
        else:
            message = {
                'success': False,
                'message': 'missing body parameters'
            }

            logger.error(message)

        res.status = falcon.HTTP_200
        res.body = json.dumps(message)
