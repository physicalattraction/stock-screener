from django.test import TestCase

from currency.models import Currency
from stock.models import Stock
from yahoo.yahoo import YahooApi


class YahooApiTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency = Currency.objects.create(symbol='EUR', name='Euro')
        cls.stock = Stock.objects.create(symbol='MIK', name='The Michaels Company', currency=cls.currency)

    def test_fetch_historical_data(self):
        self.assertEqual(self.stock.prices.all().count(), 0)

        yahoo = YahooApi()
        yahoo.fetch_historical_data(stock=self.stock, start=1571499338)

        self.assertGreaterEqual(self.stock.prices.all().count(), 1)
