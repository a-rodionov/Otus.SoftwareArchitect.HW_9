import copy
from enum import Enum

class OrderStatus(Enum):
    IN_PROGRESS = 1
    PROCESSED = 2
    REJECTED = 3

class Order:
    def __init__(self, id, status, user_account_id, total_price):
        self._id = id
        self._status = status
        self._user_account_id = user_account_id
        self._total_price = total_price

    @staticmethod
    def to_dict(order):
        return {
            'id': order._id,
            'status': order._status.value,
            'user_account_id': order._user_account_id,
            'total_price': order._total_price,
        }

    @staticmethod
    def from_dict(order_dict):
        dict_copy = copy.deepcopy(order_dict)
        dict_copy['status'] = OrderStatus(dict_copy['status'])
        return Order(**dict_copy)
