import csv
import logging
from typing import Optional

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from common.external_api import BaseService
from stock.models import Stock, StockPrice

logger = logging.getLogger(__name__)


class YahooApi(BaseService):
    response_in_json = False
    base_url = 'https://query1.finance.yahoo.com'

    def fetch_historical_data(self, stock: Stock, start: Optional[int] = None, end: Optional[int] = None):
        """
        Fetch and store the historical price data for the given stock

        :param stock: Stock to fetch data for on Yahoo
        :param start: Unix timestamp of first data point. Optional, default = 0 (fetch all data)
        :param end: Unix timestamp of last data point. Optional, default = today
        """

        if not start:
            start = 0
        if not end:
            end = int(timezone.now().timestamp())
        if start > end:
            logger.debug(f'No stock prices to fetch for {stock.symbol}: '
                         f'start timestamp {start} is after end timestamp {end}')
            return

        url = f'{self.base_url}/v7/finance/download/{stock.symbol}'
        params = {
            'period1': start,
            'period2': end,
            'interval': '1d',
            'events': 'history'
        }
        response = self._make_get_call(url, params)
        self._parse_historical_data_response(stock, response)

    @staticmethod
    def _parse_historical_data_response(stock: Stock, text: str):
        """
        Create or update StockPrices for the given symbol from the input data

        :param stock: Stock to update the prices for
        :param text: Response from the Yahoo API to fetch historical data
        """

        text = text.strip()
        reader = csv.DictReader(text.split('\n'), delimiter=',')
        rows = [row for row in reader]
        logger.debug(f'Updating {len(rows)} for stock {stock}')
        with transaction.atomic():
            dates = {parse_date(row['Date']) for row in rows}
            StockPrice.objects.filter(stock=stock, date__in=dates).delete()
            stock_prices = [
                StockPrice(stock=stock, date=parse_date(row['Date']),
                           open=row['Open'], close=row['Close'], high=row['High'], low=row['Low'])
                for row in rows
                if 'null' not in row.values()
            ]

            StockPrice.objects.bulk_create(stock_prices)
