from django.contrib import admin

from currency.models import Currency, CurrencyExchangeRate


class CurrencyExchangeRateInline(admin.TabularInline):
    model = CurrencyExchangeRate
    readonly_fields = ('date', 'rate')
    extra = 0


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'rate', 'latest_rate_date')
    readonly_fields = ('symbol', 'name', 'rate')
    inlines = (CurrencyExchangeRateInline,)
