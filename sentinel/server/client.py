# coding=utf-8
import json
import falcon
from ..db import db
from ..helpers import end_session
import logging


class GetSessionUsage(object):
    def on_post(self, req, res, account_addr, session_id):
        """
        @api {POST} /clients/{account_addr}/sessions/{session_id}/usage Usage of the current session
        @apiName GetSessionUsage
        @apiGroup Client
        @apiParam {String} account_addr Cosmos account address of the client.
        @apiParam {String} session_id Unique session ID.
        @apiParam {String} token Token for communication with node.
        @apiSuccess {Boolean} success Success key.
        @apiSuccess {Object} usage Usage of the current session.
        """
        account_addr = str(account_addr)
        session_id = str(session_id)
        token = str(req.body['token'])
        logger = logging.getLogger(__name__)

        client = db.clients.find_one({
            'account_addr': account_addr,
            'session_id': session_id,
            'token': token,
            'status': 'CONNECTED'
        })
        if client is not None:
            message = {
                'success': True,
                'usage': {"up": client['usage']['upload'],
                          "down": client['usage']['download']}
            }
            logger.info(message)
        else:
            message = {
                'success': False,
                'message': 'Wrong details.'
            }
            logger.warning(
                'someOne trying get sessionUsage with wrong details')

        res.status = falcon.HTTP_200
        res.body = json.dumps(message)


class DisconnectClient(object):
    def on_post(self, req, res, account_addr, session_id):
        """
        @api {POST} /clients/{account_addr}/sessions/{session_id}/disconnect Disconnect a client
        @apiName DisconnectClient
        @apiGroup Client
        @apiParam {String} account_addr Cosmos account address of the client.
        @apiParam {String} session_id Unique session ID.
        @apiParam {String} token Token for communication with node.
        @apiSuccess {Boolean} success Success key.
        """
        account_addr = str(account_addr)
        session_id = str(session_id)
        token = str(req.body['token'])
        logger = logging.getLogger(__name__)

        client = db.clients.find_one({
            'account_addr': account_addr,
            'session_id': session_id,
            'token': token,
            'status': {'$in': [
                'CONNECTED',
                'LIMIT_EXCEEDED']}
        })
        if client is not None:
            end, err = end_session(client['pub_key'])
            if end:
                message = {
                    'success': True,
                    'message': 'Disconnected successfully.'
                }
            else:
                message = {
                    'success': False,
                    'message': 'Not Disconnected..'
                }
                logger.error(message)
        else:
            message = {
                'success': False,
                'message': 'Wrong details.'
            }
            logger.warning('someOne trying get disconnect with wrong details')

        logger.info(message)
        res.status = falcon.HTTP_200
        res.body = json.dumps(message)
