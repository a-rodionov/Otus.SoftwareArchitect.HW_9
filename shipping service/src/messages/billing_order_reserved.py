class BillingOrderReserved:
    def __init__(self, id):
        self._id = id

    @staticmethod
    def to_dict(billing_order_reserved):
        return {
            'id': billing_order_reserved._id,
        }

    @staticmethod
    def from_dict(billing_order_reserved_dict):
        return BillingOrderReserved(**billing_order_reserved_dict)
