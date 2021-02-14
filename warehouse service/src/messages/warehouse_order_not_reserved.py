class WarehouseOrderNotReserved:
    def __init__(self, id):
        self._id = id

    @staticmethod
    def to_dict(warehouse_order_not_reserved):
        return {
            'id': warehouse_order_not_reserved._id,
        }

    @staticmethod
    def from_dict(warehouse_order_not_reserved_dict):
        return WarehouseOrderNotReserved(**warehouse_order_not_reserved_dict)
