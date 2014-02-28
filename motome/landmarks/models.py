from django.template.defaultfilters import slugify
from smartmin.models import SmartModel
from django.db import models

"""
Full description of the landmark type
"""
class LandmarkType(models.Model):
    name = models.CharField(max_length=128, help_text="Name describing the landmark type e.g. Popular name")
    slug = models.SlugField(unique=True)

    # automatically generate the slug from the landmark type name
    def save(self):
        super(LandmarkType, self).save()
        self.slug = slugify(self.name)
        super(LandmarkType, self).save()

    def __unicode__(self):
        return self.name

"""
Full description of the landmark
"""
class Landmark(SmartModel):
    official_name = models.CharField(max_length=64, null=True, blank=True, help_text="Official name for the landmark e.g. CHUK")
    unofficial_name = models.CharField(max_length=64, null=True, blank=True, help_text="Unofficial name for the landmark e.g. CHK")
    landmark_type = models.ForeignKey(LandmarkType, help_text="The type of the landmark e.g. Hospital")
    lat = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True, help_text="The latitude of the landmark")
    lng = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True, help_text="The longitude of the landmark")    

    def __unicode__(self):
        return self.official_name
