class ShippingOrderReserved:
    def __init__(self, id):
        self._id = id

    @staticmethod
    def to_dict(shipping_order_reserved):
        return {
            'id': shipping_order_reserved._id,
        }

    @staticmethod
    def from_dict(shipping_order_reserved_dict):
        return ShippingOrderReserved(**shipping_order_reserved_dict)
