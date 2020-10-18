from datetime import date, timedelta
from typing import Optional

from django.core.management import BaseCommand

from common.utils import date_str_to_timestamp, date_to_timestamp
from currency.models import Currency
from yahoo.yahoo import YahooApi


class Command(BaseCommand):
    help = 'Fetch historical data for the given currency from Yahoo Finance'

    def handle(self, *args, **options):
        yahoo = YahooApi()
        symbols = options['symbols']
        force_update = options['force_update']
        start_str = options['start']
        end_str = options['end']

        for symbol in symbols:
            try:
                currency = Currency.objects.get(symbol=symbol)
            except Currency.DoesNotExist as e:
                msg = f'No currency with symbol {symbol} exists'
                raise Currency.DoesNotExist(msg) from e

            start, end = self._get_start_and_end(start_str, end_str, force_update, currency)

            yahoo.fetch_historical_currency_data(currency, start, end)

    @staticmethod
    def _get_start_and_end(start_str: str, end_str: str, force_update: bool,
                           currency: Currency) -> (Optional[int], Optional[int]):
        if start_str:
            start = date_str_to_timestamp(start_str)
        else:
            start = None

        if end_str:
            end = date_str_to_timestamp(end_str)
        else:
            end = None

        if not start and not force_update:
            last_known_date = Command._get_date_of_latest_exchange_rate(currency)
            if last_known_date:
                start_date = last_known_date + timedelta(days=1)
                start = date_to_timestamp(start_date)

        return start, end

    @staticmethod
    def _get_date_of_latest_exchange_rate(currency: Currency) -> Optional[date]:
        last_rate = currency.rates.order_by('date').last()
        if last_rate:
            return last_rate.date
        else:
            return None

    def add_arguments(self, parser):
        help_symbols = 'Space separated list of symbols to fetch data for.'
        parser.add_argument('symbols', type=str, nargs='+', help=help_symbols)

        help_force_update = 'Remove all existing currency exchange rates before importing new ones.'
        parser.add_argument('--force-update', dest='force_update', action='store_true',
                            default=False, help=help_force_update)

        help_start = 'Start date in the format YYYY-MM-DD. Optional, if not given and force_update=False,' \
                     'the currency exchange rates since the last known rate is fetched, otherwise all ' \
                     'currency exchange rates from the beginning of time are fetched.'
        parser.add_argument('--start', type=str, default=None, help=help_start)

        help_end = 'End date in the format YYYY-MM-DD. Optional, if not given, all currency exchange rates up to ' \
                   'today are fetched.'
        parser.add_argument('--end', type=str, default=None, help=help_end)
