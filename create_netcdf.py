#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#=======================================================================
# name: create_netcdf.py
#
# category: python script
# Part 1
# description:
#   Reads EnviMet NetCDF and write a geoserver compatible netCDF file
#
# reference:
#   http://unidata.github.io/netcdf4-python/
#
# author: Elias Borngässer
#=======================================================================

from netCDF4 import Dataset,Variable
import numpy as np
import sys, math,os
import utils
from pyproj import Transformer
from affine import Affine


#Creating Dimensions
def createDimensions():
    # define axis size
    ncout.createDimension('time', None)  # unlimited
    ncout.createDimension('y', nlat)
    ncout.createDimension('x', nlon)
    ncout.createDimension('z', nlon)

    # create time axis
    time = ncout.createVariable('time', np.dtype('double').char, ('time',))
    time.long_name = 'time'
    time.units ='hours since '+year+'-'+month+'-'+day+'T'+timeString+'Z'
    time.calendar = 'standard'
    time.axis = 'T'

    # create latitude axis
    y = ncout.createVariable('y', np.dtype('double').char, ('y'))
    y.standard_name = 'projection_y_coordinate'
    y.long_name = 'y coordinate of projection'
    y.units = 'm'
    y.axis = 'Y'

    # create longitude axis
    x = ncout.createVariable('x', np.dtype('double').char, ('x'))
    x.standard_name = 'projection_x_coordinate'
    x.long_name = 'x coordinate of projection'
    x.units = 'm'
    x.axis = 'X'

    #resX,resY =utils.calculatePixelSize(locationLat,1,1)
    # copy axis from original dataset
    transformer=Transformer.from_crs(4326, epsg)
    locationLongTransformed,locationLatTransformed = transformer.transform(locationLat,locationLong)
    time[:] = np.round(times[:],2) #converting hours to integer
   
    x[:] = longitudes[::-1]+locationLongTransformed #*resX+locationLong
    y[:] = latitudes[:]+locationLatTransformed#*resY+locationLat :-1



#creating vars specified in Config
#height currently not implemented
def createVars():
    for var_name, vin in ncin.variables.items():
        data={}
        if var_name in attributes:
            var_name=var_name.replace('.','_') #
            if  len(vin.dimensions)==3:
                fill_val=vin._FillValue if hasattr(vin, '_FillValue') else 999
                data[var_name] =ncout.createVariable(var_name,np.dtype('double').char,('time','y','x',),fill_value=fill_val)
                for ncattr in vin.ncattrs():
                    if ncattr!='_FillValue':
                        data[var_name].setncattr(ncattr, vin.getncattr(ncattr))
                data[var_name][:]=vin[:]
                data[var_name][:]=data[var_name][:,::-1]
                data[var_name].setncattr('grid_mapping', 'crs')
            elif len(vin.dimensions)==4:
                for h in heightlevels:
                    var_height_name=var_name+'_'+str(h).replace('.','_')# adding height value to var name
                    fill_val=vin._FillValue if hasattr(vin, '_FillValue') else 999
                    data[var_height_name] =ncout.createVariable(var_height_name,np.dtype('double').char,('time','y','x',),fill_value=fill_val)
                    for ncattr in vin.ncattrs():
                        if ncattr!='_FillValue':
                            data[var_height_name].setncattr(ncattr, vin.getncattr(ncattr))
                    data[var_height_name].setncattr('height', h)    
                    heightIndex=np.where(np.array(heights)==h) #find height by value
                    data[var_height_name][:]=np.array(vin)[:,heightIndex,:,:] #Getting slice of array by height index
                    data[var_height_name][:]=data[var_height_name][:,::-1]
                    data[var_height_name].setncattr('grid_mapping', 'crs')
            


def add_grid_mapping(grid_mapping):
    data={}
    data['crs'] =ncout.createVariable('crs',np.dtype('c').char)
    utils.addGridMappingVars(data['crs'],grid_mapping)
    affine=Affine.rotation(58.0)
    ratio=1.0#math.pi
    elt_0_0=str(affine.a/ratio)
    elt_0_1=str(affine.b/ratio)
    elt_0_2=str(918079.626281209) #918079.626281209)#0.0) #446044.8576076973
    elt_1_0=str(affine.d/ratio)
    elt_1_1=str(affine.e/ratio)
    elt_1_2=str(6445039.217828758) #6445039.217828758) #5538108.209966961

    data['crs'].grid_mapping_name= "mercator"
    data['crs'].longitude_of_central_meridian= 0.0
    data['crs'].latitude_of_projection_origin= 0.0 
    data['crs'].standard_parallel= 0.02
    data['crs']._CoordinateTransformType= "Projection"
    data['crs']._CoordinateAxisTypes= "GeoX GeoY"
    data['crs'].spatial_ref = 'FITTED_CS["BPAF", PARAM_MT["Affine", PARAMETER["num_row", 3], PARAMETER["num_col", 3], PARAMETER["elt_0_0",'+elt_0_0+'], PARAMETER["elt_0_1", '+elt_0_1+'], PARAMETER["elt_0_2", '+elt_0_2+'], PARAMETER["elt_1_0", '+elt_1_0+'], PARAMETER["elt_1_1", '+elt_1_1+'], PARAMETER["elt_1_2", '+elt_1_2+']], PROJCS["WGS84 / Google Mercator", GEOGCS["WGS 84", DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], UNIT["degree", 0.017453292519943295], AXIS["Longitude", EAST], AXIS["Latitude", NORTH], AUTHORITY["EPSG","4326"]], PROJECTION["Mercator_1SP"], PARAMETER["semi_minor", 6378137.0], PARAMETER["latitude_of_origin", 0.0], PARAMETER["central_meridian", 0.0], PARAMETER["scale_factor", 1.0], PARAMETER["false_easting", 0.0], PARAMETER["false_northing", 0.0], UNIT["m", 1.0], AXIS["x", EAST], AXIS["y", NORTH], AUTHORITY["EPSG","900913"]], AUTHORITY["EPSG","8011113"]]'
    print(data['crs'].spatial_ref)
def add_global_attrs():
    data={}
    data['global_attribute'] =ncout.createVariable('global_attribute',np.dtype('c').char)

#-----------------
# read netCDF file
#-----------------

# open a netCDF file to read
filename = sys.path[0]+"/inputFiles/BVOC_Mainz_IsoOff_2018-07-06_05.00.00.nc"
ncin = Dataset(filename, 'r', format='NETCDF4')

#global attributes
locationLat= ncin.getncattr('LocationLatitude')
locationLong= ncin.getncattr('LocationLongitude')
false_northing = ncin.getncattr('ModelRotation')
pixelWidth = int(ncin.getncattr('SizeDX')[0])
pixelHeight = int(ncin.getncattr('SizeDY')[0])
day,month,year=str(ncin.getncattr('SimulationDate')).split('.')
timeString =str(ncin.getncattr('SimulationTime').replace('.',':'))

#get config variables
cfg=utils.readConf()
attributes=cfg['general']['attributes_to_read']
epsg=cfg['general']['EPSG']
projectname=cfg['general']['project_name']
heightlevels=cfg['general']['height_levels']
grid_mapping=cfg['general']['grid_mapping']

# get axis data
times = ncin.variables['Time']
latitudes = ncin.variables['GridsJ']
longitudes = ncin.variables['GridsI']
heights = ncin.variables['GridsK']

# get length of axis data
nlat = len(latitudes)
nlon = len(longitudes)
ntime = len(times)

# open netCDF file to write
if not os.path.isdir(sys.path[0]+'/outputFiles/'):
    os.mkdir(sys.path[0]+'/outputFiles/')
ncout = Dataset(sys.path[0]+'/outputFiles/'+ projectname +'.nc', 'w', format='NETCDF4')

createDimensions()
createVars()
add_grid_mapping(grid_mapping)
#ncout = utils.add_proj(ncout,epsg)
ncout.Conventions='CF-1.7'

# close files
ncin.close()
ncout.close()




