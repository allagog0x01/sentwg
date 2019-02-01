# coding=utf-8
import json

import falcon

from ..db import db
from ..helpers import end_session
from ..vpn import wireguard


class AddSessionDetails(object):
    def on_post(self, req, res, account_addr, session_id):
        # TODO did the request really come from master node
        account_addr = str(account_addr)
        # TODO: CHECK ACCOUNT ADDR AND SESSION ID VALIDATIONS
        session_id = str(session_id)
        # TODO ADD TO CHECK TOKEN and also validate the incoming token for it's size type and any other
        token = str(req.body['token'])

        client = db.clients.find_one({
            'account_addr': account_addr,
            'session_id': session_id
        })

        if client is not None:
            if client['status'] and client['status'] is not None:
                message = {
                'success': True,
                'message': 'Session details already added.'
            }
            else:
                update = db.clients.find_one_and_update({
                        'account_addr': account_addr,
                        'session_id': session_id
                    }, {'$set':{
                         'token': token,
                         'status': 'ADDED_SESSION_DETAILS'
                     }
                })

                if update is not None:                    
                    message = {
                        'success': True,
                        'message': 'Session details added successfully.'
                    }
                else:
                    message = {
                        'success': False,
                        'message': 'Session details not added.'
                    }

        else:
            message = {
                'success': False,
                'message': 'Wrong details.'
            }

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
        # TODO ADD STRICT VALIDATION FOR PUBLIC KEYS
        pub_key = str(req.body['pub_key'])

        # TODO: WHAT IS THIS DOING.

        client = db.clients.find_one({
            'account_addr': account_addr,
            'session_id': session_id,
            'token': token
         })
        if client is not None:
            if client['status'] and client['status'] == 'CONNECTED':
                message = {
                    'success': True,
                    'message': 'Already connected / Already shared VPN credentials..'
                }
            elif client['status'] and client['status'] == 'ADDED_SESSION_DETAILS':
                client_vpn_config, error = wireguard.add_peer(pub_key)

                # TODO CHECK IF PEER IS ADDED PROPERLY.IF PEER ADITION WAS DONE PROPERLY AT THE SAME CHECK IF THE PEER IS ALLOCATED IS SAME_IP
                if error is None:
                    update = db.update(client,
                       {'$set': {
                           'usage': {
                               'upload': 0,
                               'download': 0
                           },
                           'pub_key': pub_key,
                           'status': 'CONNECTED'
                       }
                       })
                    message = {
                        'success': True,
                        'message': 'connected / Successfully shared VPN credentials..'
                    }    
                else:
                    message = {
                        'success': False,
                        'message': 'peer is not added \n'+ error
                    }    
            else:
                message = {
                    'success': False,
                    'message': 'Session details not added..'
                }
        else:
            message = {
                    'success': False,
                    'message': 'Wrong details..'
                }

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
                'status': 'CONNECTED'
            })
            if client:
                _ = db.clients.update(client, 
                    {
                        '$push': {
                            'signatures': signature
                        }
                    })
                if signature['final']:
                    end_session(session_id)
                message = {
                    'success': True
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
                'message': 'Invalid body parameters'
            }
        res.status = falcon.HTTP_200
        res.body = json.dumps(message)
