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


#Creating Dimensions
def createDimensions():
    # define axis size
    ncout.createDimension('time', None)  # unlimited
    ncout.createDimension('lat', nlat)
    ncout.createDimension('lon', nlon)
    ncout.createDimension('z', nlon)

    # create time axis
    time = ncout.createVariable('time', np.dtype('double').char, ('time',))
    time.long_name = 'time'
    time.units ='hours since '+year+'-'+month+'-'+day+'T'+timeString+'Z'
    time.calendar = 'standard'
    time.axis = 'T'

    # create latitude axis
    lat = ncout.createVariable('lat', np.dtype('double').char, ('lat'))
    lat.standard_name = 'latitude'
    lat.long_name = 'latitude'
    lat.units = 'degrees_north'
    lat.axis = 'Y'

    # create longitude axis
    lon = ncout.createVariable('lon', np.dtype('double').char, ('lon'))
    lon.standard_name = 'longitude'
    lon.long_name = 'longitude'
    lon.units = 'degrees_east'
    lon.axis = 'X'

    resX,resY =utils.calculatePixelSize(locationLat,1,1)
    # copy axis from original dataset
    time[:] = np.round(times[:],2) #converting hours to integer
    lon[:] = longitudes[:]*resX+locationLong
    lat[:] = latitudes[:]*resY+locationLat


#creating vars specified in Config
#height currently not implemented
def createVars():
    
    for name, vin in ncin.variables.items():
        data={}
        if name in attributes:
            name=name.replace('.','_')
            if  len(vin.dimensions)==3:
                data[name] =ncout.createVariable(name,np.dtype('double').char,('time','lat','lon',))
                for ncattr in vin.ncattrs():
                    data[name].setncattr(ncattr, vin.getncattr(ncattr))
                data[name][:]=vin[:]
            elif len(vin.dimensions)==4:
                for h in heightlevels:
                    var_name=name+'_'+str(h).replace('.','_')
                    data[var_name] =ncout.createVariable(var_name,np.dtype('double').char,('time','lat','lon',))
                    for ncattr in vin.ncattrs():
                        data[var_name].setncattr(ncattr, vin.getncattr(ncattr))
                    data[var_name].setncattr('height', h)    
                    heightIndex=np.where(np.array(heights)==h)               
                    data[var_name][:]=np.array(vin)[:,heightIndex,:,:]

#-----------------
# read netCDF file
#-----------------

# open a netCDF file to read
filename = sys.path[0]+"/inputFiles/BVOC_Mainz_IsoOff_2018-07-06_05.00.00.nc"
ncin = Dataset(filename, 'r', format='NETCDF4')

#global attributes
locationLat= ncin.getncattr('LocationLatitude')
locationLong= ncin.getncattr('LocationLongitude')
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

# close files
ncin.close()
ncout.close()




