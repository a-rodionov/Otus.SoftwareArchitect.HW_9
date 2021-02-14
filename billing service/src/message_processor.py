import os
import sys
import pika
import json
from messages.order_created import OrderCreated
from messages.order_canceled import OrderCanceled
from messages.shipping_order_reserved import ShippingOrderReserved
from messages.billing_order_reserved import BillingOrderReserved
from messages.billing_order_not_reserved import BillingOrderNotReserved
from repository import BillingRepository
from controller import BillingController

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
    'MESSAGE_BROKER_URI': os.environ.get('MESSAGE_BROKER_URI', ''),
}

billing_controller = BillingController(BillingRepository(config['DATABASE_URI']))

def callback(ch, method, properties, body):
    if 'order.order.created' == method.routing_key:
        message = OrderCreated.from_dict(json.loads(body))
        if not billing_controller.cache_new_order(message._id,
                                                  message._user_account_id,
                                                  message._total_price):
            ch.basic_publish(exchange = 'topic_order',
                             routing_key = 'billing.order.not_reserved',
                             body = json.dumps(BillingOrderNotReserved.to_dict(BillingOrderNotReserved(message._id))),
                             properties = pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                             ))
    elif 'order.order.canceled' == method.routing_key:
        message = OrderCanceled.from_dict(json.loads(body))
        billing_controller.cancel_order(message._id)
    elif 'shipping.order.reserved' == method.routing_key:
        message = ShippingOrderReserved.from_dict(json.loads(body))
        if billing_controller.pay_order(message._id):
            ch.basic_publish(exchange = 'topic_order',
                             routing_key = 'billing.order.reserved',
                             body = json.dumps(BillingOrderReserved.to_dict(BillingOrderReserved(message._id))),
                             properties = pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                             ))
        else:               
            ch.basic_publish(exchange = 'topic_order',
                             routing_key = 'billing.order.not_reserved',
                             body = json.dumps(BillingOrderNotReserved.to_dict(BillingOrderNotReserved(message._id))),
                             properties = pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                             ))

connection = pika.BlockingConnection(pika.URLParameters(config['MESSAGE_BROKER_URI']))
channel = connection.channel()
channel.exchange_declare(exchange='topic_order', exchange_type='topic')
result = channel.queue_declare('billing', durable=True)
for binding_key in ['order.order.*', 'shipping.order.reserved']:
    channel.queue_bind(exchange='topic_order', queue=result.method.queue, routing_key=binding_key)
channel.basic_consume(queue=result.method.queue, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
