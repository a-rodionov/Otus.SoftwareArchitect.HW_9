from sqlalchemy import create_engine

from order import OrderStatus, Order
from courier import Courier

class ShippingRepository:
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
        result = self._connection.execute('''insert into orders (id,
                                                                 status,
                                                                 delivery_address,
                                                                 delivery_time)
                                             values(%s, %s, %s, %s)
                                             on conflict (id)
                                             do update set status = %s
                                             returning id''',
                                          order_dict['id'],
                                          order_dict['status'],
                                          order_dict['delivery_address'],
                                          order_dict['delivery_time'],
                                          order_dict['status'])
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
        order_dict = dict(row.items())
        return Order.from_dict(order_dict)

    def save_courier(self, courier):
        self.lazy_init()
        if courier._id == -1:
            result = self._connection.execute('''insert into couriers (id) values(DEFAULT) returning id''')
            courier_id = result.scalar()
            if courier_id is None:
                return False
            courier._id = courier_id
        else:
            self._connection.execute('''delete from reservations where courier_id = %s''', courier._id)
            for order in courier._orders:
                self._connection.execute('''insert into reservations (order_id,
                                                                      courier_id)
                                                         values(%s, %s)''',
                                         order._id,
                                         courier._id)
        return True

    def get_courier_ids(self):
        self.lazy_init()
        result = self._connection.execute('''select id from couriers''')
        return [dict(r.items())['id'] for r in result]

    def get_courier_by_order_id(self, order_id):
        self.lazy_init()
        result = self._connection.execute('''select courier_id from reservations where order_id = %s''', order_id)
        courier_id = result.scalar()
        if courier_id is None:
            return None
        return self.get_courier_by_id(courier_id)

    def get_courier_by_id(self, courier_id):
        self.lazy_init()
        result = self._connection.execute('''select * from couriers where id = %s''', courier_id)
        row = result.first()
        if row is None:
            return None
        else:
            courier_dict = dict(row.items())
            result = self._connection.execute('''select O.id,
                                                        O.status,
                                                        O.delivery_address,
                                                        O.delivery_time
                                                 from orders O
                                                 inner join reservations R
                                                 on O.id = R.order_id and
                                                    R.courier_id = %s''',
                                              courier_dict['id'])
            orders = []
            for row in result:
                order_dict = dict(row.items())
                orders.append(Order.from_dict(order_dict))
            return Courier(courier_dict['id'], orders)
