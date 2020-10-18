from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from django.utils.dateparse import parse_date


def date_str_to_timestamp(date_str: Optional[str]) -> Optional[int]:
    if not date_str:
        return None
    date_obj = parse_date(date_str)
    return date_to_timestamp(date_obj)


def date_to_timestamp(date_obj: Optional[date]) -> Optional[int]:
    if not date_obj:
        return None
    datetime_obj = datetime(year=date_obj.year, month=date_obj.month, day=date_obj.day)
    return int(datetime_obj.timestamp())


def round_currency(amount: Decimal) -> Decimal:
    """
    Round the amount to a human readable number of decimal places
    """

    if amount > 1000:
        return amount.quantize(Decimal('1.'))
    elif amount > 1:
        return amount.quantize(Decimal('.01'))
    else:
        return amount.quantize(Decimal('.0001'))
