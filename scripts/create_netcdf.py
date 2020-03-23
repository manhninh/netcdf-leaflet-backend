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
import sys, math, os,logging
import utils, makeMap
from pyproj import Transformer
from affine import Affine

# dimXName='rlon' # #
# standardXName='grid_longitude' # #
# xUnits='degrees' # #
# dimYName='rlat' # # 
# standardYName='grid_latitude'#  #
# yUnits='degrees' # #
# crs="mercator2"

dimXName='x' #rlon #
standardXName='projection_x_coordinate' #grid_longitude #
xUnits='m' # #degrees
dimYName='y' # # rlat
standardYName='projection_y_coordinate'#grid_latitude  #
yUnits='m' # #degrees
defined_grid_mapping=False

#Creating Dimensions
def createDimensions():

    # define axis size
    ncout.createDimension('time', None)  # unlimited
    ncout.createDimension(dimYName, nlat)
    ncout.createDimension(dimXName, nlon)
    ncout.createDimension('z', nlon)

    # create time axis
    time = ncout.createVariable('time', np.dtype('double').char, ('time',))
    time.long_name = 'time'
    time.units ='hours since '+year+'-'+month+'-'+day+'T'+timeString+'Z'
    time.calendar = 'standard'
    time.axis = 'T'

    time[:] = np.round(times[:],2) #converting hours to integer

    # create latitude axis
    y = ncout.createVariable(dimYName, np.dtype('double').char, (dimYName))
    y.standard_name = standardYName
    y.long_name = 'y coordinate of projection'
    y.units = yUnits
    #y._CoordinateAxisType = "GeoY"

    # create longitude axis
    x = ncout.createVariable(dimXName, np.dtype('double').char, (dimXName))
    x.standard_name = standardXName
    x.long_name = 'x coordinate of projection'
    x.units = xUnits
    #x._CoordinateAxisType = "GeoX"


    if not defined_grid_mapping and 'targetEPSG' in cfg['general']:
        transformer=Transformer.from_crs(sourceEPSG, cfg['general']['targetEPSG'])
        locationLongTransformed,locationLatTransformed = transformer.transform(locationLat,locationLong)
        x[:] = longitudes[::-1]+locationLongTransformed #*resX+locationLong
        y[:] = latitudes[:]+locationLatTransformed #*resY+locationLat
    else:
        x[:] = longitudes[:]#+locationLongTransformed #*resX+locationLong
        y[:] = latitudes[:]#+locationLatTransformed #*resY+locationLat

#creating vars specified in Config
#height currently not implemented
def add_attributes(vin:Variable,data:Variable):
    for ncattr in vin.ncattrs():
        if ncattr!='_FillValue':
            data.setncattr(ncattr, vin.getncattr(ncattr))
    return data

def createVars():
    for var_name, vin in ncin.variables.items():
        data={}

        if var_name in attributes:
            # vin_array=vin[:][:]
            # vin_min = float(vin_array.min())
            # vin_max = float(vin_array.max())
            var_name=var_name.replace('.','_') #
            if  len(vin.dimensions)==3:
                makeMap.addOverlay(vin.name,vin.long_name,False)
                fill_val=vin._FillValue if hasattr(vin, '_FillValue') else 999
                data[var_name] =ncout.createVariable(var_name,np.dtype('double').char,('time',dimYName,dimXName,),fill_value=fill_val)
                data[var_name] =add_attributes(vin,data[var_name])
                data[var_name][:]=vin[:]
                data[var_name][:]=data[var_name][:,::-1]
                data[var_name].setncattr('grid_mapping', crs)

                vin_min = float(data[var_name][:][:].min())
                vin_max = float(data[var_name][:][:].max())
                makeMap.addLayer(l_name=vin.name,l_mappingName=vin.long_name,minValue=vin_min,maxValue=vin_max,unit=vin.units)

            elif len(vin.dimensions)==4:
                makeMap.addOverlay(vin.name,vin.long_name,True)
                for h in heightlevels:
                    var_height_name=var_name+str(h).replace('.','')# adding height value to var name
                    fill_val=vin._FillValue if hasattr(vin, '_FillValue') else 999
                    data[var_height_name] =ncout.createVariable(var_height_name,np.dtype('double').char,('time',dimYName,dimXName,),fill_value=fill_val)
                    data[var_height_name] =add_attributes(vin,data[var_height_name])
                    data[var_height_name].setncattr('height', h)    
                    heightIndex=np.where(np.array(heights)==h) #find height by value
                    data[var_height_name][:]=np.array(vin)[:,heightIndex,:,:] #Getting slice of array by height index
                    data[var_height_name][:]=data[var_height_name][:,::-1]
                    data[var_height_name].setncattr('grid_mapping', crs)
                    
                    heightString=str(h)+' Meter'
                    vin_min = float(data[var_height_name][:][:].min())
                    vin_max = float(data[var_height_name][:][:].max())
                    makeMap.addHeightLayer(var_height_name,heightString,vin.long_name,minValue=vin_min,maxValue=vin_max,unit=vin.units)
                    makeMap.addHeight(str(h).replace('.',''),heightString)
def add_defined_grid_mapping(crs):
    vin=ncin.variables[crs]
    data={}
    data[crs] =ncout.createVariable(crs,"S1") 
    data[crs] =add_attributes(vin,data[crs])
def add_manual_grid_mapping(crs):
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
sourceEPSG=cfg['general']['sourceEPSG']
projectname=cfg['general']['project_name']
heightlevels=cfg['general']['height_levels']
grid_mapping=cfg['general']['grid_mapping']
inputFile=cfg['general']['inputFile']
logging.getLogger().setLevel(cfg['general']['log_level'])

filePaths=[sys.path[0]+'/../inputFiles/'+inputFile,cfg['frontend']['absolutePath']]
#Check if Config File is correct and Paths are existing
for path in filePaths:
    if not os.path.exists(path):
        logging.error('Path: '+path+' does not exist')
        exit

# open a netCDF file to read
filename = filePaths[0]
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
latitudes = ncin.variables['GridsJ']
longitudes = ncin.variables['GridsI']
heights = ncin.variables['GridsK']

# get length of axis data
nlat = len(latitudes)
nlon = len(longitudes)
ntime = len(times)

makeMap.createMap('-'.join([year,month,day]),timeString,ntime-1,int(times[1]*60),locationLat,locationLong)

# open netCDF file to write
if not os.path.isdir(sys.path[0]+'/../outputFiles/'):
    os.mkdir(sys.path[0]+'/../outputFiles/')
ncout = Dataset(sys.path[0]+'/../outputFiles/'+ projectname +'.nc', 'w', format='NETCDF4')

if grid_mapping in ncin.variables:
    crs=grid_mapping
    add_defined_grid_mapping(crs)
    defined_grid_mapping=True
else:
    crs="mercator"#oblique_stereographic # mercator #rotated_latitude_longitude
    add_manual_grid_mapping(crs)

createDimensions()
createVars()
#ncout = utils.add_proj(ncout,epsg)
ncout.Conventions='CF-1.7'

# close files
ncin.close()
ncout.close()

makeMap.finalizeMap()




