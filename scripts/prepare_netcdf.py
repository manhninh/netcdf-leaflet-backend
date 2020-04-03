#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#=======================================================================
# name: prepare_netcdf.py
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
from libs import utils, makeMap

cfg=utils.cfg

dimXName='GridsI'
dimYName='GridsJ'
dimZName='GridsK'

def createDimensions():
    for d in ncin.dimensions:
        dimVar=ncin[d]
        ncout.createDimension(d,dimVar.size)
        data=ncout.createVariable(d,np.dtype('double').char,(d))
        add_attributes(dimVar,data)
        if d== dimYName:
            data[:]=dimVar[::-1]
        else:
            data[:]=dimVar[:]

#creating vars specified in Config
def add_attributes(vin:Variable,data:Variable):
    for ncattr in vin.ncattrs():
        if ncattr!='_FillValue':
            data.setncattr(ncattr, vin.getncattr(ncattr))
    return data

def createVars():
    for var_name in attributes:
        if var_name in ncin.variables:
            vin = ncin.variables[var_name]
            data={}
            var_name=var_name.replace('.','_') 
            if  len(vin.dimensions)==3: 
                makeMap.addOverlay(vin.name,vin.long_name,False)
                fill_val=vin._FillValue if hasattr(vin, '_FillValue') else 999
                data[var_name] =ncout.createVariable(var_name,np.dtype('double').char,('Time',dimYName,dimXName,),fill_value=fill_val)
                data[var_name] =add_attributes(vin,data[var_name])
                data[var_name][:]=vin[:]
                data[var_name][:]=data[var_name][:,::-1]
                data[var_name].setncattr('grid_mapping', 'crs')

                vin_min = float(data[var_name][:][:].min())
                vin_max = float(data[var_name][:][:].max())
                makeMap.addLayer(l_name=vin.name,l_mappingName=vin.long_name,minValue=vin_min,maxValue=vin_max,unit=vin.units)

            elif len(vin.dimensions)==4 and vin.dimensions[1]==dimZName:
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
                    data[var_height_name].setncattr('grid_mapping', 'crs')
                    
                    heightString=str(h)+' Meter'
                    vin_min = float(data[var_height_name][:][:].min())
                    vin_max = float(data[var_height_name][:][:].max())
                    makeMap.addHeightLayer(var_height_name,heightString,vin.long_name,minValue=vin_min,maxValue=vin_max,unit=vin.units)
                    makeMap.addHeight(str(h).replace('.',''),heightString)
            else:
                logging.warning('Variable '+ var_name + ' has no valid dimensions')
        else:
            logging.warning('Variable '+ var_name + ' not found in '+inputFile)

def add_manual_grid_mapping():
    data={}
    data['crs'] =ncout.createVariable('crs',np.dtype('c').char)
    utils.addGridMappingVars(data['crs'],locationLat,locationLong,rotation)

def add_global_attrs():
    data={}
    data['global_attribute'] =ncout.createVariable('global_attribute',np.dtype('c').char)

#-----------------
# read netCDF file
#-----------------
#get config variables

attributes=cfg['general']['attributes_to_read']
projectName=cfg['general']['projectName']
heightlevels=cfg['general']['height_levels']
inputFile=cfg['general']['inputFile']

# open a netCDF file to read
filename = cfg['general']['inputFile']
try:
    ncin = Dataset(filename, 'r', format='NETCDF4')
except:
    logging.error(filename +"is not a valid NetCDF File")
    sys.exit(1)
logging.info("Creating project "+projectName +" from "+inputFile)

#global attributes
locationLat= ncin.getncattr('LocationLatitude')
locationLong= ncin.getncattr('LocationLongitude')

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

makeMap.createMap('-'.join([year,month,day]),timeString,ntime-1,int(times[0]*60),locationLat,locationLong)

# open netCDF file to write
if not os.path.isdir(cfg['general']['workdir']+'/outputFiles/'):
    os.mkdir(cfg['general']['workdir']+'/outputFiles/')
ncout = Dataset(cfg['general']['workdir']+'/outputFiles/'+ projectName +'.nc', 'w', format='NETCDF4')


add_manual_grid_mapping()

createDimensions()
createVars()
#ncout = utils.add_proj(ncout,epsg)
ncout.Conventions='CF-1.7'

# close files
ncin.close()
ncout.close()

makeMap.finalizeMap()




