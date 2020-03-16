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


import math,yaml,os,sys
from urllib.request import urlopen
from affine import Affine

def calculatePixelSize(latitude,pixelWidth,pixelHeight): #calculate Resolution in degrees when given resolution in meters
    r_earth = 6378.137  #radius of the earth in kilometer

    resX = (1/((2*math.pi/360) * r_earth * math.cos(latitude))) /1000* pixelWidth
    resY = (1 / ((2 * math.pi / 360) * r_earth)) / 1000 * pixelHeight#111 km / degree 
    return resX,resY

def readConf():
    import yaml
    with open(os.path.join(sys.path[0], "conf/config.yml"), 'r') as ymlfile:
	    cfg = yaml.safe_load(ymlfile)
	    return cfg

def addGridMappingVars(var,grid_mapping):
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


    elif grid_mapping=='albers_conical_equal_area':
	    var.grid_mapping_name = grid_mapping
	    var.false_easting = 1000000.
	    var.false_northing = 0.
	    var.latitude_of_projection_origin = 45.
	    var.longitude_of_central_meridian = -126.
	    var.standard_parallel = 50., 58.5
	    var.longitude_of_prime_meridian = 0.
	    var.semi_major_axis = 6378137.
	    var.inverse_flattening = 298.257222101 

    elif grid_mapping=='lambert_conformal_conic_1SP':
	    var.grid_mapping_name = grid_mapping
	    var.central_meridian= -95.0
	    var.latitude_of_origin= 25.0
	    var.scale_factor= 1.0
	    var.false_easting= 0.0
	    var.false_northing= 0.0
    elif grid_mapping=="Mercator_1SP":
	    var.grid_mapping_name = grid_mapping
	    var.central_meridian= 0.0
	    var.scale_factor= 1.0
	    var.false_easting= 0.0
	    var.false_northing= 0.0
    elif grid_mapping=="mercator":
        var.grid_mapping_name= grid_mapping
        affine=Affine.rotation(58.0)
        elt_0_0=str(math.cos(58*math.pi)/180)
        elt_0_1=str(math.sin(58*math.pi)/180)
        elt_0_2=str(918079.626281209) #918079.626281209)#0.0) #446044.8576076973
        elt_1_0=str(-math.sin(58*math.pi)/180)
        elt_1_1=str(math.cos(58*math.pi)/180)
        elt_1_2=str(6445039.217828758) #6445039.217828758) #5538108.209966961


        var.longitude_of_central_meridian= 0.0
        var.latitude_of_projection_origin= 0.0 
        var.standard_parallel= 0.0
        var._CoordinateTransformType= "Projection"
        var._CoordinateAxisTypes= "GeoX GeoY"
        var.spatial_ref='PROJCS["WGS84 / Google Mercator", GEOGCS["WGS 84", DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], UNIT["degree", 0.017453292519943295], AXIS["Longitude", EAST], AXIS["Latitude", NORTH], AUTHORITY["EPSG","4326"]], PROJECTION["Mercator_1SP"], PARAMETER["semi_minor", 6378137.0], PARAMETER["latitude_of_origin", 0.0], PARAMETER["central_meridian", 0.0], PARAMETER["scale_factor", 1.0], PARAMETER["false_easting", 0.0], PARAMETER["false_northing", 0.0], UNIT["m", 1.0], AXIS["x", EAST], AXIS["y", NORTH], AUTHORITY["EPSG","900913"]]'
        #var.spatial_ref= 'FITTED_CS["BPAF", PARAM_MT["Affine", PARAMETER["num_row", 3], PARAMETER["num_col", 3], PARAMETER["elt_0_0",'+elt_0_0+'], PARAMETER["elt_0_1", '+elt_0_1+'], PARAMETER["elt_0_2", '+elt_0_2+'], PARAMETER["elt_1_0", '+elt_1_0+'], PARAMETER["elt_1_1", '+elt_1_1+'], PARAMETER["elt_1_2", '+elt_1_2+']], PROJCS["WGS84 / Google Mercator", GEOGCS["WGS 84", DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], UNIT["degree", 0.017453292519943295], AXIS["Longitude", EAST], AXIS["Latitude", NORTH], AUTHORITY["EPSG","4326"]], PROJECTION["Mercator_1SP"], PARAMETER["semi_minor", 6378137.0], PARAMETER["latitude_of_origin", 0.0], PARAMETER["central_meridian", 0.0], PARAMETER["scale_factor", 1.0], PARAMETER["false_easting", 0.0], PARAMETER["false_northing", 0.0], UNIT["m", 1.0], AXIS["x", EAST], AXIS["y", NORTH], AUTHORITY["EPSG","900913"]], AUTHORITY["EPSG","8011113"]]'
        #var.spatial_ref= 'PARAM_MT["Affine", PARAMETER["num_row", 3], PARAMETER["num_col", 3], PARAMETER["elt_0_0",'+elt_0_0+'], PARAMETER["elt_0_1", '+elt_0_1+'], PARAMETER["elt_0_2", '+elt_0_2+'], PARAMETER["elt_1_0", '+elt_1_0+'], PARAMETER["elt_1_1", '+elt_1_1+'], PARAMETER["elt_1_2", '+elt_1_2+']]'
 
        return var
    elif grid_mapping=="mercator2":
        var.grid_mapping_name= grid_mapping

        var.longitude_of_central_meridian= 0.0
        var.latitude_of_projection_origin= 0.0 
        var.standard_parallel= 0.0
        var._CoordinateTransformType= "Projection"
        var._CoordinateAxisTypes= "GeoX GeoY"
        var.spatial_ref= 'PROJCS["Hotine_Oblique_Mercator_Azimuth_Center",GEOGCS["GCS_WGS_1984",DATUM["D_unknown",SPHEROID["WGS84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Hotine_Oblique_Mercator_Azimuth_Center"],PARAMETER["latitude_of_center",50.0],PARAMETER["longitude_of_center",8.25],PARAMETER["rectified_grid_angle",'+str(180-58)+'],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["m",1.0], AUTHORITY["EPSG","8011112"]]'
    elif grid_mapping=="rotated_latitude_longitude":
        var.grid_mapping_name= grid_mapping
        var._CoordinateTransformType= "Projection"
        var._CoordinateAxisTypes= "GeoX GeoY"
        var.grid_north_pole_latitude = 37.0
        var.grid_north_pole_longitude = -153.0
    elif grid_mapping=="oblique_stereographic":
        var.grid_mapping_name=grid_mapping
        var.projection_name = "Amersfoort / RD New"
        var.semi_major_axis = 6377397.
        var.inverse_flattening = 299.1528
        var.latitude_of_projection_origin = 52.15616
        var.longitude_of_central_meridian = 5.387639
        var.scale_factor_at_projection_origin = 0.9999079
        var.false_easting = 155000
        var.false_northing = 463000
        var.proj4_params = "+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.999908 +x_0=155000 +y_0=463000 +ellps=bessel +units=m +towgs84=565.4174,50.3319,465.5542,-0.398957388243134,0.343987817378283,-1.87740163998045,4.0725 +no_defs"
        var.EPSG_code = "EPSG:28992"

    elif grid_mapping=="polar_sterepographic":
        var.latitude_of_projection_origin = 90.0
        var.false_northing = 0.0
        var.straight_vertical_longitude_from_pole = -135.0
        var.false_easting = 0.0
        var.scale_factor_at_projection_origin = 0.9330127239227295
        var.grid_mapping_name = "polar_stereographic"
    return var

def add_proj(nc_obj,epsg):
    """
        Adds the appropriate attributes to the netcdf for managing projection info
        Args:
        nc_obj: netCDF4 dataset object needing the projection information
        epsg:   projection information to be added
        Returns:
        nc_obj: the netcdf object modified
    """
    # function to generate .prj file information using spatialreference.org
    # access projection information
    try:
        wkt = urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg))
    except:
        wkt = urlopen("http://spatialreference.org/ref/sr-org/{0}/prettywkt/".format(epsg))

    # remove spaces between charachters
    remove_spaces = ((wkt.read()).decode('utf-8')).replace(" ","")
    # Add in the variable for holding coordinate system info
    map_meta = parse_wkt(remove_spaces,epsg)

    nc_obj.createVariable("projection","S1")
    nc_obj["projection"].setncatts(map_meta)

    for name,var in nc_obj.variables.items():

        # Assume all 2D+ vars are the same projection
        if 'x' in var.dimensions and 'y' in var.dimensions:
            #print("Adding Coordinate System info to {0}".format(name))
            nc_obj[name].setncatts({"grid_mapping":"projection"})

        elif name.lower() in ['x','y']:
            # Set a standard name, which is required for recognizing projections
            nc_obj[name].setncatts({"standard_name":"projection_{}_coordinate"
            "".format(name.lower())})
            # Set the units
            nc_obj[name].setncatts({"units":"meters"
            "".format(name.lower())})


    return nc_obj


def parse_wkt(epsg_string,epsg):
    """
    """
    map_meta = {}
    wkt_data = (epsg_string.lower()).split(',')

    if 'utm' in epsg_string.lower():
        map_meta = gather_utm_meta(epsg_string,epsg)
    print(" Meta information to be added...\n")
    for k,v in map_meta.items():
        print(k,repr(v))
    return map_meta

def gather_utm_meta(epsg_str,epsg):
    """
    Use if the EPSG data is associated to UTM
    Gathers the data and returns a dictionary of data and attributes that need
    to be added to the netcdf based on
    https://www.unidata.ucar.edu/software/thredds/current/netcdf-java/reference/StandardCoordinateTransforms.html
    """
    meta = epsg_str.lower()

    map_meta = {
                    "grid_mapping_name": "universal_transverse_mercator",
                    "utm_zone_number": None,
                    "semi_major_axis": None,
                    "inverse_flattening": None,
                    'spatial_ref':epsg_str,
                    "_CoordinateTransformType": "projection",
                    "_CoordinateAxisTypes": "GeoX GeoY"}

    # Assign the zone number
    zone_str = meta.split('zone')[1]
    var.utm_zone_number= float((strip_chars(zone_str.split(',')[0])).strip()[-2:])

    # Assign the semi_major_axis
    axis_string = meta.split('spheroid')[1]
    var.semi_major_axis= float(axis_string.split(',')[1])

    # Assing the flattening
    map_meta["inverse_flattening"] = float(strip_chars(axis_string.split(',')[2]))

    return map_meta
def strip_chars(edit_str, bad_chars='[(){}<>,"_]=\nns'):
    result = ''.join([s for s in edit_str if s not in bad_chars])

    return result
