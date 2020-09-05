from django.contrib import admin

from currency.models import Currency, CurrencyExchangeRate


class CurrencyExchangeRateInline(admin.TabularInline):
    model = CurrencyExchangeRate


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'rate')
    inlines = (CurrencyExchangeRateInline,)
