from Utilities.NotificationCenter import NotificationCenter as NC
from flask import Blueprint, jsonify, request
from uuid import uuid4
from time import time

mod = Blueprint(__name__, 'api')
device_id = str(uuid4())[1:6].upper()


def _error(msg):
    return jsonify({
        "ok": False,
        "msg": msg
    })


@mod.route('/', methods=['GET'])
def index_get():
    return jsonify({
        "ok": True,
        "node": device_id,
        "time": time()
    })


msg_data = {}


@NC.notify_on('broadcast')
def broadcast_store(data, msg_id):
    msg_data[msg_id] = data


@mod.route('/history', methods=['GET'])
def history_get():
    return jsonify({
        'ok': True,
        'data': [{'msg_id': msg_id,
                  'data': data} for msg_id, data in msg_data.items()]
    })


@mod.route('/broadcast', methods=['POST'])
def broadcast_post():
    if not request.json:
        return _error('json required')
    if not 'data' in request.json:
        return _error('missing data')

    data = request.json['data']
    byte = bytes(data.encode())

    if len(byte) > 250:
        return _error("data too large")

    msg_id = str(uuid4())[1:5].upper()
    NC.default().post_notification('queue_broadcast',
                                   threaded=False,
                                   data=data,
                                   msg_id=msg_id)

    return jsonify({
        "ok": True,
        "node": device_id,
        "bytes": len(byte),
        "data": data,
        "msg_id": msg_id
    })
