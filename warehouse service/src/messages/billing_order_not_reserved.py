class BillingOrderNotReserved:
    def __init__(self, id):
        self._id = id

    @staticmethod
    def to_dict(billing_order_not_reserved):
        return {
            'id': billing_order_not_reserved._id,
        }

    @staticmethod
    def from_dict(billing_order_not_reserved_dict):
        return BillingOrderNotReserved(**billing_order_not_reserved_dict)
