# coding=utf-8
import json
import falcon
from ..db import db
from ..helpers import end_session
import logging
import jsonschema

logger = logging.getLogger(__name__)


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
        schema = {
            "type": "object", "properties":  {
                "token":  {"type": "string"},
            },
            "required": ["token"]
        }
        try:
            jsonschema.validate(req.body, schema)
            account_addr = str(account_addr)
            session_id = str(session_id)
            token = str(req.body['token'])

            client = db.clients.find_one({
                'account_addr': account_addr,
                'session_id': session_id,
                'token': token,
                'status': {'$in': ['CONNECTED', 'LIMIT_EXCEEDED']}
            })
            if client is not None and client['status'] == 'CONNECTED':
                message = {
                    'success': True,
                    'usage': {"up": client['usage']['upload'],
                              "down": client['usage']['download']},
                }
            elif client is not None and client['status'] == 'LIMIT_EXCEEDED':
                message = {
                    'success': False,
                    'message': 'limit has exceeded'
                }
            else:
                message = {
                    'success': False,
                    'message': 'Wrong details'
                }
                logger.warning(
                    'someOne trying get sessionUsage with wrong details')
        except Exception as e:
            message = {
                'success': False,
                'message': 'invalid request missing request parameters'
            }
            logger.exception(e)
        logger.info(message)
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
        schema = {
            "type": "object", "properties":  {
                "token":  {"type": "string"},
            },
            "required": ["token"]
        }
        try:
            jsonschema.validate(req.body, schema)
            account_addr = str(account_addr)
            session_id = str(session_id)
            token = str(req.body['token'])

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
                    logger.error(err)
            else:
                message = {
                    'success': False,
                    'message': 'Wrong details.'
                }
                logger.warning(
                    'someOne trying get disconnect with wrong details')
        except Exception as e:
            message = {
                'success': False,
                'message': 'invalid request missing request parameters'
            }
            logger.exception(e)

        logger.info(message)
        res.status = falcon.HTTP_200
        res.body = json.dumps(message)
