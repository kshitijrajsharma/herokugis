from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from leaflet.admin import LeafletGeoAdmin
from .models import *
# Register your models here.
@admin.register(studyarea)
class studyareaadmin(LeafletGeoAdmin):
    list_display = ('name', 'objectid')
# @admin.register(raster)
# class rasateradmin(LeafletGeoAdmin):
#     pass
