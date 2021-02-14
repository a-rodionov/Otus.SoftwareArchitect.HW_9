import os
import sys
import pika
import json
from messages.order_canceled import OrderCanceled
from messages.billing_order_reserved import BillingOrderReserved
from messages.warehouse_order_not_reserved import WarehouseOrderNotReserved
from repository import OrderRepository
from controller import OrderController

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
    'MESSAGE_BROKER_URI': os.environ.get('MESSAGE_BROKER_URI', ''),
}

order_controller = OrderController(OrderRepository(config['DATABASE_URI']))

def callback(ch, method, properties, body):
    if 'warehouse.order.not_reserved' == method.routing_key:
        message = WarehouseOrderNotReserved.from_dict(json.loads(body))
        order_controller.order_processing_failed(message._id)
        ch.basic_publish(exchange = 'topic_order',
                         routing_key = 'order.order.canceled',
                         body = json.dumps(OrderCanceled.to_dict(OrderCanceled(message._id))),
                         properties = pika.BasicProperties(
                            delivery_mode = 2, # make message persistent
                         ))
    elif 'billing.order.reserved' == method.routing_key:
        message = BillingOrderReserved.from_dict(json.loads(body))
        if not order_controller.order_processing_succeed(message._id):
            order_controller.order_processing_failed(message._id)
            ch.basic_publish(exchange = 'topic_order',
                             routing_key = 'order.order.canceled',
                             body = json.dumps(OrderCanceled.to_dict(OrderCanceled(message._id))),
                             properties = pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                             ))

connection = pika.BlockingConnection(pika.URLParameters(config['MESSAGE_BROKER_URI']))
channel = connection.channel()
channel.exchange_declare(exchange='topic_order', exchange_type='topic')
result = channel.queue_declare('order', durable=True)
for binding_key in ['warehouse.order.not_reserved', 'billing.order.reserved']:
    channel.queue_bind(exchange='topic_order', queue=result.method.queue, routing_key=binding_key)
channel.basic_consume(queue=result.method.queue, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
