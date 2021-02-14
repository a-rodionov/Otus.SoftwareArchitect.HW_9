from order import OrderStatus, Order
from courier import Courier
from repository import ShippingRepository

class ShippingController:

    def __init__(self, shipping_repository):
        self._shipping_repository = shipping_repository

    def add_courier(self):
        courier = Courier(-1)
        if self._shipping_repository.save_courier(courier):
            return courier._id
        else:
            return None

    def get_courier(self, courier_id):
        return self._shipping_repository.get_courier_by_id(courier_id)

    def cache_new_order(self, order_id, delivery_address, delivery_time):
        saved_order = self._shipping_repository.get_order_by_id(order_id)
        if saved_order:
            return True
        return self._shipping_repository.save_order(Order(order_id, OrderStatus.IN_PROGRESS, delivery_address, delivery_time))
        
    def get_order(self, order_id):
        return self._shipping_repository.get_order_by_id(order_id)

    def reserve_shipping(self, order_id):
        saved_order = self._shipping_repository.get_order_by_id(order_id)
        if saved_order is None:
            return False
        if saved_order._status == OrderStatus.REJECTED:
            return False
        elif saved_order._status == OrderStatus.PROCESSED:
            return True
        elif saved_order._status == OrderStatus.IN_PROGRESS:
            courier_ids = self._shipping_repository.get_courier_ids()
            for courier_id in courier_ids:
                courier = self._shipping_repository.get_courier_by_id(courier_id)
                if courier.reserve_shipping(saved_order):
                    saved_order._status = OrderStatus.PROCESSED
                    self._shipping_repository.save_order(saved_order)
                    self._shipping_repository.save_courier(courier)
                    return True
        return False

    def cancel_order(self, order_id):
        saved_order = self._shipping_repository.get_order_by_id(order_id)
        if saved_order is None:
            return True
        if saved_order._status == OrderStatus.IN_PROGRESS:
            saved_order._status = OrderStatus.REJECTED
            self._shipping_repository.save_order(saved_order)
            return True
        elif saved_order._status == OrderStatus.PROCESSED:
            courier = self._shipping_repository.get_courier_by_order_id(order_id)
            if courier:
                if courier.cancel_shipping(saved_order):
                    self._shipping_repository.save_courier(courier)
            saved_order._status = OrderStatus.REJECTED
            self._shipping_repository.save_order(saved_order)
        return True
