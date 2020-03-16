#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#=======================================================================
# name: upload_netcdf.py
#
# category: python script
#
# description:
# Part 2 
#   Publishing netcdf on geoserver with layers.
#
# reference:
#   http://unidata.github.io/netcdf4-python/
#
# author: Elias Borngässer
#=======================================================================


import zipfile
import requests
import utils
import sys,os
import json,re
import logging
from geoserver.catalog import Catalog
cat=Catalog("http://localhost:8080/geoserver/rest/", "admin", "geoserver")

#get config variables
cfg=utils.readConf()
projectname=cfg['general']['project_name']
workspace=cfg['geoserver']['workspaceName']
geoserver_url=cfg['geoserver']['url']

#Check if Config File is correct and NETCDF File existing
if not os.path.exists(sys.path[0]+'/outputFiles/'+projectname+'.nc'):
    logging.error('File '+sys.path[0]+'/outputFiles/'+projectname+'.nc does not exist')
    exit
    
coveragestore=projectname
headers_zip = {'content-type': 'application/zip'}
headers_xml = {'content-type': 'text/xml'}
netcdfFile=sys.path[0]+'/outputFiles/'+projectname+'.nc'

#prepare Session
session = requests.Session()
session.auth = ('admin', 'geoserver')
session.headers.update({'content-type': 'application/json'})#default is json

#delete coveragestore with same Name
r_delete_coveragestore = session.delete(geoserver_url+'/rest/workspaces/'+ workspace  + '/coveragestores/'+coveragestore+'/?recurse=true&purge=all')
print(r_delete_coveragestore.content)

#create New Coveragestore
r_create_coveragestore = session.post(geoserver_url+'/rest/workspaces/'+ workspace  + '/coveragestores?configure=all',
    data='<coverageStore><name>' + coveragestore + '</name><workspace>' + workspace + '</workspace><enabled>true</enabled><type>NetCDF</type><url>file:' + netcdfFile + '</url></coverageStore>',)
print(r_create_coveragestore.content)

# zip the nc file into a zip
zfile = sys.path[0]+'/outputFiles/data.zip'
output = zipfile.ZipFile(zfile, 'w')
output.write(netcdfFile, coveragestore + '.nc', zipfile.ZIP_DEFLATED )
output.close()

#upload zip file (creates layers automatically)
with open(output.filename, 'rb') as zip_file:
    r_create_layer = session.put(geoserver_url+'/rest/workspaces/' + workspace  + '/coveragestores/' + coveragestore  + '/file.netcdf',
        data=zip_file,
        headers=headers_zip)
print(r_create_layer.content)
os.remove(output.filename)
print(session.get('http://localhost:8080/geoserver/rest/workspaces/NetCDF/coveragestores/test/coverages/TSurf.json').content)

#assign styles to created layers
r_get_layers =session.get(geoserver_url+'/rest/workspaces/' + workspace  +'/layers')
layers = r_get_layers.json()
layers = layers['layers']['layer']

# timeParameter={ "enabled": "true","presentation": "LIST", "units": "ISO8601", "defaultValue": None, "nearestMatchEnabled": "false" }
# elevationParameter={ "enabled": "false"}
for _l in layers:
    layer=cat.get_layer(_l['name'])
    #session.post(geoserver_url+'/rest/workspaces/' + workspace  + '/coveragestores/' + coveragestore +'/coverages', data='<coverage><name>'+str(layer)+'</name><title>'+str(layer)+'</title><nativeCRS>GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","3042"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]</nativeCRS><srs>EPSG:3857</srs><projectionPolicy>REPROJECT_TO_DECLARED</projectionPolicy><dimensions><coverageDimension><name>GRAY_INDEX</name><description>GridSampleDimension[-Infinity,Infinity]</description><range><min>-inf</min><max>inf</max></range><nullValues><double>255.0</double></nullValues><dimensionType><name>UNSIGNED_8BITS</name></dimensionType></coverageDimension></dimensions></coverage>',headers=headers_xml)

    if re.match(r".+_\d+_\d+",layer.name): #Checking for variable with multiple height levels
        layer.default_style=re.sub(r"_\d+_\d+","",layer.name)
    else: 
        layer.default_style=layer.name
    cat.save(layer)
    #get coverage to activate time Dimension
    from geoserver.support import DimensionInfo
    coverage = cat.get_resource(layer.name,"test",workspace="NetCDF")
    timeInfo = DimensionInfo("time", "true", "LIST", None, "ISO8601", None)
    coverage.metadata = ({'time': timeInfo})
    cat.save(coverage)
  