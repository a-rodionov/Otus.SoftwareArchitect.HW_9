import copy
import datetime
from enum import Enum

class OrderStatus(Enum):
    IN_PROGRESS = 1
    PROCESSED = 2
    REJECTED = 3

class Order:
    def __init__(self, id, status, delivery_address, delivery_time):
        self._id = id
        self._status = status
        self._delivery_address = delivery_address
        self._delivery_time = delivery_time

    @staticmethod
    def to_dict(order):
        return {
            'id': order._id,
            'status': order._status.value,
            'delivery_address': order._delivery_address,
            'delivery_time': order._delivery_time.strftime("%d/%m/%y %H:%M:%S"),
        }

    @staticmethod
    def from_dict(order_dict):
        dict_copy = copy.deepcopy(order_dict)
        dict_copy['status'] = OrderStatus(dict_copy['status'])
        dict_copy['delivery_time'] = datetime.datetime.strptime(dict_copy['delivery_time'], '%d/%m/%y %H:%M:%S')
        return Order(**dict_copy)

