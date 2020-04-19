from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from rasterio.plot import show_hist
from rasterstats import raster_stats
from osgeo import gdal
import geojson,subprocess
import os.path,os,json
import fiona
import rasterio
import rasterio.mask
import matplotlib
from matplotlib import pyplot as plt
# import geopandas as gpd



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
        maskraster()
        param = request.GET['parameter']
        stats = raster_stats("data/destination_data.shp", 'data/nepal250.tif',stats=list(param.split(" ")),interpolate='nearest',geojson_out=True)
        return HttpResponse(json.dumps(stats) )
    else:
        return HttpResponse("unsuccesful")
def maskraster():
    with fiona.open("data/destination_data.shp", "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]
    with rasterio.open("data/nepal250.tif") as src:
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
    with rasterio.open("data/RGB.byte.masked.tif", "w", **out_meta) as dest:
        dest.write(out_image)
def showhistogram(request):
    if request.method == 'GET':
        matplotlib.use('TkAgg')
        fp = r"data/RGB.byte.masked.tif"
        raster = rasterio.open(fp)
        show_hist(raster, bins=50, lw=0.0, stacked=False, alpha=0.3,histtype='stepfilled', title="Histogram")
        # .after(100, animate)
        # plt.plot()
        # plt.savefig('calculatorapp/Template/assets/img/histogram.png')
        return HttpResponse('successful' )
    else:
        return HttpResponse("unsuccesful")
    
def remove():
    file_path="data/destination_data.shp"
    file_raster="data/RGB.byte.masked.tif"
    # file_histogram="calculatorapp/Template/assets/img/histogram.png"
    if os.path.exists(file_path):
        os.remove("data/destination_data.shp")
        os.remove("data/destination_data.shx")
        os.remove("data/destination_data.prj")
        os.remove("data/destination_data.dbf")
    if os.path.exists(file_raster):
        os.remove("data/RGB.byte.masked.tif")
    # if os.path.exists(file_histogram):
    #     os.remove("calculatorapp/Template/assets/img/histogram.png")

        
        
       

