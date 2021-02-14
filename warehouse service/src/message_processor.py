import os
import sys
import pika
import json
from messages.order_created import OrderCreated
from messages.order_canceled import OrderCanceled
from messages.warehouse_order_reserved import WarehouseOrderReserved
from messages.warehouse_order_not_reserved import WarehouseOrderNotReserved
from messages.shipping_order_not_reserved import ShippingOrderNotReserved
from repository import WarehouseRepository
from controller import WarehouseController
from goods import Goods
from order import OrderStatus, Order

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
    'MESSAGE_BROKER_URI': os.environ.get('MESSAGE_BROKER_URI', ''),
}

warehouse_controller = WarehouseController(WarehouseRepository(config['DATABASE_URI']))

def callback(ch, method, properties, body):
    if 'order.order.created' == method.routing_key:
        message = OrderCreated.from_dict(json.loads(body))
        if warehouse_controller.cache_new_order(Order(message._id,
                                                      OrderStatus.IN_PROGRESS,
                                                      message._goods)):
            if warehouse_controller.reserve_goods(message._id):
                ch.basic_publish(exchange = 'topic_order',
                                 routing_key = 'warehouse.order.reserved',
                                 body = json.dumps(WarehouseOrderReserved.to_dict(WarehouseOrderReserved(message._id))),
                                 properties = pika.BasicProperties(
                                    delivery_mode = 2, # make message persistent
                                 ))
            else:               
                ch.basic_publish(exchange = 'topic_order',
                                 routing_key = 'warehouse.order.not_reserved',
                                 body = json.dumps(WarehouseOrderNotReserved.to_dict(WarehouseOrderNotReserved(message._id))),
                                 properties = pika.BasicProperties(
                                    delivery_mode = 2, # make message persistent
                                 ))
        else:
            ch.basic_publish(exchange = 'topic_order',
                             routing_key = 'warehouse.order.not_reserved',
                             body = json.dumps(WarehouseOrderNotReserved.to_dict(WarehouseOrderNotReserved(message._id))),
                             properties = pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                             ))
    elif 'order.order.canceled' == method.routing_key:
        message = OrderCanceled.from_dict(json.loads(body))
        warehouse_controller.cancel_order(message._id)
    elif 'shipping.order.not_reserved' == method.routing_key:
        message = ShippingOrderNotReserved.from_dict(json.loads(body))
        warehouse_controller.cancel_order(message._id)
        ch.basic_publish(exchange = 'topic_order',
                         routing_key = 'warehouse.order.not_reserved',
                         body = json.dumps(WarehouseOrderNotReserved.to_dict(WarehouseOrderNotReserved(message._id))),
                         properties = pika.BasicProperties(
                            delivery_mode = 2, # make message persistent
                         ))

connection = pika.BlockingConnection(pika.URLParameters(config['MESSAGE_BROKER_URI']))
channel = connection.channel()
channel.exchange_declare(exchange='topic_order', exchange_type='topic')
result = channel.queue_declare('warehouse', durable=True)
for binding_key in ['order.order.*', 'shipping.order.not_reserved']:
    channel.queue_bind(exchange='topic_order', queue=result.method.queue, routing_key=binding_key)
channel.basic_consume(queue=result.method.queue, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
