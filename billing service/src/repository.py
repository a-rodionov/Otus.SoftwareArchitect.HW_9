from sqlalchemy import create_engine

from order import OrderStatus, Order
from user_account import UserAccount

class BillingRepository:
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
                                                                 user_account_id,
                                                                 total_price)
                                             values(%s, %s, %s, %s)
                                             on conflict (id)
                                             do update set status = %s
                                             returning id''',
                                          order_dict['id'],
                                          order_dict['status'],
                                          order_dict['user_account_id'],
                                          order_dict['total_price'],
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
        else:
            return Order.from_dict(dict(row.items()))

    def save_user_account(self, user_account):
        self.lazy_init()
        if user_account._id == -1:
            result = self._connection.execute('''insert into user_accounts (username,
                                                                            password,
                                                                            first_name,
                                                                            last_name,
                                                                            email,
                                                                            phone,
                                                                            balance)
                                                 values(%s, %s, %s, %s, %s, %s, %s)
                                                 returning id''',
                                              user_account._username,
                                              user_account._password,
                                              user_account._first_name,
                                              user_account._last_name,
                                              user_account._email,
                                              user_account._phone,
                                              user_account._balance)
            user_account_id = result.scalar()
            if user_account_id is None:
                return False
            user_account._id = user_account_id
            return True
        else:
            result = self._connection.execute('''update user_accounts
                                                     set username = %s,
                                                         password = %s,
                                                         first_name = %s,
                                                         last_name = %s,
                                                         email = %s,
                                                         phone = %s,
                                                         balance = %s
                                                 where id = %s
                                                 returning id''',
                                              user_account._username,
                                              user_account._password,
                                              user_account._first_name,
                                              user_account._last_name,
                                              user_account._email,
                                              user_account._phone,
                                              user_account._balance,
                                              user_account._id)
            user_account_id = result.scalar()
            if user_account_id is None:
                return False
            return True

    def get_user_account_by_id(self, user_account_id):
        self.lazy_init()
        result = self._connection.execute('''select * from user_accounts where id = %s''', user_account_id)
        row = result.first()
        if row is None:
            return None
        else:
            return UserAccount.from_dict(dict(row.items()))
