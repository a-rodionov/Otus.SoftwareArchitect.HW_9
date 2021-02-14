import copy
import datetime

class Goods:
    def __init__(self, goods_id, quantity):
        self._id = goods_id
        self._quantity = quantity

    @staticmethod
    def to_dict(goods):
        return {
            'goods_id': goods._id,
            'quantity': goods._quantity
        }

    @staticmethod
    def from_dict(goods_dict):
        return Goods(**goods_dict)

class OrderCreated:
    def __init__(self, id, user_account_id, total_price, goods, delivery_address, delivery_time):
        self._id = id
        self._user_account_id = user_account_id
        self._total_price = total_price
        self._goods = goods
        self._delivery_address = delivery_address
        self._delivery_time = delivery_time

    @staticmethod
    def to_dict(order_created):
        return {
            'id': order_created._id,
            'user_account_id': order_created._user_account_id,
            'total_price': order_created._total_price,
            'goods': [Goods.to_dict(g) for g in order_created._goods],
            'delivery_address': order_created._delivery_address,
            'delivery_time': order_created._delivery_time.strftime("%d/%m/%y %H:%M:%S"),
        }

    @staticmethod
    def from_dict(order_created_dict):
        dict_copy = copy.deepcopy(order_created_dict)
        goods = [Goods(**g) for g in dict_copy['goods']]
        dict_copy['goods'] = goods
        dict_copy['delivery_time'] = datetime.datetime.strptime(dict_copy['delivery_time'], '%d/%m/%y %H:%M:%S')
        return OrderCreated(**dict_copy)
