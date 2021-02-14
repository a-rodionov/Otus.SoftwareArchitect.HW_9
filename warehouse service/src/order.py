import copy
from enum import Enum
from goods import Goods

class OrderStatus(Enum):
    IN_PROGRESS = 1
    PROCESSED = 2
    REJECTED = 3

class Order:
    def __init__(self, order_id, status, goods=[]):
        self._id = order_id
        self._status = status
        self._goods = goods

    @staticmethod
    def to_dict(order):
        return {
            'order_id': order._id,
            'status': order._status.value,
            'goods': [Goods.to_dict(g) for g in order._goods],
        }

    @staticmethod
    def from_dict(order_dict):
        dict_copy = copy.deepcopy(order_dict)
        goods = [Goods(**g) for g in dict_copy['goods']]
        dict_copy['goods'] = goods
        dict_copy['status'] = OrderStatus(dict_copy['status'])
        return Order(**dict_copy)