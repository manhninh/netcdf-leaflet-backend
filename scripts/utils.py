#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#=======================================================================
# name: utils.py
#
# category: python script
# Part 1
# description:
#   General methods used in main scripts
#
# author: Elias Borngässer
#=======================================================================


import math,yaml,os,sys,shutil
from urllib.request import urlopen
from affine import Affine
from geoserver.catalog import Catalog


def readConf():
    import yaml
    with open(sys.path[0] + "/conf/config.yml", 'r') as ymlfile:
	    cfg = yaml.safe_load(ymlfile)
	    return cfg

cfg=readConf()
geoserverURL=cfg['geoserver']['url']
frontendPath=cfg['frontend']['absolutePath']

def cleanupProjects(ignore):
    cat=Catalog(geoserverURL+ "/rest/", "admin", "geoserver")
    workspaces=cat.get_workspaces()
    projects=[]
    for _r, dirs, _f in os.walk(frontendPath+'/projects/'):
        for d in dirs:
            if d not in workspaces and d not in ignore:
                shutil.rmtree(frontendPath+'/projects/'+d)
            else:
                projects.append(d)
    return projects


def addGridMappingVars(var,grid_mapping,locationLat,locationLon,rotation):
    if grid_mapping=='transverse_mercator':
	    var.scale_factor_at_central_meridian = 0.9996
	    var.longitude_of_central_meridian = 15.
	    var.latitude_of_projection_origin = 0.
	    var.false_easting = 500000.
	    var.false_northing = 0.
	    var.grid_mapping_name = "transverse_mercator"
	    var.utm_zone_number = 33
	    var.inverse_flattening = 298.257222101
	    var.semi_major_axis = 6378137. 
	    var.proj4 = "+proj=utm +zone=33 +datum=WGS84 +units=m +no_defs +ellps=WGS84 +towgs84=0,0,0"


    elif grid_mapping=="mercator2":
        var.grid_mapping_name= grid_mapping
        affine=Affine.rotation(58) #(58*math.pi)/180
        elt_0_0=str(affine.a)
        elt_0_1=str(affine.b)
        elt_0_2=str(posX)
        elt_1_0=str(affine.d)
        elt_1_1=str(affine.e)
        elt_1_2=str(posY)
        # elt_0_0=str(math.cos(58*math.pi)/180)
        # elt_0_1=str(math.sin(58*math.pi)/180)
        # elt_0_2=str(affine.c) #918079.626281209)#0.0) #446044.8576076973
        # elt_1_0=str(-math.sin(58*math.pi)/180)
        # elt_1_1=str(math.cos(58*math.pi)/180)
        # elt_1_2=str(affine.f) #6445039.217828758) #5538108.209966961


        var.longitude_of_central_meridian= 0.0
        var.latitude_of_projection_origin= 0.0 
        var.standard_parallel= 0.0
        var._CoordinateTransformType= "Projection"
        var._CoordinateAxisTypes= "GeoX GeoY"
        #var.spatial_ref='PROJCS["WGS84 / Google Mercator", GEOGCS["WGS 84", DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], UNIT["degree", 0.017453292519943295], AXIS["Longitude", EAST], AXIS["Latitude", NORTH], AUTHORITY["EPSG","4326"]], PROJECTION["Mercator_1SP"], PARAMETER["semi_minor", 6378137.0], PARAMETER["latitude_of_origin", 0.0], PARAMETER["central_meridian", 0.0], PARAMETER["scale_factor", 1.0], PARAMETER["false_easting", 0.0], PARAMETER["false_northing", 0.0], UNIT["m", 1.0], AXIS["x", EAST], AXIS["y", NORTH], AUTHORITY["EPSG","900913"]]'
        var.spatial_ref= 'FITTED_CS["BPAF", PARAM_MT["Affine", PARAMETER["num_row", 3], PARAMETER["num_col", 3], PARAMETER["elt_0_0",'+elt_0_0+'], PARAMETER["elt_0_1", '+elt_0_1+'], PARAMETER["elt_0_2", '+elt_0_2+'], PARAMETER["elt_1_0", '+elt_1_0+'], PARAMETER["elt_1_1", '+elt_1_1+'], PARAMETER["elt_1_2", '+elt_1_2+']], PROJCS["WGS84 / Google Mercator", GEOGCS["WGS 84", DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], UNIT["degree", 0.017453292519943295], AXIS["Longitude", EAST], AXIS["Latitude", NORTH], AUTHORITY["EPSG","4326"]], PROJECTION["Mercator_1SP"], PARAMETER["semi_minor", 6378137.0], PARAMETER["latitude_of_origin", 0.0], PARAMETER["central_meridian", 0.0], PARAMETER["scale_factor", 1.0], PARAMETER["false_easting", 0.0], PARAMETER["false_northing", 0.0], UNIT["m", 1.0], AXIS["x", EAST], AXIS["y", NORTH], AUTHORITY["EPSG","900913"]], AUTHORITY["EPSG","8011113"]]'
#         var.spatial_ref= 'FITTED_CS["BPAF", PARAM_MT["Affine", PARAMETER["num_row", 3], PARAMETER["num_col", 3], PARAMETER["elt_0_0",'+elt_0_0+'], PARAMETER["elt_0_1", '+elt_0_1+'], PARAMETER["elt_0_2", '+elt_0_2+'], PARAMETER["elt_1_0", '+elt_1_0+'], PARAMETER["elt_1_1", '+elt_1_1+'], PARAMETER["elt_1_2", '+elt_1_2+']], PROJCS["transverse_mercator", \
#   GEOGCS["unknown", \
#     DATUM["unknown", \
#       SPHEROID["unknown", 6378137.0, 298.252840776245]], \
#     PRIMEM["Greenwich", 0.0], \
#     UNIT["degree", 0.017453292519943295], \
#     AXIS["Geodetic longitude", EAST], \
#     AXIS["Geodetic latitude", NORTH]], \
#   PROJECTION["Transverse_Mercator"], \
#   PARAMETER["central_meridian", 9.0], \
#   PARAMETER["latitude_of_origin", 0.0], \
#   PARAMETER["scale_factor", 0.9995999932289124], \
#   PARAMETER["false_easting", 500000.0], \
#   PARAMETER["false_northing", 0.0], \
#   UNIT["m", 1.0], \
#   AXIS["Easting", EAST], \
#   AXIS["Northing", NORTH],\
#   AUTHORITY["EPSG","32632"]],\
#   AUTHORITY["EPSG","8011113"]]'
        #print (var.spatial_ref)
    elif grid_mapping=="mercator":
        var.grid_mapping_name= grid_mapping

        var.longitude_of_central_meridian= 0.0
        var.latitude_of_projection_origin= 0.0 
        var.standard_parallel= 0.0
        var._CoordinateTransformType= "Projection"
        var._CoordinateAxisTypes= "GeoX GeoY"
        var.spatial_ref= 'PROJCS["Hotine_Oblique_Mercator_Azimuth_Center",GEOGCS["GCS_WGS_1984",DATUM["D_unknown",SPHEROID["WGS84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Hotine_Oblique_Mercator_Azimuth_Center"],PARAMETER["latitude_of_center",'+str(locationLat)+'],PARAMETER["longitude_of_center",'+str(locationLon)+'],PARAMETER["rectified_grid_angle",'+str(-rotation)+'],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["m",1.0], AUTHORITY["EPSG","8011112"]]'
    elif grid_mapping=="rotated_latitude_longitude":
        var.grid_mapping_name= grid_mapping
        var._CoordinateTransformType= "Projection"
        var._CoordinateAxisTypes= "GeoX GeoY"
        var.grid_north_pole_latitude = 37.0
        var.grid_north_pole_longitude = -153.0

    return var
