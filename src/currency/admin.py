from django.contrib import admin

from currency.models import Currency, CurrencyExchangeRate


class CurrencyExchangeRateInline(admin.TabularInline):
    model = CurrencyExchangeRate
    extra = 0


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'rate')
    inlines = (CurrencyExchangeRateInline,)
