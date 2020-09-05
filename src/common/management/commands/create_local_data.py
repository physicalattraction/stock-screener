import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand, call_command
from django.utils import timezone

from currency.models import Currency, CurrencyExchangeRate
from stock.models import Stock, StockPrice

SEPT_4 = timezone.datetime(year=2020, month=9, day=4, tzinfo=timezone.utc)


class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.ENVIRONMENT != 'local':
            msg = 'Cannot create local data on a non-local environment'
            raise AssertionError(msg)

        if os.path.isfile(settings.DB_FILE):
            os.remove(settings.DB_FILE)

        call_command('migrate')
        if not User.objects.filter(is_staff=True).exists():
            User.objects.create_superuser(username='admin', email='admin@nyon.nl', password='admin')

        usd = Currency.objects.create(symbol='USD', name='US Dollar')
        CurrencyExchangeRate.objects.create(currency=usd, date=SEPT_4, rate=0.8463085212)

        mik = Stock.objects.create(symbol='MIK', name='The Michaels Company')
        StockPrice.objects.create(stock=mik, date=SEPT_4, open=10.43, high=10.79, low=9.96, close=10.50)
