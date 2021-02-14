import copy

class Courier:
    def __init__(self, id, orders=[]):
        self._id = id
        self._orders = orders

    #Резервируем 2 часа на выполнение заказа. Час до и час после назначенного времени
    def reserve_shipping(self, order):
        orders = [o for o in self._orders if abs((o._delivery_time - order._delivery_time).total_seconds()/60) < 120]
        if orders:
            return False
        self._orders.append(order)
        return True

    def cancel_shipping(self, order):
        original_orders_count = len(self._orders)
        self._orders = [o for o in self._orders if o._id != order._id]
        return original_orders_count != len(self._orders)

    def is_reserved_shipping(self, order):
        orders = [o for o in self._orders if o._id == order._id]
        if orders:
            return True
        return False

    @staticmethod
    def to_dict(courier):
        return {
            'id': courier._id,
            'orders': [{
                'order_id': o._id,
                } for o in courier._orders
            ]
        }

    @staticmethod
    def from_dict(courier_dict):
        courier_dict = copy.deepcopy(courier_dict)
        orders = [Order(**o) for o in order_dict['orders']]
        return Courier(courier_dict.get('courier_id'), orders)