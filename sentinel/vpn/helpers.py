# coding=utf-8
import subprocess


from ..db import db


def update_session_data(session_data):
    pub_key = session_data['pub_key']
    db.clients.find_one_and_update({
        'pub_key': pub_key,
        'status': 'CONNECTED'
    }, {
        '$set': {
            'usage': {
                'upload': session_data['usage']['upload'],
                'download': session_data['usage']['download']
            }
        }
    })


def get_sessions():
    sessions = []
    data = db.clients.find({
        'status': 'CONNECTED'
    })
    for client in data:
        sessions.append({
            'sessionId': client['session_id'],
            'usage': {
                        'download': client['usage']['download'],
                        'upload': client['usage']['upload']
                        }
        })
    return sessions
