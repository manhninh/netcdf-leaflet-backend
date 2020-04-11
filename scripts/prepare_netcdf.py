#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#=======================================================================
# name: prepare_netcdf.py
#
# description:
#   Reads EnviMet NetCDF and write a geoserver compatible netCDF file
#
# author: Elias Borngässer
#=======================================================================

from netCDF4 import Dataset,Variable
import numpy as np
import sys, math, os,logging
from libs import utils, makeMap, DEM
from pathlib import Path

cfg=utils.cfg

dimXName='GridsI'
dimYName='GridsJ'
dimZName='GridsK'
dimTName='Time'

def createDimensions():
    for d in ncin.dimensions:
        dimVar=ncin[d]
        ncout.createDimension(d,dimVar.size)
        data=ncout.createVariable(d,np.dtype('double').char,(d))
        add_attributes(dimVar,data)
        if d==dimTName:
            data.units="Hours since {}-{}-{} {}".format(year,month,day,timeString)
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
    isDEM =False
    varDEMOFFSet=None
    maxDEMOffset=0
    emptyArray=None
    if 'DEMOffset' in  ncin.variables:
        maxDEMOffset=int(ncin.variables["DEMOffset"][:][:].max())
        isDEM= True if maxDEMOffset>0 else False
        varDEMOFFSet=ncin.variables["DEMOffset"][:]
        emptyArray=np.empty_like(ncin.variables["DEMOffset"])
    logging.debug("Is DEMFile: "+str(isDEM))
    for var_name in attributes:
        if var_name in ncin.variables:
            vin = ncin.variables[var_name]
            data={}
            var_name=var_name.replace('.','_')
            # Variables without Height Dimension 
            if  len(vin.dimensions)==3: 
                makeMap.addOverlay(vin.name,vin.long_name,False)
                fill_val=vin._FillValue if hasattr(vin, '_FillValue') else 999
                data[var_name] =ncout.createVariable(var_name,np.dtype('double').char,(dimTName,dimYName,dimXName,),fill_value=fill_val)
                data[var_name] =add_attributes(vin,data[var_name])
                data[var_name][:]=vin[:,::-1]# flipping vertical axis for correct visualization
                data[var_name].setncattr('grid_mapping', 'crs')
                # Create Layer
                makeMap.addLayer(l_name=vin.name,l_mappingName=vin.long_name)
                # Default Style
                vin_min = float(data[vin.name][:][:].min())
                vin_max = float(data[vin.name][:][:].max())
                makeMap.createStyle(s_name=vin.name,longName=vin.long_name,minValue=vin_min,maxValue=vin_max,unit=vin.units)
                #Timedependent Styles
                for i in range(ntime):
                    vin_min = float(data[var_name][i][:].min())
                    vin_max = float(data[var_name][i][:].max())
                    makeMap.createStyle(s_name=vin.name+str(i),longName=vin.long_name,minValue=vin_min,maxValue=vin_max,unit=vin.units,index=i)

            #Variables with Height Dimension
            elif len(vin.dimensions)==4 and vin.dimensions[1]==dimZName:
                makeMap.addOverlay(vin.name,vin.long_name,True)
                for h in heightlevels:
                    heightIndex=int(np.where(np.array(heights)==h)[0]) #find height by value (MUST BE UNIQUE)
                    if isDEM and maxDEMOffset+heightIndex>nheight:
                        logging.warning("Will skip heightLevel "+ h +" cause of max DEMOffset Value "+maxDEMOffset)
                        continue
                    var_height_name=var_name+str(h).replace('.','')# adding height value to var name
                    fill_val=vin._FillValue if hasattr(vin, '_FillValue') else 999
                    data[var_height_name] =ncout.createVariable(var_height_name,np.dtype('double').char,(dimTName,dimYName,dimXName,),fill_value=fill_val)
                    data[var_height_name] =add_attributes(vin,data[var_height_name])
                    data[var_height_name].setncattr('height', h)    

                    if isDEM:
                        data[var_height_name][:]=DEM.getDEMArray(emptyArray,vin[:],varDEMOFFSet,heightIndex)
                    else:
                        data[var_height_name][:]=np.array(vin)[:,heightIndex,:,:] #Getting slice of array by height index
                    data[var_height_name][:]=data[var_height_name][:,::-1] 
                    data[var_height_name].setncattr('grid_mapping', 'crs')
                    # Create HeightLayer
                    makeMap.addHeightLayer(var_height_name,h,vin.long_name)
                    # Default Style
                    vin_min = float(data[var_height_name][:][:].min())
                    vin_max = float(data[var_height_name][:][:].max())
                    makeMap.createStyle(s_name=var_height_name,longName=vin.long_name,minValue=vin_min,maxValue=vin_max,unit=vin.units,h=h)
                    #Timedependent Styles
                    for i in range(ntime):
                        vin_min = float(data[var_height_name][i][:].min())
                        vin_max = float(data[var_height_name][i][:].max())
                        makeMap.createStyle(s_name=var_height_name+str(i),longName=vin.long_name,minValue=vin_min,maxValue=vin_max,unit=vin.units,h=h,index=i)

            else:
                logging.warning('Variable '+ var_name + ' has no valid dimensions')
        else:
            logging.warning('Variable '+ var_name + ' not found in '+inputFile)

def add_manual_grid_mapping():
    data={}
    data['crs'] =ncout.createVariable('crs',np.dtype('c').char)
    utils.addGridMappingVars(data['crs'],locationLat,locationLong,rotation)


#-----------------
# read netCDF file
#-----------------
#get config variables

attributes=cfg['general']['attributes_to_read']
projectName=cfg['general']['projectName']

inputFile=cfg['general']['inputFile']

# open a netCDF file to read
filename = cfg['general']['inputFile']
try:
    ncin = Dataset(filename, 'r', format='NETCDF4')
except:
    logging.error(filename +" is not a valid NetCDF File")
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
times = ncin.variables[dimTName]
latitudes = ncin.variables[dimYName]
longitudes = ncin.variables[dimXName]
heights = ncin.variables[dimZName]

# get length of axis data
nlat = len(latitudes)
nlon = len(longitudes)
ntime = len(times)
nheight =len(heights)

heightlevels=cfg['general']['height_levels']
if isinstance(heightlevels,int):
    if nheight<heightlevels:
        logging.warning("File "+inputFile+" only has "+str(nheight) +" Levels, will only use those")
        heightlevels=heights[:nheight]
    heightlevels=heights[:heightlevels]
    
if ntime>1:
    timeInterval=int((times[1]-times[0])*60) # Examine the timeInterval
else:
    timeInterval=60 #Just using some value to fix timeHandling
makeMap.initMap('-'.join([year,month,day]),timeString,ntime,timeInterval,locationLat,locationLong)

# open netCDF file to write
if not os.path.isdir(cfg['general']['workdir']+'/outputFiles/'+projectName+'/'):
    Path(cfg['general']['workdir']+'/outputFiles/'+projectName+'/').mkdir(parents=True,exist_ok=True)
ncout = Dataset(cfg['general']['workdir']+'/outputFiles/'+projectName+'/'+ projectName +'.nc', 'w', format='NETCDF4')


add_manual_grid_mapping()

createDimensions()
createVars()
#ncout = utils.add_proj(ncout,epsg)
ncout.Conventions='CF-1.7'

# close files
ncin.close()
ncout.close()

makeMap.finalizeMap()




