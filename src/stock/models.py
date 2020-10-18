from decimal import Decimal
from typing import Optional

from django.db import models

from common.utils import round_currency
from currency.models import Currency


class Stock(models.Model):
    help_symbol = 'Symbol to look up the stock on Yahoo finance'

    symbol = models.CharField(unique=True, max_length=16, help_text=help_symbol)
    ticker = models.CharField(max_length=32, blank=True, null=True)
    name = models.CharField(max_length=64)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    prices: models.QuerySet['StockPrice']

    class Meta:
        ordering = ('symbol',)

    @property
    def price(self) -> Optional[Decimal]:
        first_price = self.prices.first()
        if first_price:
            return first_price.current
        else:
            return None

    @property
    def price_in_euro(self) -> Optional[Decimal]:
        price = self.price
        rate = self.currency.rate
        if price and rate:
            return round_currency(price * rate)
        else:
            return None

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
        ordering = ('stock', '-date')
        unique_together = ('stock', 'date')

    @property
    def current(self) -> Decimal:
        """
        Return the current price of the stock, properly rounded
        """

        current = self.close or self.open
        return round_currency(current)

    def __str__(self):
        return f'{self.current:0.2f} ({self.date})'
