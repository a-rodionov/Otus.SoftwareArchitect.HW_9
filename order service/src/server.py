import os
import json
import pika
import datetime

from flask import Flask, request, g
from flask_api import status
from flask_expects_json import expects_json

from order import *
from repository import OrderRepository
from controller import OrderController
from messages.order_created import OrderCreated

order_creation_schema = {
    'type': 'object',
    'properties': {
        'user_account_id': {'type': 'number'},
        'total_price': {'type': 'number'},
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
        },
        'delivery_address': {'type': 'string'},
        'delivery_time': {'type': 'string'}
    },
    'required': ['user_account_id', 'total_price', 'goods', 'delivery_address', 'delivery_time']
}

ERROR_UNEXPECTED = 1
ERROR_INPUT_DATA = 2
ERROR_OBJECT_NOT_FOUND = 3

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
    'MESSAGE_BROKER_URI': os.environ.get('MESSAGE_BROKER_URI', ''),
    'HOSTNAME': os.environ['HOSTNAME'],
    'APP_NAME': os.environ.get('APP_NAME', 'no name'),
}

app = Flask(__name__)
order_controller = OrderController(OrderRepository(config['DATABASE_URI']))

@app.route("/")
def hello():
    return 'Application \'' + config['APP_NAME'] + '\' from ' + config['HOSTNAME'] + '!'

@app.route("/health")
def health():
    return '{"status": "ok"}'

@app.route("/config")
def configuration():
    return json.dumps(config)


@app.route('/order/order', methods=['POST'])
@expects_json(order_creation_schema)
def order_create():
    try:
        g.data['id'] = -1
        g.data['status'] = OrderStatus.IN_PROGRESS.value
        order = Order.from_dict(g.data)
        order_controller.create_order(order)
        if order._id == -1:
            return '', status.HTTP_400_BAD_REQUEST
        else:
            connection = pika.BlockingConnection(pika.URLParameters(config['MESSAGE_BROKER_URI']))
            channel = connection.channel()
            channel.exchange_declare(exchange='topic_order', exchange_type='topic')
            message = OrderCreated(order._id,
                                   order._user_account_id,
                                   order._total_price,
                                   order._goods,
                                   order._delivery_address,
                                   order._delivery_time)
            channel.basic_publish(exchange='topic_order', routing_key='order.order.created', body=json.dumps(OrderCreated.to_dict(message)))
            connection.close()
            return json.dumps({'order_id': order._id}), status.HTTP_201_CREATED
    except Exception as exc:
        return json.dumps({'code': ERROR_UNEXPECTED, 'message': str(exc)}), status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/order/order/<int:order_id>', methods=['GET'])
def order_get(order_id):
    try:
        order = order_controller.get_order(order_id)
        if order is None:
            return '', status.HTTP_404_NOT_FOUND
        else:
            return json.dumps(Order.to_dict(order)), status.HTTP_200_OK
    except Exception as exc:
        return json.dumps({'code': ERROR_UNEXPECTED, 'message': str(exc)}), status.HTTP_500_INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    app.run(host='0.0.0.0',port='8000')
