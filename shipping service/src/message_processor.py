import os
import sys
import pika
import json
from messages.order_created import OrderCreated
from messages.order_canceled import OrderCanceled
from messages.warehouse_order_reserved import WarehouseOrderReserved
from messages.billing_order_not_reserved import BillingOrderNotReserved
from messages.shipping_order_reserved import ShippingOrderReserved
from messages.shipping_order_not_reserved import ShippingOrderNotReserved
from repository import ShippingRepository
from controller import ShippingController
from courier import Courier
from order import OrderStatus, Order

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
    'MESSAGE_BROKER_URI': os.environ.get('MESSAGE_BROKER_URI', ''),
}

shipping_controller = ShippingController(ShippingRepository(config['DATABASE_URI']))

def callback(ch, method, properties, body):
    if 'order.order.created' == method.routing_key:
        message = OrderCreated.from_dict(json.loads(body))
        if not shipping_controller.cache_new_order(message._id,
                                                   message._delivery_address,
                                                   message._delivery_time):
            ch.basic_publish(exchange = 'topic_order',
                             routing_key = 'shipping.order.not_reserved',
                             body = json.dumps(ShippingOrderNotReserved.to_dict(ShippingOrderNotReserved(message._id))),
                             properties = pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                             ))
    elif 'order.order.canceled' == method.routing_key:
        message = OrderCanceled.from_dict(json.loads(body))
        shipping_controller.cancel_order(message._id)
    elif 'warehouse.order.reserved' == method.routing_key:
        message = WarehouseOrderReserved.from_dict(json.loads(body))
        if shipping_controller.reserve_shipping(message._id):
            ch.basic_publish(exchange = 'topic_order',
                             routing_key = 'shipping.order.reserved',
                             body = json.dumps(ShippingOrderReserved.to_dict(ShippingOrderReserved(message._id))),
                             properties = pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                             ))
        else:               
            ch.basic_publish(exchange = 'topic_order',
                             routing_key = 'shipping.order.not_reserved',
                             body = json.dumps(ShippingOrderNotReserved.to_dict(ShippingOrderNotReserved(message._id))),
                             properties = pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                             ))
    elif 'billing.order.not_reserved' == method.routing_key:
        message = BillingOrderNotReserved.from_dict(json.loads(body))
        shipping_controller.cancel_order(message._id)
        ch.basic_publish(exchange = 'topic_order',
                         routing_key = 'shipping.order.not_reserved',
                         body = json.dumps(ShippingOrderNotReserved.to_dict(ShippingOrderNotReserved(message._id))),
                         properties = pika.BasicProperties(
                            delivery_mode = 2, # make message persistent
                         ))

connection = pika.BlockingConnection(pika.URLParameters(config['MESSAGE_BROKER_URI']))
channel = connection.channel()
channel.exchange_declare(exchange='topic_order', exchange_type='topic')
result = channel.queue_declare('shipping', durable=True)
for binding_key in ['order.order.*', 'warehouse.order.reserved', 'billing.order.not_reserved']:
    channel.queue_bind(exchange='topic_order', queue=result.method.queue, routing_key=binding_key)
channel.basic_consume(queue=result.method.queue, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
