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
import json
from geoserver.catalog import Catalog
cat=Catalog("http://localhost:8080/geoserver/rest/", "admin", "geoserver")

#get config variables
cfg=utils.readConf()
projectname=cfg['general']['project_name']
geoserver_url=cfg['geoserver']['url']

workspace='NetCDF'#[FIX] workspace name is used static and not created right now
coveragestore=projectname
headers_zip = {'content-type': 'application/zip'}
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
    data='<coverageStore><name>' + coveragestore + '</name><workspace>' + workspace + '</workspace><enabled>true</enabled><type>NetCDF</type><url>file:' + netcdfFile + '</url></coverageStore>')
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

#assign styles to created layers
r_get_layers =session.get(geoserver_url+'/rest/workspaces/' + workspace  +'/layers')
layers = r_get_layers.json()
layers = layers['layers']['layer']

# timeParameter={ "enabled": "true","presentation": "LIST", "units": "ISO8601", "defaultValue": None, "nearestMatchEnabled": "false" }
# elevationParameter={ "enabled": "false"}
for _l in layers:
    layer=cat.get_layer(_l['name'])
    layer.default_style=layer.name
    cat.save(layer)
    #get coverage to activate time Dimension
    from geoserver.support import DimensionInfo
    coverage = cat.get_resource(layer.name,"test",workspace="NetCDF")
    timeInfo = DimensionInfo("time", "true", "LIST", None, "ISO8601", None)
    coverage.metadata = ({'time': timeInfo})
    cat.save(coverage)
