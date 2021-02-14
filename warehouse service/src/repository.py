import copy
from sqlalchemy import create_engine

from goods import Goods
from order import OrderStatus, Order

class WarehouseRepository:
    def __init__(self, db_uri):
        self._db_uri = db_uri
        self._engine = None
        self._connection = None

    def lazy_init(self):
        if self._connection is None:
            self._engine = create_engine(self._db_uri)
            self._connection = self._engine.connect()

    def save_goods(self, goods):
        self.lazy_init()
        result = self._connection.execute('''insert into warehouse (goods_id,
                                                                    quantity)
                                             values(%s, %s)
                                             on conflict (goods_id)
                                             do update set quantity = %s
                                             returning goods_id''',
                                          goods._id,
                                          goods._quantity,
                                          goods._quantity)
        goods_id = result.scalar()
        if goods_id is None:
            return False
        return True

    def get_goods_by_id(self, goods_id):
        self.lazy_init()
        result = self._connection.execute('''select *
                                             from warehouse
                                             where goods_id = %s''',
                                          goods_id)
        row = result.first()
        if row is None:
            return None
        return Goods.from_dict(dict(row.items()))

    def get_order_by_id(self, order_id):
        self.lazy_init()
        result = self._connection.execute('''select id as order_id,
                                                    status
                                             from orders where id = %s''',
                                          order_id)
        row = result.first()
        if row is None:
            return None
        else:
            order_dict = dict(row.items())
            result = self._connection.execute('''select goods_id,
                                                        goods_quantity as quantity
                                                 from order_goods
                                                 where order_id = %s''',
                                              order_id)
            order_dict['goods'] = [dict(r.items()) for r in result]
            return Order.from_dict(order_dict)

    def save_order(self, order):
        self.lazy_init()
        result = self._connection.execute('''insert into orders (id,
                                                                 status)
                                             values(%s, %s)
                                             on conflict (id)
                                             do update set status = %s
                                             returning id''',
                                          order._id,
                                          order._status.value,
                                          order._status.value)
        order_id = result.scalar()
        if order_id is None:
            return False
        self._connection.execute('''delete from order_goods where order_id = %s''', order_id)
        for goods in order._goods:
            result = self._connection.execute('''insert into order_goods (order_id,
                                                                          goods_id,
                                                                          goods_quantity)
                                                 values(%s, %s, %s)
                                                 returning goods_id''',
                                              order_id,
                                              goods._id,
                                              goods._quantity)
            goods_id = result.scalar()
            if goods_id is None:
                return False
        return True