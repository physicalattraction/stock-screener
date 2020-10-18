import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand, call_command
from django.utils import timezone

from currency.models import Currency, CurrencyExchangeRate
from stock.models import Stock

SEPT_4 = timezone.datetime(year=2020, month=9, day=4, tzinfo=timezone.utc)
OCT_18 = timezone.datetime(year=2020, month=10, day=18, tzinfo=timezone.utc)


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

        Currency.objects.create(symbol='EUR', name='Euro')
        cad = Currency.objects.create(symbol='CAD', name='Canadian dollar')
        gbx = Currency.objects.create(symbol='GBX', name='GB penny')
        hkd = Currency.objects.create(symbol='HKD', name='Hong Kong dollar')
        jpy = Currency.objects.create(symbol='JPY', name='Japanese yen')
        sek = Currency.objects.create(symbol='SEK', name='Swedish crown')
        usd = Currency.objects.create(symbol='USD', name='US dollar')
        Currency.objects.create(symbol='EUR', name='Euro')
        CurrencyExchangeRate.objects.create(currency=usd, date=SEPT_4, rate=0.8463)
        CurrencyExchangeRate.objects.create(currency=cad, date=OCT_18, rate=0.64719)
        CurrencyExchangeRate.objects.create(currency=gbx, date=OCT_18, rate=0.0110248)
        CurrencyExchangeRate.objects.create(currency=hkd, date=OCT_18, rate=0.110141)
        CurrencyExchangeRate.objects.create(currency=jpy, date=OCT_18, rate=0.008098)
        CurrencyExchangeRate.objects.create(currency=sek, date=OCT_18, rate=0.9635)
        CurrencyExchangeRate.objects.create(currency=usd, date=OCT_18, rate=0.8536)

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

        symbols = [stock.symbol for stock in stocks]
        today = timezone.now()
        start_date = today - timedelta(days=90)
        call_command('fetch_historical_data', *symbols, '--force-update', '--start',
                     start_date.strftime('%Y-%m-%d'))
