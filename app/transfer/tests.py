import json
from random import randrange

from django.contrib.auth.hashers import make_password
from django.test import TestCase

from django.contrib.auth.models import User

from .models import Wallet


class UserTestCase(TestCase):

    user_data_1 = {'username': 'user_name_1',
                   'password': '123-123-123',
                   'amount': 175}

    user_data_2 = {'username': 'user_name_2',
                   'password': '231-231-231',
                   'amount': 567}

    user_data_3 = {'username': 'user_name_3',
                   'password': '321-321-321',
                   'amount': 777}

    def setUp(self):
        self.user_1 = User.objects.create(
            username=self.user_data_1['username'],
            password=make_password(self.user_data_1['password'])
        )

        self.user_2 = User.objects.create(
            username=self.user_data_2['username'],
            password=make_password(self.user_data_2['password'])
        )

    def test_create_double_user(self):
        response = self.client.post('/signup/',
                                    json.dumps(self.user_data_2),
                                    content_type="application/json").json()

        self.assertFalse(response['success'])

    def test_create_user(self):
        response = self.client.post('/signup/',
                                    json.dumps(self.user_data_3),
                                    content_type="application/json").json()

        self.assertTrue(response['success'], "Can't create user")

    def test_login_user(self):
        response = self.client.post('/login/',
                                    json.dumps(self.user_data_2),
                                    content_type="application/json").json()

        self.assertTrue(response['success'], "Can't create user")

    def test_transfer(self):
        initial_balance = 350
        wallet_1 = Wallet.objects.create(user=self.user_1, balance=initial_balance)
        wallet_2 = Wallet.objects.create(user=self.user_2, balance=initial_balance)

        data = dict()
        data['sender'] = self.user_1.username
        data['receiver'] = self.user_2.username
        data['amount'] = get_random_amount()

        response = self.client.post('/login/',
                                    json.dumps(self.user_data_1),
                                    content_type="application/json").json()

        self.assertTrue(response['success'], "Can't login")

        response = self.client.post('/transfer/',
                                    json.dumps(data),
                                    content_type="application/json").json()

        self.assertTrue(response['success'], "Can't transfer")

        wallet_1_after = Wallet.objects.get(user=self.user_1)
        wallet_2_after = Wallet.objects.get(user=self.user_2)
        self.assertEqual(wallet_1_after.balance.amount, wallet_1.balance.amount - data['amount'])
        self.assertEqual(wallet_2_after.balance.amount, wallet_2.balance.amount + data['amount'])

    def test_transfer_insufficient_balance(self):
        initial_balance = 150
        Wallet.objects.create(user=self.user_1, balance=initial_balance)
        Wallet.objects.create(user=self.user_2, balance=initial_balance)

        data = dict()
        data['sender'] = self.user_1.username
        data['receiver'] = self.user_2.username
        data['amount'] = get_random_amount(more=initial_balance)

        response = self.client.post('/login/',
                                    json.dumps(self.user_data_1),
                                    content_type="application/json").json()

        self.assertTrue(response['success'], "Can't login")

        response = self.client.post('/transfer/',
                                    json.dumps(data),
                                    content_type="application/json").json()

        self.assertFalse(response['success'])


def get_random_amount(more=None):
    if more:
        return randrange(more + 1, more + 500)
    return randrange(1, 101)
