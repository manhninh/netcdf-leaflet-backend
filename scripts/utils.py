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
    with open(os.environ['CONFIGFILE'], 'r') as ymlfile:
	    cfg = yaml.safe_load(ymlfile)
        if 'workdir' in cfg['general']:
        workdir=cfg['general']['workdir']
        else:
            workdir='.'
	    return workdir, cfg

cfg=readConf()
geoserverURL=cfg['geoserver']['url']
frontendPath=cfg['frontend']['path']

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
