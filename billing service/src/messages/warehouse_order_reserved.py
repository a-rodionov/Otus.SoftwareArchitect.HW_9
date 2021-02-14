class WarehouseOrderReserved:
    def __init__(self, id):
        self._id = id

    @staticmethod
    def to_dict(warehouse_order_reserved):
        return {
            'id': warehouse_order_reserved._id,
        }

    @staticmethod
    def from_dict(warehouse_order_reserved_dict):
        return WarehouseOrderReserved(**warehouse_order_reserved_dict)
