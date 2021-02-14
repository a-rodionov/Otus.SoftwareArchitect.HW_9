import copy
import datetime
from enum import Enum
from goods import Goods

class OrderStatus(Enum):
    IN_PROGRESS = 1
    PROCESSED = 2
    REJECTED = 3

class Order:
    def __init__(self, id, status, user_account_id, total_price, goods, delivery_address, delivery_time):
        self._id = id
        self._status = status
        self._user_account_id = user_account_id
        self._total_price = total_price
        self._goods = goods
        self._delivery_address = delivery_address
        self._delivery_time = delivery_time

    @staticmethod
    def to_dict(order):
        return {
            'id': order._id,
            'status': order._status.value,
            'user_account_id': order._user_account_id,
            'total_price': order._total_price,
            'goods': [Goods.to_dict(g) for g in order._goods],
            'delivery_address': order._delivery_address,
            'delivery_time': order._delivery_time.strftime("%d/%m/%y %H:%M:%S"),
        }

    @staticmethod
    def from_dict(order_dict):
        dict_copy = copy.deepcopy(order_dict)
        goods = [Goods(**g) for g in dict_copy['goods']]
        dict_copy['goods'] = goods
        dict_copy['status'] = OrderStatus(dict_copy['status'])
        dict_copy['delivery_time'] = datetime.datetime.strptime(dict_copy['delivery_time'], '%d/%m/%y %H:%M:%S')
        return Order(**dict_copy)
