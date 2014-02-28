from smartmin.views import *
from .models import *
from landmarks.widgets import CoordinatesPickerField
from django.core.urlresolvers import reverse

class LandmarkForm(forms.ModelForm):
    coordinates = CoordinatesPickerField(required=True)    

    def clean(self):

        clean = self.cleaned_data;
        if 'coordinates' in clean and self.instance:
            self.instance.lat = clean['coordinates']['lat']
            self.instance.lng = clean['coordinates']['lng']

        return clean

    class Meta:
        model = Landmark
        fields = ('official_name', 'unofficial_name', 'landmark_type', 'coordinates')

class LandmarkTypeCRUDL(SmartCRUDL):
    model = LandmarkType
    actions = ('create', 'list', 'update')
    permissions = True

    class Create(SmartCreateView):
        fields = ('name',)

class LandmarkCRUDL(SmartCRUDL):
    model = Landmark
    actions = ('create', 'list', 'update')
    permissions = True

    class Create(SmartCreateView):
        form_class = LandmarkForm
        fields = ('official_name', 'unofficial_name', 'landmark_type', 'coordinates')

        def pre_save(self, obj):
            obj = super(LandmarkCRUDL.Create, self).pre_save(obj)
            self.request.session['landmarks'] = Landmark.objects.all()
            return obj

        def get_success_url(self):
            return "%s?lat=%s&lng=%s" % (reverse('landmarks.landmark_create'), self.object.lat, self.object.lng)

    class List(SmartListView):
        fields = ('official_name', 'lat', 'lng', 'landmark_type')
