from django.db import models
from django.contrib.gis.db import models as geomodels
from raster import models as rastermodel
# Create your models here.
class studyarea(models.Model):
    objectid = models.BigIntegerField(blank=True,null=True)
    name = models.CharField(max_length=100,default='Null')
    geom = geomodels.MultiPolygonField(srid=4326)
    class Meta:
        verbose_name_plural = "studyarea"

