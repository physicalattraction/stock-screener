from datetime import date, timedelta
from typing import Optional

from django.core.management import BaseCommand

from common.utils import date_str_to_timestamp, date_to_timestamp
from stock.models import Stock
from yahoo.yahoo import YahooApi


class Command(BaseCommand):
    help = 'Fetch historical data for the given stock from Yahoo Finance'

    def handle(self, *args, **options):
        yahoo = YahooApi()
        symbols = options['symbols']
        force_update = options['force_update']
        start_str = options['start']
        end_str = options['end']

        for symbol in symbols:
            try:
                stock = Stock.objects.get(symbol=symbol)
            except Stock.DoesNotExist as e:
                msg = f'No stock with symbol {symbol} exists'
                raise Stock.DoesNotExist(msg) from e

            start, end = self._get_start_and_end(start_str, end_str, force_update, stock)

            yahoo.fetch_historical_data(stock, start, end)

    @staticmethod
    def _get_start_and_end(start_str, end_str, force_update, stock) -> (Optional[int], Optional[int]):
        if start_str:
            start = date_str_to_timestamp(start_str)
        else:
            start = None

        if end_str:
            end = date_str_to_timestamp(end_str)
        else:
            end = None

        if not start and not force_update:
            last_known_date = Command._get_date_of_latest_stock_price(stock)
            if last_known_date:
                start_date = last_known_date + timedelta(days=1)
                start = date_to_timestamp(start_date)

        return start, end

    @staticmethod
    def _get_date_of_latest_stock_price(stock) -> Optional[date]:
        last_price = stock.prices.order_by('date').last()
        if last_price:
            return last_price.date
        else:
            return None

    def add_arguments(self, parser):
        help_symbols = 'Space separated list of symbols to fetch data for.'
        parser.add_argument('symbols', type=str, nargs='+', help=help_symbols)

        help_force_update = 'Remove all existing stock prices before importing new ones.'
        parser.add_argument('--force-update', dest='force_update', action='store_true',
                            default=False, help=help_force_update)

        help_start = 'Start date in the format YYYY-MM-DD. Optional, if not given and force_update=False,' \
                     'the stock prices since the last known stock price is fetched, otherwise all stock' \
                     'prices from the beginning of time are fetched.'
        parser.add_argument('--start', type=str, default=None, help=help_start)

        help_end = 'End date in the format YYYY-MM-DD. Optional, if not given, all stock prices up to ' \
                   'today are fetched.'
        parser.add_argument('--end', type=str, default=None, help=help_end)
