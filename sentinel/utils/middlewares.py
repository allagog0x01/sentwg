# coding=utf-8
import json
import falcon

import logging

class JSONTranslator(object):
    def process_request(self, req, _):
        body = req.stream.read()
        try:
            req.body = json.loads(body.decode('utf-8'))
        except ValueError:
            logger = logging.getLogger(__name__)
            
            _ = {
                'message': 'Malformed JSON',
                'errors': ['JSON was incorrect or not encoded as UTF-8.']
            }
            logger.error(_)

class ValidateRequest(object):
    def process_request(self, req, _):
        #account_addr = str(account_addr)
        #session_id = str(session_id)
        token = str(req.body['token'])
        logger = logging.getLogger(__name__)
        if token is None:

            message = {
                'success': False,
                'message': 'Token is missing'
            }
            logger.warning(message) 
        #TODO response has to be delivered from here