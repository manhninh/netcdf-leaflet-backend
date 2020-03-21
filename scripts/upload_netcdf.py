#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#=======================================================================
# name: upload_netcdf.py
#
# category: python script
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


#get config variables
cfg=utils.readConf()
projectname=cfg['general']['project_name']
workspace=cfg['geoserver']['workspaceName']
geoserver_url=cfg['geoserver']['url']

cat=Catalog(geoserver_url+ "/rest/", "admin", "geoserver")

#Check if Config File is correct and NETCDF File existing
if not os.path.exists(sys.path[0]+'/../outputFiles/'+projectname+'.nc'):
    logging.error('File '+sys.path[0]+'/../outputFiles/'+projectname+'.nc does not exist')
    exit
    
coveragestore=projectname
headers_zip = {'content-type': 'application/zip'}
headers_xml = {'content-type': 'text/xml'}
netcdfFile=sys.path[0]+'/../outputFiles/'+projectname+'.nc'

#prepare Session
session = requests.Session()
session.auth = ('admin', 'geoserver')
session.headers.update({'content-type': 'application/json'})#default is json
#create Workspace if doesn't exist
if  not cat.get_workspace(workspace):
    cat.create_workspace(workspace,workspace)
#delete coveragestore with same Name if existing
if cat.get_store(coveragestore,workspace):
    cat.delete(cat.get_store(coveragestore,workspace),purge="all",recurse=True)
# r_delete_coveragestore = session.delete(geoserver_url+'/rest/workspaces/'+ workspace  + '/coveragestores/'+coveragestore+'/?recurse=true&purge=all')
# print(r_delete_coveragestore.content)

#create New Coveragestore
r_create_coveragestore = session.post(geoserver_url+'/rest/workspaces/'+ workspace  + '/coveragestores?configure=all',
    data='<coverageStore><name>' + coveragestore + '</name><workspace>' + workspace + '</workspace><enabled>true</enabled><type>NetCDF</type><url>file:' + netcdfFile + '</url></coverageStore>',)
print(r_create_coveragestore.content)

# zip the nc file into a zip
zfile = sys.path[0]+'/../outputFiles/data.zip'
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
layers= cat.get_layers()
# r_get_layers =session.get(geoserver_url+'/rest/workspaces/' + workspace  +'/layers')
# layers = r_get_layers.json()
# layers = layers['layers']['layer']

for layer in layers:
    layerName=layer.resource.name
    #GetStyleName
    layer.default_style=layerName

    #check if Style exists
    if cat.get_style(layer.default_style):
        cat.delete(cat.get_style(layer.default_style))
    f = open(sys.path[0]+'/../outputFiles/styles/'+layer.default_style+'.xml')
    cat.create_style(layer.default_style, f.read())
    cat.save(layer)
    #get coverage to activate time Dimension
    from geoserver.support import DimensionInfo
    coverage = cat.get_resource(layerName,projectname,workspace=workspace)
    timeInfo = DimensionInfo("time", "true", "LIST", None, "ISO8601", None)
    coverage.metadata = ({'time': timeInfo})
    cat.save(coverage)
print('App can be started with: '+cfg['frontend']['absolutePath']+'/index.html')
  