class OrderCanceled:
    def __init__(self, id):
        self._id = id

    @staticmethod
    def to_dict(order_canceled):
        return {
            'id': order_canceled._id,
        }

    @staticmethod
    def from_dict(order_canceled_dict):
        return OrderCanceled(**order_canceled_dict)
