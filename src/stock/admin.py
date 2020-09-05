from django.contrib import admin

from stock.models import Stock, StockPrice


class StockPriceInline(admin.TabularInline):
    model = StockPrice


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'ticker', 'name', 'price')
    inlines = (StockPriceInline,)
