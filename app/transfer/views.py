import json
from decimal import Decimal

import requests

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth.hashers import make_password

from .models import Wallet, MoneyTransfer, MoneyConversion


@csrf_exempt
def ajax_transfer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Need authenticate'})
    if request.method == 'POST':
        params = json.loads(request.body)

        if all([params['sender'], params['amount'], params['receiver']]):
            return make_transfer(params)

    return JsonResponse({'success': False})


@transaction.atomic
def make_transfer(params):
    sender_wallet = Wallet.objects.get(user__username=params['sender'])
    receiver_wallet = Wallet.objects.get(user__username=params['receiver'])
    amount = params['amount']

    if sender_wallet.balance.amount < params['amount']:
        return JsonResponse({'success': False,
                             'message': 'Insufficient money on balance'})

    # Need convert or not
    if sender_wallet.balance_currency != receiver_wallet.balance_currency:
        # Convert money
        exchange_rate = get_exchange_rate(sender_wallet.balance_currency,
                                          receiver_wallet.balance_currency)
        converted_amount = Decimal(amount * exchange_rate)
        converter = MoneyConversion.objects.create(initial_currency=sender_wallet.balance_currency,
                                                   initial_amount=amount,
                                                   exchange_rate=exchange_rate,
                                                   converted_currency=receiver_wallet.balance_currency,
                                                   converted_amount=converted_amount)
    else:
        converter = None
        converted_amount = amount

    # Decrease amount of sender
    sender_wallet.balance.amount -= amount
    sender_wallet.save()

    # Increase amount of receiver
    receiver_wallet.balance.amount += converted_amount
    receiver_wallet.save()

    # Write data about transfer to DB
    MoneyTransfer.objects.create(sender=sender_wallet,
                                 receiver=receiver_wallet,
                                 amount=amount,
                                 converter=converter)
    return JsonResponse({'success': True})


def get_exchange_rate(init_currency, result_currency):
    url = f"https://api.exchangeratesapi.io/latest?base={init_currency}"
    result_dict = requests.get(url).json()
    return result_dict['rates'][result_currency]


@csrf_exempt
def ajax_login(request):
    if request.method == 'POST':
        params = json.loads(request.body)
        username = params['username']
        password = params['password']
        if username and password:
            # Test username/password combination
            user = authenticate(username=username, password=password)
            # Found a match
            if user is not None:
                # User is active
                if user.is_active:
                    # Officially log the user in
                    login(request, user)
                    data = {'success': True}
                else:
                    data = {'success': False, 'error': 'User is not active'}
            else:
                data = {'success': False, 'error': 'Wrong username and/or password'}

            return JsonResponse(data)

    # Request method is not POST or one of username or password is missing
    return HttpResponseBadRequest()


@csrf_exempt
def ajax_signup(request):
    if request.method == 'POST':
        params = json.loads(request.body)
        username = params['username']
        password = params['password']
        if username and password:
            try:
                user = User.objects.create(username=username,
                                           password=make_password(password))
                login(request, user)
                data = {'success': True}
            except Exception as exc:
                data = {'success': False, 'message': str(exc)}
            return JsonResponse(data)

    # Request method is not POST or one of username or password is missing
    return HttpResponseBadRequest()
