import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand, call_command
from django.utils import timezone

from currency.models import Currency
from stock.models import Stock


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

        today = timezone.now()
        start_date = today - timedelta(days=90)

        cad, gbx, hkd, jpy, sek, usd = self._create_currencies(start_date)
        self._create_stocks(cad, gbx, hkd, jpy, sek, start_date, usd)

    def _create_currencies(self, start_date):
        Currency.objects.create(symbol='EUR', name='Euro')
        cad = Currency.objects.create(symbol='CAD', name='Canadian dollar')
        gbx = Currency.objects.create(symbol='GBX', name='GB penny')
        gbp = Currency.objects.create(symbol='GBP', name='GB pound')
        hkd = Currency.objects.create(symbol='HKD', name='Hong Kong dollar')
        jpy = Currency.objects.create(symbol='JPY', name='Japanese yen')
        sek = Currency.objects.create(symbol='SEK', name='Swedish crown')
        usd = Currency.objects.create(symbol='USD', name='US dollar')
        currency_symbols = [currency.symbol for currency in {cad, gbx, gbp, hkd, jpy, sek, usd}]
        call_command('fetch_historical_currency_data', *currency_symbols, '--force-update', '--start',
                     start_date.strftime('%Y-%m-%d'))
        return cad, gbx, hkd, jpy, sek, usd

    def _create_stocks(self, cad, gbx, hkd, jpy, sek, start_date, usd):
        stocks = [
            Stock(symbol='MIK', name='The Michaels Company', currency=usd),
            Stock(symbol='DEDI.ST', name='Dedicare AB', currency=sek),
            Stock(symbol='CARD.L', name='Card Factory', currency=gbx),
            Stock(symbol='MOMO', name='Momo', currency=usd),
            Stock(symbol='1997.T', name='Akatsuki Eazima', currency=jpy),
            Stock(symbol='3932.T', name='Akatsuki', currency=jpy),
            Stock(symbol='1830.HK', name='Perfect Shape', currency=hkd),
            Stock(symbol='DR.TO', name='Medical Facilities Corporation', currency=cad),
            Stock(symbol='NHTC', name='Natural Health Trends Corp.', currency=usd),
            Stock(symbol='SCS.L', name='SCS Group', currency=gbx),
        ]
        Stock.objects.bulk_create(stocks)
        stock_symbols = [stock.symbol for stock in stocks]
        call_command('fetch_historical_stock_data', *stock_symbols, '--force-update', '--start',
                     start_date.strftime('%Y-%m-%d'))
