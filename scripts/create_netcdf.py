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
#from pylab import *
import numpy as np
import sys, math, os,logging
import utils, makeMap
from pyproj import Transformer
from affine import Affine

dimXName='GridsI' #rlon #
standardXName='projection_x_coordinate' #grid_longitude #
xUnits='m' # #degrees
dimYName='GridsJ' # # rlat
standardYName='projection_y_coordinate'#grid_latitude  #
yUnits='m' # #degrees
defined_grid_mapping=False

def createDimensions2():
    for d in ncin.dimensions:
        dimVar=ncin[d]
        ncout.createDimension(d,dimVar.size)
        data=ncout.createVariable(d,np.dtype('double').char,(d))
        add_attributes(dimVar,data)
        if d== 'GridsJ':
            data[:]=dimVar[::-1]
        else:
            data[:]=dimVar[:]
    dimVar=ncin['UTM_Y']
    data=ncout.createVariable('UTM_Y',np.dtype('double').char,('GridsI', 'GridsJ'))
    add_attributes(dimVar,data)
    dimVar=ncin['UTM_X']
    data=ncout.createVariable('UTM_X',np.dtype('double').char,('GridsI', 'GridsJ'))
    add_attributes(dimVar,data)
        



#Creating Dimensions
def createDimensions():

    # define axis size
    ncout.createDimension('Time', None)  # unlimited
    ncout.createDimension(dimYName, nlat)
    ncout.createDimension(dimXName, nlon)
    ncout.createDimension('z', nlon)

    # create time axis
    time = ncout.createVariable('Time', np.dtype('double').char, ('Time',))
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
        x[:] = longitudes[:]#+locationLongTransformed #*resX+locationLong
        y[:] = latitudes[::-1]#+locationLatTransformed #*resY+locationLat
    else:
        x[:] = longitudes[:]
        y[:] = latitudes[::-1]

#creating vars specified in Config
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
                data[var_name] =ncout.createVariable(var_name,np.dtype('double').char,('Time',dimYName,dimXName,),fill_value=fill_val)
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
                    data[var_height_name] =ncout.createVariable(var_height_name,np.dtype('double').char,('Time',dimYName,dimXName,),fill_value=fill_val)
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
    utils.addGridMappingVars(data[crs],crs,locationLat,locationLong,rotation)

def add_global_attrs():
    data={}
    data['global_attribute'] =ncout.createVariable('global_attribute',np.dtype('c').char)

#-----------------
# read netCDF file
#-----------------
#get config variables
workdir, cfg =utils.readConf()

attributes=cfg['general']['attributes_to_read']
sourceEPSG=cfg['general']['sourceEPSG']
projectname=cfg['general']['project_name']
heightlevels=cfg['general']['height_levels']
grid_mapping=cfg['general']['grid_mapping']
inputFile=cfg['general']['inputFile']
logging.getLogger().setLevel(cfg['general']['log_level'])

filePaths=[workdir+'/inputFiles/'+inputFile,cfg['frontend']['path']]
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

transformer=Transformer.from_crs(4326, cfg['general']['targetEPSG'])
locationLongTransformed,locationLatTransformed = transformer.transform(locationLat,locationLong)
rotation = ncin.getncattr('ModelRotation')
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
if not os.path.isdir(workdir+'/outputFiles/'):
    os.mkdir(workdir+'/outputFiles/')
ncout = Dataset(workdir+'/outputFiles/'+ projectname +'.nc', 'w', format='NETCDF4')

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




