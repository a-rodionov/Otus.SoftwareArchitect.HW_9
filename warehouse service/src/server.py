import os
import json
from flask import Flask, request, g
from flask_api import status
from flask_expects_json import expects_json

from goods import Goods
from order import OrderStatus, Order
from repository import WarehouseRepository
from controller import WarehouseController

ERROR_UNEXPECTED = 1
ERROR_INPUT_DATA = 2
ERROR_OBJECT_NOT_FOUND = 3

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
    'HOSTNAME': os.environ['HOSTNAME'],
    'APP_NAME': os.environ.get('APP_NAME', 'no name'),
}

app = Flask(__name__)
warehouse_controller = WarehouseController(WarehouseRepository(config['DATABASE_URI']))

goods_adjustment_schema = {
    'type': 'object',
    'properties': {
        'goods': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'goods_id': {'type': 'number'},
                    'quantity': {'type': 'number'}
                },
                'required': ['goods_id', 'quantity']
            }
        }
    },
    'required': ['goods']
}

order_creation_schema = {
    'type': 'object',
    'properties': {
        'order_id': {'type': 'number'},
        'goods': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'goods_id': {'type': 'number'},
                    'quantity': {'type': 'number'}
                },
                'required': ['goods_id', 'quantity']
            }
        }
    },
    'required': ['order_id', 'goods']
}

@app.route("/")
def hello():
    return 'Application \'' + config['APP_NAME'] + '\' from ' + config['HOSTNAME'] + '!'

@app.route("/health")
def health():
    return '{"status": "ok"}'

@app.route("/config")
def configuration():
    return json.dumps(config)


@app.route('/warehouse/adjust_goods', methods=['POST'])
@expects_json(goods_adjustment_schema)
def adjust_goods():
    try:
        goods = [Goods(**goods_dict) for goods_dict in g.data['goods']]
        if warehouse_controller.adjust_goods(goods):
            return '', status.HTTP_200_OK
        else:
            return '', status.HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as exc:
        return json.dumps({'code': ERROR_UNEXPECTED, 'message': str(exc)}), status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/warehouse/order/<int:order_id>', methods=['GET'])
def order_get(order_id):
    try:
        order = warehouse_controller.get_order(order_id)
        return json.dumps(Order.to_dict(order)), status.HTTP_200_OK
    except Exception as exc:
        return json.dumps({'code': ERROR_UNEXPECTED, 'message': str(exc)}), status.HTTP_500_INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    app.run(host='0.0.0.0',port='8000')
