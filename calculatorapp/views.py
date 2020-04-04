from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from .models import Post, Like
from rasterstats import zonal_stats
import geojson,gdal,subprocess
import os.path,os


def homepage(request):
    template_name= 'home.html'
    return render(request,template_name)
def test(request):
    test= 'test.html'
    return render(request,test)
def receivedata(request):
    if request.method == 'GET':
        
        vector = request.GET['vector']
        file_path="data/destination_data.shp"
        if os.path.exists(file_path):
        # os.close(file_path)
            os.remove(file_path)
            os.remove("data/destination_data.shx")
            os.remove("data/destination_data.prj")
            os.remove("data/destination_data.dbf")
        data=geojson.loads(vector)
        with open('data.geojson', 'w')as f:
            geojson.dump(data,f)           
        args=['ogr2ogr','-f','ESRI Shapefile', "data/destination_data.shp",'data.geojson']
        subprocess.Popen(args)
        return HttpResponse('success' )
    else:
        return HttpResponse("unsuccesful")
def senddata(request):
    if request.method == 'GET':
        stats = zonal_stats("data/destination_data.shp", 'data/elevation1proj.tif',stats=['min', 'max','mean', 'median', 'majority', 'sum']) 
        return HttpResponse(str(stats) )
        
    else:
        return HttpResponse("unsuccesful")

    

