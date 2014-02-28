from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from smartmin.models import SmartModel
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings

def comma_formatted(value, has_decimals):
    """
    Returns the passed in Decimal as a string, with the appropriate number of decimals
    and commas every three digits.
    """
    formatted = ""
    negative = False

    if value < 0:
        value = -value
        negative = True

    if has_decimals:
        decimal_portion = (value * 100) % 100
        formatted = ".%02d" % decimal_portion

    # now do the rest, 1000 at a time
    remainder = int(value)

    while remainder >= 1000:
        formatted = (",%03d" % (remainder % 1000)) + formatted
        remainder = remainder / 1000

    formatted = ("%d" % remainder) + formatted

    # deal with the negative case
    if negative:
        formatted = "-" + formatted
        
    return formatted

class Currency(SmartModel):
    name = models.CharField(max_length=64, unique=True,
                            help_text="The name of this currency, ie: US Dollars")
    currency_code = models.CharField(max_length=3, unique=True,
                                     help_text="The international currency code for this currency, ie: USD, RWF")
    abbreviation = models.CharField(max_length=4, unique=True,
                                    help_text="An abbreviated name for this currency, used in reports, ie: US$, RWF")
    has_decimals = models.BooleanField(default=False,
                                       help_text="Whether this currency has decimals, ie: cents in US dollars")
    prefix = models.CharField(default="", blank=True, max_length=4,
                              help_text="Any prefix to display before a value in this currency, ie: $")
    suffix = models.CharField(default="", blank=True, max_length=4,
                              help_text="Any suffix to display after a value in this currency, ie: RWF")    

    def format(self, value, force_even=False):
        """
        Formats the passed in value according to this currency's rules.
        """
        if value is None:
            return ""

        has_decimals = self.has_decimals and not force_even
        if has_decimals:
            value = Decimal(value).quantize(Decimal(".01"), ROUND_HALF_UP)
        else:
            value = Decimal(value).quantize(Decimal("1"), ROUND_HALF_UP)

        is_negative = value < Decimal("0")
        value = abs(value)

        formatted = self.prefix + comma_formatted(value, has_decimals) + self.suffix

        if is_negative:
            formatted = "-" + formatted

        return formatted

    def __unicode__(self):
        return self.name

    class Meta:
       verbose_name_plural = "Currencies"
       ordering = ('name',)       

class Country(SmartModel):
    name = models.CharField(max_length=64, unique=True,
                            help_text="The name of this country, ie: Rwanda")
    country_code = models.CharField(max_length=2, unique=True,
                                    help_text="The two letter country code, ie: US, RW")
    currency = models.ForeignKey(Currency, related_name="countries",
                                 help_text="The local currency in this country.")
    language = models.CharField(max_length=10, choices=settings.LANGUAGES,
                                help_text="The language used in this country, reports will also be offered in this language")
    calling_code = models.IntegerField(help_text="The country calling code for this country, leaving off the +, ie, 250 for Rwanda",
                                       validators = [MaxValueValidator(999)])
    phone_format = models.CharField(max_length=15, validators=[RegexValidator("[# -]+")],
                                     help_text="The format to use when displaying phone numbers, use # signs "
                                    "for numbers as well as spaces and dashes, ie: ### ### ## ##")
    national_id_format = models.CharField(max_length=35, validators=[RegexValidator("[# -]+")],
                                          help_text="The format to use when displaying national ids, use # signs for numbers, "
                                          "A for letters, as well as spaces and dashes, ie: # #### # ####### # ##")
    bounds_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    bounds_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True)

    bounds_zoom = models.IntegerField(default=8)

    def format_id(self, national_id):
        return format_string(self.national_id_format, national_id)        

    def format_phone(self, phone):
        return format_string(self.phone_format, phone)

    def derive_international_number(self, phone):
        """
        Prunes of the leading zero and prepends the country code
        """
        return "%s%s" % (self.calling_code, phone[1:])

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ('name',)

def format_string(format, value):
    python_format = ''
    for idx in range(len(format)):
        char = format[idx]
        if char == '#' or char == 'A':
            python_format += "%s"
        else:
            python_format += char

    # we now have something that looks like like this: %s%s%s%s%s %s%s%s %s%s %s%s
    # we just need to build an argument list to go with it
    try:
        arguments = [value[i] for i in range(len(value))]
        return python_format % tuple(arguments)
    except:
        return value
