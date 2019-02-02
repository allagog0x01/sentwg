# coding=utf-8
import json
import falcon



class JSONTranslator(object):
    def process_request(self, req, _):
        body = req.stream.read()
        try:
            req.body = json.loads(body.decode('utf-8'))
        except ValueError:
            _ = {
                'message': 'Malformed JSON',
                'errors': ['JSON was incorrect or not encoded as UTF-8.']
            }

class ValidateRequest(object):
    def process_request(self, req, res, _):
        #account_addr = str(account_addr)
        #session_id = str(session_id)
        token = str(req.body['token'])
        if token is None:

            message = {
                'success': False,
                'message': 'Token is missing'
            }
            res.status = falcon.HTTP_200
            res.body = json.dumps(message)
        #TODO response has to be delivered from here