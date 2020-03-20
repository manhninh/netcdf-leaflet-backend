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
import sys, math, os
import utils, makeMap
from pyproj import Transformer
from affine import Affine

# dimXName='rlon' # #
# standardXName='grid_longitude' # #
# xUnits='degrees' # #
# dimYName='rlat' # # 
# standardYName='grid_latitude'#  #
# yUnits='degrees' # #

dimXName='x' #rlon #
standardXName='x'#'projection_x_coordinate' #grid_longitude #
xUnits='degrees_east' # #degrees
dimYName='y' # # rlat
standardYName='y'#'projection_y_coordinate'#grid_latitude  #
yUnits='degrees_north' # #degrees

crs="mercator" #oblique_stereographic # mercator #rotated_latitude_longitude

#Creating Dimensions
def createDimensions():

    # define axis size
    ncout.createDimension('time', None)  # unlimited
    ncout.createDimension(dimYName, nlat)
    ncout.createDimension(dimXName, nlon)
    ncout.createDimension('z', len(heightlevels))

    # create time axis
    time = ncout.createVariable('time', np.dtype('double').char, ('time',))
    time.long_name = 'time'
    time.units ='hours since '+year+'-'+month+'-'+day+'T'+timeString+'Z'
    time.calendar = 'standard'
    time.axis = 'T'

    # create latitude axis
    y = ncout.createVariable('lat', np.dtype('double').char, (dimYName,dimXName))
    #y.standard_name = standardYName
    y.long_name = 'latitude'
    y.units = yUnits
    #y._CoordinateAxisType = "GeoY"

    # create longitude axis
    x = ncout.createVariable('lon', np.dtype('double').char, (dimYName,dimXName))
    #x.standard_name = standardXName
    x.long_name = 'longitude'
    x.units = xUnits
    #x._CoordinateAxisType = "GeoX"

    resX,resY =utils.calculatePixelSize(locationLat,1,1)
    # copy axis from original dataset
    transformer=Transformer.from_crs(4326, epsg)
    locationLongTransformed,locationLatTransformed = transformer.transform(locationLat,locationLong)
   
    #  lons=np.array(longitudes).fill(8)
    #  for i in nlon:
    #      for j in nlat
    #          x[i][j]=longitudes[i,j]

    x[:][:] = longitudes[:]#+locationLongTransformed #*resX+locationLong
    y[:][:] = latitudes[:]#+locationLatTransformed #*resY+locationLat

#creating vars specified in Config
#height currently not implemented
def createVars():
    for var_name, vin in ncin.variables.items():
        data={}
        if var_name in attributes:

            var_name=var_name.replace('.','_') #
            if  len(vin.dimensions)==3:
                makeMap.addOverlay(vin.name,vin.long_name,False)
                fill_val=vin._FillValue if hasattr(vin, '_FillValue') else 999
                data[var_name] =ncout.createVariable(var_name,np.dtype('double').char,('time',dimYName,dimXName,),fill_value=fill_val)
                for ncattr in vin.ncattrs():
                    if ncattr!='_FillValue' and ncattr!='grid_mapping':
                        data[var_name].setncattr(ncattr, vin.getncattr(ncattr))
                data[var_name][:]=vin[:]
                data[var_name][:]=data[var_name][:,::-1]
                #data[var_name].setncattr('grid_mapping', crs)

                makeMap.addLayer(l_name=vin.name,l_mappingName=vin.long_name)

            elif len(vin.dimensions)==4:
                makeMap.addOverlay(vin.name,vin.long_name,True)
                for h in heightlevels:
                    var_height_name=var_name+'_'+str(h).replace('.','_')# adding height value to var name
                    fill_val=vin._FillValue if hasattr(vin, '_FillValue') else 999
                    data[var_height_name] =ncout.createVariable(var_height_name,np.dtype('double').char,('time',dimYName,dimXName,),fill_value=fill_val)
                    for ncattr in vin.ncattrs():
                        if ncattr!='_FillValue' and ncattr!='grid_mapping':
                            data[var_height_name].setncattr(ncattr, vin.getncattr(ncattr))
                    data[var_height_name].setncattr('height', h)    
                    heightIndex=np.where(np.array(heights)==h) #find height by value
                    data[var_height_name][:]=np.array(vin)[:,heightIndex,:,:] #Getting slice of array by height index
                    data[var_height_name][:]=data[var_height_name][:,::-1]
                    #data[var_height_name].setncattr('grid_mapping', crs)
                    
                    heightString=str(h)+' Meter'
                    makeMap.addHeightLayer(var_height_name,heightString,vin.long_name)
                    makeMap.addHeight(str(h).replace('.','_'),heightString)
            
def add_grid_mapping(crs):
    data={}
    data[crs] =ncout.createVariable(crs,"S1")
    utils.addGridMappingVars(data[crs],crs)

def add_global_attrs():
    data={}
    data['global_attribute'] =ncout.createVariable('global_attribute',np.dtype('c').char)

#-----------------
# read netCDF file
#-----------------
#get config variables
cfg=utils.readConf()
attributes=cfg['general']['attributes_to_read']
epsg=cfg['general']['EPSG']
projectname=cfg['general']['project_name']
heightlevels=cfg['general']['height_levels']
grid_mapping=cfg['general']['grid_mapping']
inputFile=cfg['general']['inputFile']

# open a netCDF file to read
filename = sys.path[0]+"/inputFiles/"+inputFile
ncin = Dataset(filename, 'r', format='NETCDF4')

#global attributes
locationLat= ncin.getncattr('LocationLatitude')
locationLong= ncin.getncattr('LocationLongitude')
false_northing = ncin.getncattr('ModelRotation')
pixelWidth = int(ncin.getncattr('SizeDX')[0])
pixelHeight = int(ncin.getncattr('SizeDY')[0])
day,month,year=str(ncin.getncattr('SimulationDate')).split('.')
timeString =str(ncin.getncattr('SimulationTime').replace('.',':'))




# get axis data
times = ncin.variables['Time']
latitudes = ncin.variables['Lat']
longitudes = ncin.variables['Lon']
heights = ncin.variables['GridsK']

# get length of axis data
nlat = len(ncin.variables['GridsJ'])
nlon = len(ncin.variables['GridsI'])
ntime = len(times)

makeMap.createMap('-'.join([year,month,day]),timeString,ntime-1,int(times[1]*60),locationLat,locationLong)

# open netCDF file to write
if not os.path.isdir(sys.path[0]+'/outputFiles/'):
    os.mkdir(sys.path[0]+'/outputFiles/')
ncout = Dataset(sys.path[0]+'/outputFiles/'+ projectname +'.nc', 'w', format='NETCDF4')

createDimensions()
createVars()
#add_grid_mapping(crs)
ncout.Conventions='CF-1.7'

# close files
ncin.close()
ncout.close()

makeMap.createOverlays()




