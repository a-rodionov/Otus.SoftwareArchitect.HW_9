import os
import json
from flask import Flask, request, g
from flask_api import status
from flask_expects_json import expects_json

from order import *
from user_account import UserAccount
from repository import BillingRepository
from controller import BillingController

user_creation_schema = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
        'firstName': {'type': 'string'},
        'lastName': {'type': 'string'},
        'email': {'type': 'string'},
        'phone': {'type': 'string'}
    },
    'required': ['username', 'password', 'firstName', 'lastName', 'email', 'phone']
}

deposit_schema = {
    'type': 'object',
    'properties': {
        'amount': {'type': 'number'}
    },
    'required': ['amount']
}

ERROR_UNEXPECTED = 1
ERROR_INPUT_DATA = 2
ERROR_OBJECT_NOT_FOUND = 3

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
    'HOSTNAME': os.environ['HOSTNAME'],
    'APP_NAME': os.environ.get('APP_NAME', 'no name'),
}

app = Flask(__name__)
billing_controller = BillingController(BillingRepository(config['DATABASE_URI']))

@app.route("/")
def hello():
    return 'Application \'' + config['APP_NAME'] + '\' from ' + config['HOSTNAME'] + '!'

@app.route("/health")
def health():
    return '{"status": "ok"}'

@app.route("/config")
def configuration():
    return json.dumps(config)


@app.route('/billing/user', methods=['POST'])
@expects_json(user_creation_schema)
def user_create():
    try:
        user_id = billing_controller.add_new_user_account(g.data['username'],
                                                          g.data['password'].encode('utf-8'),
                                                          g.data['firstName'],
                                                          g.data['lastName'],
                                                          g.data['email'],
                                                          g.data['phone'])
        if user_id is None:
            return '', status.HTTP_400_BAD_REQUEST
        else:
            return json.dumps({'user_id': user_id}), status.HTTP_201_CREATED
    except Exception as exc:
        return json.dumps({'code': ERROR_UNEXPECTED, 'message': str(exc)}), status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/billing/user/<int:user_id>', methods=['GET'])
def user_get(user_id):
    try:
        user_account = billing_controller.get_user_account(user_id)
        if user_account is None:
            return '', status.HTTP_404_NOT_FOUND
        else:
            return json.dumps(UserAccount.to_dict(user_account)), status.HTTP_200_OK
    except Exception as exc:
        return json.dumps({'code': ERROR_UNEXPECTED, 'message': str(exc)}), status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/billing/deposit/<int:user_id>', methods=['POST'])
@expects_json(deposit_schema)
def deposit(user_id):
    try:
        if billing_controller.deposit(user_id, g.data['amount']):
            return '', status.HTTP_200_OK
        else:
            return '', status.HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as exc:
        return json.dumps({'code': ERROR_UNEXPECTED, 'message': str(exc)}), status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/billing/order/<int:order_id>', methods=['GET'])
def order_get(order_id):
    try:
        order = billing_controller.get_order(order_id)
        return json.dumps(Order.to_dict(order)), status.HTTP_200_OK
    except Exception as exc:
        return json.dumps({'code': ERROR_UNEXPECTED, 'message': str(exc)}), status.HTTP_500_INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    app.run(host='0.0.0.0',port='8000')
