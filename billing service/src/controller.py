import os
import hashlib
from order import *
from user_account import UserAccount
from repository import BillingRepository

class BillingController:

    def __init__(self, billing_repository):
        self._billing_repository = billing_repository

    def add_new_user_account(self, username, password, firstName, lastName, email, phone):
        salt = os.urandom(32)
        user_account = UserAccount(-1,
                                   username,
                                   salt + hashlib.pbkdf2_hmac('sha256', password, salt, 100000, dklen=128),
                                   firstName,
                                   lastName,
                                   email,
                                   phone,
                                   0)
        if self._billing_repository.save_user_account(user_account):
            return user_account._id
        else:
            return None

    def get_user_account(self, user_account_id):
        return self._billing_repository.get_user_account_by_id(user_account_id)

    def deposit(self, user_account_id, amount):
        user_account = self._billing_repository.get_user_account_by_id(user_account_id)
        if user_account is None:
            return False
        if user_account.deposit(amount):
            self._billing_repository.save_user_account(user_account)
            return True
        return False

    def cache_new_order(self, order_id, user_account_id, total_price):
        order = self._billing_repository.get_order_by_id(order_id)
        if order:
            return True
        return self._billing_repository.save_order(Order(order_id, OrderStatus.IN_PROGRESS, user_account_id, total_price))
        
    def get_order(self, order_id):
        return self._billing_repository.get_order_by_id(order_id)
        
    def pay_order(self, order_id):
        saved_order = self._billing_repository.get_order_by_id(order_id)
        if saved_order is None:
            return False
        if saved_order._status == OrderStatus.REJECTED:
            return False
        elif saved_order._status == OrderStatus.PROCESSED:
            return True
        elif saved_order._status == OrderStatus.IN_PROGRESS:
            user_account = self._billing_repository.get_user_account_by_id(saved_order._user_account_id)
            if user_account:
                if user_account.pay_order(saved_order):
                    saved_order._status = OrderStatus.PROCESSED
                    self._billing_repository.save_order(saved_order)
                    self._billing_repository.save_user_account(user_account)
                    return True
                else:
                    saved_order._status = OrderStatus.REJECTED
                    self._billing_repository.save_order(saved_order)
                    return False
            else:
                saved_order._status = OrderStatus.REJECTED
                self._billing_repository.save_order(saved_order)
                return False
        else:
            return False

    def cancel_order(self, order_id):
        saved_order = self._billing_repository.get_order_by_id(order_id)
        if saved_order is None:
            return True
        if saved_order._status == OrderStatus.IN_PROGRESS:
            saved_order._status = OrderStatus.REJECTED
            self._billing_repository.save_order(saved_order)
            return True
        elif saved_order._status == OrderStatus.PROCESSED:
            saved_order._status = OrderStatus.REJECTED
            user_account = self._billing_repository.get_user_account_by_id(saved_order._user_account_id)
            if user_account:
                user_account.cancel_order(saved_order)
                self._billing_repository.save_user_account(user_account)
            self._billing_repository.save_order(saved_order)
        return True
