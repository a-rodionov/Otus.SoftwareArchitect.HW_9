from order import OrderStatus, Order
from repository import OrderRepository

class OrderController:

    def __init__(self, order_repository):
        self._order_repository = order_repository

    def create_order(self, order):
        return self._order_repository.save_order(order)

    def get_order(self, order_id):
        return self._order_repository.get_order_by_id(order_id)

    def order_processing_failed(self, order_id):
        saved_order = self._order_repository.get_order_by_id(order_id)
        if saved_order is None:
            return True
        saved_order._status = OrderStatus.REJECTED
        return self._order_repository.save_order(saved_order)

    def order_processing_succeed(self, order_id):
        saved_order = self._order_repository.get_order_by_id(order_id)
        if saved_order is None:
            return False
        if saved_order._status == OrderStatus.REJECTED:
            return False
        saved_order._status = OrderStatus.PROCESSED
        return self._order_repository.save_order(saved_order)
        
