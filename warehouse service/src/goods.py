class Goods:
    def __init__(self, goods_id, quantity):
        self._id = goods_id
        self._quantity = quantity

    def increase(self, quantity):
        self._quantity += quantity
        return True

    def decrease(self, quantity):
        if self._quantity < quantity:
            return False
        self._quantity -= quantity
        return True

    @staticmethod
    def to_dict(goods):
        return {
            'goods_id': goods._id,
            'quantity': goods._quantity
        }

    @staticmethod
    def from_dict(goods_dict):
        return Goods(**goods_dict)