from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse

from rasterstats import zonal_stats
import geojson,gdal,subprocess
import os.path,os,json


def homepage(request):
    template_name= 'home.html'
    remove() 
    return render(request,template_name)

def receivedata(request):
    if request.method == 'GET':
        vector = request.GET['vector']
        remove()
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
        param = request.GET['parameter']
        stats = zonal_stats("data/destination_data.shp", 'data/elevation1proj.tif',stats=list(param.split(" ")),geojson_out=True)
        return HttpResponse(json.dumps(stats) )
    else:
        return HttpResponse("unsuccesful")

def remove():
    file_path="data/destination_data.shp"
    if os.path.exists(file_path):
        os.remove("data/destination_data.shp")
        os.remove("data/destination_data.shx")
        os.remove("data/destination_data.prj")
        os.remove("data/destination_data.dbf")
       

