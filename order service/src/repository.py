from sqlalchemy import create_engine

from goods import Goods
from order import OrderStatus, Order

class OrderRepository:
    def __init__(self, db_uri):
        self._db_uri = db_uri
        self._engine = None
        self._connection = None

    def lazy_init(self):
        if self._connection is None:
            self._engine = create_engine(self._db_uri)
            self._connection = self._engine.connect()

    def save_order(self, order):
        self.lazy_init()
        order_dict = Order.to_dict(order)
        if order._id == -1:
            result = self._connection.execute('''insert into orders (status,
                                                                     user_account_id,
                                                                     total_price,
                                                                     delivery_address,
                                                                     delivery_time)
                                                 values(%s, %s, %s, %s, %s)
                                                 returning id''',
                                              order_dict['status'],
                                              order_dict['user_account_id'],
                                              order_dict['total_price'],
                                              order_dict['delivery_address'],
                                              order_dict['delivery_time'])
            order_id = result.scalar()
            if order_id is None:
                return False

            for goods in order._goods:
                goods_dict = Goods.to_dict(goods)
                result = self._connection.execute('''insert into order_goods (order_id,
                                                                              goods_id,
                                                                              goods_quantity)
                                                     values(%s, %s, %s)
                                                     returning goods_id''',
                                                  order_id,
                                                  goods_dict['goods_id'],
                                                  goods_dict['quantity'])
                goods_id = result.scalar()
                if goods_id is None:
                    return False
            order._id = order_id
            return True
        else:
            result = self._connection.execute('''update orders set status = %s where id = %s returning id''',
                                              order_dict['status'],
                                              order_dict['id'])
            order_id = result.scalar()
            if order_id is None:
                return False
            return True


    def get_order_by_id(self, order_id):
        self.lazy_init()
        result = self._connection.execute('''select * from orders where id = %s''', order_id)
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
