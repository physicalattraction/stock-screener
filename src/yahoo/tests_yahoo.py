from django.test import TestCase

from currency.models import Currency
from stock.models import Stock
from yahoo.yahoo import YahooApi


class YahooApiTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency = Currency.objects.create(symbol='USD', name='US dollar')
        cls.stock = Stock.objects.create(symbol='MIK', name='The Michaels Company', currency=cls.currency)

    def test_fetch_historical_currency_data(self):
        self.assertEqual(self.currency.rates.all().count(), 0)

        yahoo = YahooApi()
        yahoo.fetch_historical_currency_data(currency=self.currency, start=1571499338)

        self.assertGreaterEqual(self.currency.rates.all().count(), 1)


    def test_fetch_historical_stock_data(self):
        self.assertEqual(self.stock.prices.all().count(), 0)

        yahoo = YahooApi()
        yahoo.fetch_historical_stock_data(stock=self.stock, start=1571499338)

        self.assertGreaterEqual(self.stock.prices.all().count(), 1)
