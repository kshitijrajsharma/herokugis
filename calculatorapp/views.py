from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from rasterio.plot import show_hist
# from rasterstats import raster_stats
import geojson,subprocess
import os.path,os,json
import fiona
import rasterio
import rasterio.mask
import matplotlib
from matplotlib import pyplot as plt
# import gdal,ogr
from osgeo import gdal, ogr
from osgeo.gdalconst import *
import numpy as np
import sys
import json 
import shutil
import earthpy.plot as ep
# import geopandas as gpd



def homepage(request):
    template_name= 'home.html'
    remove() 
    return render(request,template_name)
def bbox_to_pixel_offsets(gt, bbox):
    originX = gt[0]
    originY = gt[3]
    pixel_width = gt[1]
    pixel_height = gt[5]
    x1 = int((bbox[0] - originX) / pixel_width)
    x2 = int((bbox[1] - originX) / pixel_width) + 1

    y1 = int((bbox[3] - originY) / pixel_height)
    y2 = int((bbox[2] - originY) / pixel_height) + 1

    xsize = x2 - x1
    ysize = y2 - y1
    return (x1, y1, xsize, ysize)
def zonal(vector_path, raster_path, nodata_value=None, global_src_extent=False,stats=None,geojson_out=False,**kwargs):
    rds = gdal.Open(raster_path, GA_ReadOnly)
    assert(rds)
    rb = rds.GetRasterBand(1)
    rgt = rds.GetGeoTransform()

    if nodata_value:
        nodata_value = float(nodata_value)
        rb.SetNoDataValue(nodata_value)

    vds = ogr.Open(vector_path, GA_ReadOnly)  # TODO maybe open update if we want to write stats
    assert(vds)
    vlyr = vds.GetLayer(0)

    # create an in-memory numpy array of the source raster data
    # covering the whole extent of the vector layer
    if global_src_extent:
        # use global source extent
        # useful only when disk IO or raster scanning inefficiencies are your limiting factor
        # advantage: reads raster data in one pass
        # disadvantage: large vector extents may have big memory requirements
        src_offset = bbox_to_pixel_offsets(rgt, vlyr.GetExtent())
        src_array = rb.ReadAsArray(*src_offset).astype(np.uintc)

        # calculate new geotransform of the layer subset
        new_gt = (
            (rgt[0] + (src_offset[0] * rgt[1])),
            rgt[1],
            0.0,
            (rgt[3] + (src_offset[1] * rgt[5])),
            0.0,
            rgt[5]
        )

    mem_drv = ogr.GetDriverByName('Memory')
    driver = gdal.GetDriverByName('MEM')

    # Loop through vectors
    stats = []
    feat = vlyr.GetNextFeature()
    while feat is not None:

        if not global_src_extent:
            
            src_offset = bbox_to_pixel_offsets(rgt, feat.geometry().GetEnvelope())
            src_array = rb.ReadAsArray(*src_offset).astype(np.uintc)
            new_gt = (
                (rgt[0] + (src_offset[0] * rgt[1])),
                rgt[1],
                0.0,
                (rgt[3] + (src_offset[1] * rgt[5])),
                0.0,
                rgt[5]
            )

        
        mem_ds = mem_drv.CreateDataSource('out')
        mem_layer = mem_ds.CreateLayer('poly', None, ogr.wkbPolygon)
        mem_layer.CreateFeature(feat.Clone())

        
        rvds = driver.Create('', src_offset[2], src_offset[3], 1, gdal.GDT_Byte)
        rvds.SetGeoTransform(new_gt)
        gdal.RasterizeLayer(rvds, [1], mem_layer, burn_values=[1])
        rv_array = rvds.ReadAsArray().astype(np.uintc)

        masked = np.ma.MaskedArray(
            src_array,
            mask=np.logical_or(
                src_array == nodata_value,
                np.logical_not(rv_array)
            )
        )

        feature_stats = {

            'min': int(np.amin(masked)),
            'mean': int(masked.mean(dtype=np.uint64)),
            'max': int(masked.max()),
            'std': int(masked.std()),
            'sum': int(masked.sum(dtype=np.uint64)),
            'count': int(masked.count()),
            'fid': int(feat.GetFID())}

        stats.append(feature_stats)
        
        rvds = None
        mem_ds = None
        feat = vlyr.GetNextFeature()

    vds = None
    rds = None
    
    return stats

def receivedata(request):
    if request.method == 'GET':
        vector = request.GET['vector']
        remove()
        data=geojson.loads(vector)
        with open('data/data.geojson', 'w')as f:
            geojson.dump(data,f)           
        args=['ogr2ogr','-f','ESRI Shapefile', "data/destination_data.shp",'data/data.geojson']
        subprocess.Popen(args)
        return HttpResponse('success' )
    else:

        return HttpResponse("unsuccesful")

def senddata(request):
    if request.method == 'GET':
        maskraster()
        param = request.GET['parameter']
        stats = zonal("data/destination_data.shp", 'data/nepal250.tif')
        with open("data/data.geojson", 'r') as f:
            data = json.load(f)
        if(param != "all"):
            i=0
            for feat in data['features']:
                dic=stats[i]
                feat['properties'][param]=dic[param]
                i=i+1
        else:
            i=0
            for feat in data['features']:
                for key, val in stats[i].items():
                    feat['properties'][key]=val
                i=i+1

        return HttpResponse(json.dumps(data) )
    else:
        remove()
        return HttpResponse("unsuccesful")
def maskraster():
    # file_raster="data/RGB.byte.masked.tif"
    # file_histogram="calculatorapp/Template/assets/img/histogram.png"
    # if os.path.exists(file_histogram):
    #     os.remove(file_histogram)
    # if os.path.exists(file_raster):
    #     os.remove(file_raster)
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
        param = request.GET['parameter']
        
        dem_path="data/RGB.byte.masked.tif"
        with rasterio.open(dem_path) as src:
            dem_in = src.read(1, masked=True)
        ep.hist(dem_in, colors=['purple'],
            title="Distribution of DEM Elevation Values",
            xlabel='Elevation (meters)',
            ylabel='Frequency')

        plt.savefig("calculatorapp/Template/assets/img/histogram"+param+".png")
        
    
        return HttpResponse('successful' )
    else:
        return HttpResponse("unsuccesful")  
def remove():
    file_path="data/destination_data.shp"
    file_raster="data/RGB.byte.masked.tif"
    file_histogram="calculatorapp/Template/assets/img"
    if os.path.exists(file_path):
        os.remove("data/destination_data.shp")
        os.remove("data/destination_data.shx")
        os.remove("data/destination_data.prj")
        os.remove("data/destination_data.dbf")
        os.remove("data/data.geojson")
    if os.path.exists(file_raster):
        os.remove("data/RGB.byte.masked.tif")
    if os.path.exists(file_histogram):
        folder = 'calculatorapp/Template/assets/img'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        
        
       

