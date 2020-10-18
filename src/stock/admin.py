from django.contrib import admin

from stock.models import Stock, StockPrice


class StockPriceInline(admin.TabularInline):
    model = StockPrice
    readonly_fields = ('date', 'open', 'close', 'high', 'low')
    extra = 0


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'ticker', 'name', 'currency', 'price', 'price_in_euro')
    inlines = (StockPriceInline,)
