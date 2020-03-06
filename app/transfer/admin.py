from django.contrib import admin

from .models import MoneyConversion, MoneyTransfer, Wallet


@admin.register(MoneyConversion)
class MoneyConversionAdmin(admin.ModelAdmin):
    pass


@admin.register(MoneyTransfer)
class MoneyTransferAdmin(admin.ModelAdmin):
    pass


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    pass
