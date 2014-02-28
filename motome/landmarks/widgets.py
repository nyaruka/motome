from django import forms
import datetime
from django.utils.safestring import mark_safe
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape

class CoordinatesPickerWidget(forms.Widget):
    """
    A widget that provides both a way of picking a point on a map
    """
    def __init__(self, attrs=None):
        # needs to be set before we are rendered
        self.country = None
        super(CoordinatesPickerWidget, self).__init__(attrs)
    
    def render(self, name, value, attrs):
        html = ''
        
        val = value['lat'] if value else ''
        html += '<input type="text" name="coordinates_lat" id="lat" value="%s" style="width:150px;margin-right:10px;text-align:right">' % val

        val = value['lng'] if value else ''
        html += '<input type="text" name="coordinates_lng" id="lng" value="%s" style="width:150px;text-align:right">' % val

        return mark_safe(force_unicode(html))

    def value_from_datadict(self, data, files, name):
        lat = data.get('coordinates_lat')
        lng = data.get('coordinates_lng')

        if lat and lng:
            return dict(lat=lat, lng=lng)
        else:
            return None

    class Media:
       js = ('http://maps.google.com/maps/api/js?sensor=false', 'js/coordinates_picker.js')

class CoordinatesPickerField(forms.Field):
    widget = CoordinatesPickerWidget
