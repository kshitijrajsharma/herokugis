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

class Post(models.Model):
    post_heading= models.CharField(max_length=200)
    post_text=models.TextField()
    post_author= models.CharField(max_length= 100,default='default')

class Like(models.Model):
    post= models.ForeignKey(Post,on_delete = 'CASCADE')