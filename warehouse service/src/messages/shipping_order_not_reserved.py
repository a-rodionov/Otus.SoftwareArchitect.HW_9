class ShippingOrderNotReserved:
    def __init__(self, id):
        self._id = id

    @staticmethod
    def to_dict(shipping_order_not_reserved):
        return {
            'id': shipping_order_not_reserved._id,
        }

    @staticmethod
    def from_dict(shipping_order_not_reserved_dict):
        return ShippingOrderNotReserved(**shipping_order_not_reserved_dict)
