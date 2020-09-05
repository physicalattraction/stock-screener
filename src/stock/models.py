from decimal import Decimal

from django.db import models


class Stock(models.Model):
    help_symbol = 'Symbol to look up the stock on Yahoo finance'

    symbol = models.CharField(unique=True, max_length=16, help_text=help_symbol)
    ticker = models.CharField(max_length=32, blank=True, null=True)
    name = models.CharField(max_length=64)

    prices: models.QuerySet['StockPrice']

    class Meta:
        ordering = ('symbol',)

    @property
    def price(self) -> 'StockPrice':
        return self.prices.last()

    def __str__(self):
        return self.symbol


class StockPrice(models.Model):
    """
    Price of a stock at a certain date, in its original currency
    """

    stock = models.ForeignKey(Stock, related_name='prices', on_delete=models.CASCADE)
    date = models.DateField()
    open = models.DecimalField(max_digits=10, decimal_places=4)
    close = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    high = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    low = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    class Meta:
        ordering = ('stock', 'date')

    @property
    def current(self) -> Decimal:
        return self.close or self.open

    def __str__(self):
        return f'{self.current:0.2f} ({self.date})'
