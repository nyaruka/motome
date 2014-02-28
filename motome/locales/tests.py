# -*- coding: utf-8 -*-
from .models import *
from decimal import Decimal
from templatetags.locales import *
from django.core.urlresolvers import reverse
from motome.tests import MotomeTestCase
import datetime

class FormatTest(MotomeTestCase):
    def test_formatted(self):
        self.assertEqual("1,000", comma_formatted(Decimal(1000), False))
        self.assertEqual("1,000.00", comma_formatted(Decimal(1000), True))
        self.assertEqual("1,010.20", comma_formatted(Decimal("1010.20"), True))
        self.assertEqual("1,010", comma_formatted(Decimal("1010"), False))

        self.assertEqual("-1,010", comma_formatted(Decimal("-1010"), False))

        self.assertEqual("-1,010,200", comma_formatted(Decimal("-1010200"), False))

        self.assertEqual("38.23", comma_formatted(Decimal("38.23"), True))

    def test_templatetags(self):
        self.assertEqual("333 333", format_string("### ###", "333333"))
        self.assertEqual("333-333", format_string("###-###", "333333"))

        # wrong number of args should back down to original format
        self.assertEqual("33333", format_string("###-###", "33333"))

        country = Country()
        country.phone_format = '#### ## ## ##'

        self.assertEquals("0788 38 33 83", format_phone('0788383383', country))
        self.assertEquals("078838338", format_phone('078838338', country))

        country.national_id_format = '#-####-#-#######-#-##'

        self.assertEquals("1-1984-8-0004007-0-52", format_id('1198480004007052', country))
        self.assertEquals("119844804007052", format_id('119844804007052', country))

        # this time is assumed to be in UTC
        time = datetime.datetime(day=23, month=6, year=1977, hour=10, minute=30, second=0)
        
        # but we want it displayed in the local timezone, CAT, which is +2
        self.assertEquals("Jun 23 1977, 12:30", local_timezone(time))

        # int formatting
        self.assertEquals("1,234", format_int(1234))
        self.assertEquals("1,234", format_int(Decimal("1234.00")))
        self.assertEquals("12.00.00", format_int("12.00.00"))

        # currency formatting
        self.assertEquals("$12.00", format_currency(Decimal("12"), self.usd))
        self.assertEquals("12.00.00", format_currency("12.00.00", self.usd))
