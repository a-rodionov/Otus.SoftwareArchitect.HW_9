class UserAccount:
    def __init__(self, id, username, password, first_name, last_name, email, phone, balance):
        self._id = id
        self._username = username
        self._password = password
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._phone = phone
        self._balance = balance

    @staticmethod
    def to_dict(user_account):
        return {
            'id': user_account._id,
            'username': user_account._username,
            'password': user_account._password,
            'first_name': user_account._first_name,
            'last_name': user_account._last_name,
            'email': user_account._email,
            'phone': user_account._phone,
            'balance': user_account._balance,
        }

    @staticmethod
    def from_dict(user_account_dict):
        return UserAccount(**user_account_dict)

    def deposit(self, amount):
        if amount < 0:
            return False
        self._balance += amount
        return True

    def pay_order(self, order):
        if self._balance < order._total_price:
            return False
        self._balance -= order._total_price
        return True

    def cancel_order(self, order):
        self._balance += order._total_price
        return True