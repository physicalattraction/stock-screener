from datetime import date
from decimal import Decimal
from typing import Optional

from django.db import models


class Currency(models.Model):
    help_symbol = 'Symbol to look up the currency on e.g. Google'

    symbol = models.CharField(max_length=16, unique=True, help_text=help_symbol)
    name = models.CharField(max_length=64)

    rates: models.QuerySet['CurrencyExchangeRate']  # Dynamically added by class CurrencyExchangeRate

    class Meta:
        verbose_name_plural = 'currencies'
        ordering = ('symbol',)

    def __str__(self):
        return self.symbol

    @property
    def rate(self) -> Decimal:
        first_rate = self.rates.first()
        if first_rate:
            return first_rate.rate
        else:
            return Decimal(1)

    @property
    def latest_rate_date(self) -> Optional[date]:
        first_rate = self.rates.first()
        if first_rate:
            return first_rate.date
        else:
            return None


class CurrencyExchangeRate(models.Model):
    """
    Exchange rate of a currency to euros at a certain date
    """

    help_rate = 'Value of 1 unit of the currency in EUR'

    currency = models.ForeignKey(Currency, related_name='rates', on_delete=models.CASCADE)
    date = models.DateField()
    rate = models.DecimalField(max_digits=10, decimal_places=4, help_text=help_rate)

    class Meta:
        ordering = ('currency', '-date')
        unique_together = ('currency', 'date')

    def __str__(self):
        return f'{self.rate} ({self.date})'
