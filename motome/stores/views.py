from .models import *
from smartmin.views import *
from locales.widgets import CoordinatesPickerField

class StoreForm(forms.ModelForm):
    coordinates = CoordinatesPickerField(required=True)    

    def clean(self):
        clean = self.cleaned_data;
        if 'coordinates' in clean:
            self.instance.lat = clean['coordinates']['lat']
            self.instance.lng = clean['coordinates']['lng']

        return clean

    class Meta:
        model = Store
        fields = ('name', 'description', 'country', 'logo', 'splash', 'coordinates')

class StoreCRUDL(SmartCRUDL):
    model = Store
    actions = ('create','update', 'list')

    class List(SmartListView):
        fields = ('name', 'created_by', 'created_on')

    class Create(SmartCreateView):
        fields = ('country', 'name', 'description', 'logo', 'splash')
        success_url = 'id@stores.store_update'

    class Update(SmartUpdateView):
        form_class = StoreForm
        fields = ('country', 'name', 'description', 'logo', 'splash', 'coordinates')

        def derive_initial(self):
            if self.object.lat and self.object.lng:
                return dict(coordinates=(dict(lat=self.object.lat, lng=self.object.lng)))

        def get_context_data(self, **kwargs):
            context = super(StoreCRUDL.Update, self).get_context_data(**kwargs)
            context['display_fields'] = ['name', 'country']

            # add our country and it's root locations
            context['country'] = self.object.country

            # set the country on our form's location picker
            self.form.fields['coordinates'].set_country(self.object.country)
            
            return context
