from ..config import DEFAULT_GAS
from ..cosmos import call as cosmos_call
from ..db import db
from ..node import add_tx
from ..node import node
from ..node import update_session
from ..vpn import disconnect_client


def update_session_status(pub_key, status):
    _ = db.clients.find_one_and_update({
        'pub_key': pub_key
    }, {
        '$set': {
            'status': status
        }
    })


def end_session(pub_key):
    session = db.clients.find_one({
        'pub_key': pub_key,
        'status': 'CONNECTED'
    })
    if session is not None:
        session_id = session['session_id']
        update_session_status(pub_key, 'DISCONNECTED')
        disconnect_client(pub_key)
        if 'signatures' in session and len(session['signatures']) > 0:
            signature = session['signatures'][-1]
            error, data = cosmos_call('get_vpn_payment', {
                'amount': signature['amount'],
                'session_id': session_id,
                'counter': signature['index'],
                'name': node.config['account']['name'],
                'gas': DEFAULT_GAS,
                'isfinal': True,
                'password': node.config['account']['password'],
                'sign': signature['hash']
            })
            if error is None:
                tx = {
                    'from_account_address': 'VPN_PAYMENT',
                    'to_account_address': session['account_addr'],
                    'tx_hash': data['hash'].encode()
                }
                error, data = add_tx(tx)
                if error is None:
                    error, data = update_session(session_id, session['token'], signature['amount'])
            print(error, data)
