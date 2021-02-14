from order import OrderStatus, Order
from goods import Goods
from repository import WarehouseRepository

class WarehouseController:

    def __init__(self, warehouse_repository):
        self._warehouse_repository = warehouse_repository

    def adjust_goods(self, adjusting_goods=[]):
        for adjusting_goods_itr in adjusting_goods:
            warehouse_goods = self._warehouse_repository.get_goods_by_id(adjusting_goods_itr._id)
            if warehouse_goods:
                warehouse_goods._quantity = adjusting_goods_itr._quantity
                self._warehouse_repository.save_goods(warehouse_goods)
            else:
                self._warehouse_repository.save_goods(adjusting_goods_itr)
        return True

    def cache_new_order(self, order):
        saved_order = self._warehouse_repository.get_order_by_id(order._id)
        if saved_order:
            return True
        return self._warehouse_repository.save_order(order)

    def get_order(self, order_id):
        return self._warehouse_repository.get_order_by_id(order_id)

    def reserve_goods(self, order_id):
        saved_order = self._warehouse_repository.get_order_by_id(order_id)
        if saved_order is None:
            return False
        if saved_order._status == OrderStatus.REJECTED:
            return False
        elif saved_order._status == OrderStatus.PROCESSED:
            return True
        elif saved_order._status == OrderStatus.IN_PROGRESS:
            goods = []
            for saved_order_goods in saved_order._goods:
                warehouse_goods = self._warehouse_repository.get_goods_by_id(saved_order_goods._id)
                if warehouse_goods:
                    if warehouse_goods.decrease(saved_order_goods._quantity):
                        goods.append(warehouse_goods)
                    else:
                        saved_order._status = OrderStatus.REJECTED
                        break
                else:
                    saved_order._status = OrderStatus.REJECTED
                    break

            if saved_order._status == OrderStatus.REJECTED:
                self._warehouse_repository.save_order(saved_order)
                return False
            saved_order._status = OrderStatus.PROCESSED
            self._warehouse_repository.save_order(saved_order)
            for modified_goods in goods:
                self._warehouse_repository.save_goods(modified_goods)
        return True

    def cancel_order(self, order_id):
        saved_order = self._warehouse_repository.get_order_by_id(order_id)
        if saved_order is None:
            return True
        if saved_order._status == OrderStatus.IN_PROGRESS:
            saved_order._status = OrderStatus.REJECTED
            self._warehouse_repository.save_order(saved_order)
            return True
        elif saved_order._status == OrderStatus.PROCESSED:
            for saved_order_goods in saved_order._goods:
                warehouse_goods = self._warehouse_repository.get_goods_by_id(saved_order_goods._id)
                warehouse_goods.increase(saved_order_goods._quantity)
                self._warehouse_repository.save_goods(warehouse_goods)
            saved_order._status = OrderStatus.REJECTED
            self._warehouse_repository.save_order(saved_order)
        return True
