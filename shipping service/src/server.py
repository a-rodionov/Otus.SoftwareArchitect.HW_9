import os
import json
import datetime

from flask import Flask, request, g
from flask_api import status
from flask_expects_json import expects_json

from order import *
from courier import Courier
from repository import ShippingRepository
from controller import ShippingController

ERROR_UNEXPECTED = 1
ERROR_INPUT_DATA = 2
ERROR_OBJECT_NOT_FOUND = 3

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
    'HOSTNAME': os.environ['HOSTNAME'],
    'APP_NAME': os.environ.get('APP_NAME', 'no name'),
}

app = Flask(__name__)
shipping_controller = ShippingController(ShippingRepository(config['DATABASE_URI']))

@app.route("/")
def hello():
    return 'Application \'' + config['APP_NAME'] + '\' from ' + config['HOSTNAME'] + '!'

@app.route("/health")
def health():
    return '{"status": "ok"}'

@app.route("/config")
def configuration():
    return json.dumps(config)


@app.route('/shipping/courier', methods=['POST'])
def courier_create():
    try:
        courier_id = shipping_controller.add_courier()
        if courier_id is None:
            return '', status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            return json.dumps({'courier_id': courier_id}), status.HTTP_201_CREATED
    except Exception as exc:
        return json.dumps({'code': ERROR_UNEXPECTED, 'message': str(exc)}), status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/shipping/courier/<int:courier_id>', methods=['GET'])
def get_courier(courier_id):
    try:
        courier = shipping_controller.get_courier(courier_id)
        return json.dumps(Courier.to_dict(courier)), status.HTTP_200_OK
    except Exception as exc:
        return json.dumps({'code': ERROR_UNEXPECTED, 'message': str(exc)}), status.HTTP_500_INTERNAL_SERVER_ERROR
                
@app.route('/shipping/order/<int:order_id>', methods=['GET'])
def order_get(order_id):
    try:
        order = shipping_controller.get_order(order_id)
        return json.dumps(Order.to_dict(order)), status.HTTP_200_OK
    except Exception as exc:
        return json.dumps({'code': ERROR_UNEXPECTED, 'message': str(exc)}), status.HTTP_500_INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    app.run(host='0.0.0.0',port='8000')
