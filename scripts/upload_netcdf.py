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
import sys, os
import logging
from geoserver.catalog import Catalog


#get config variables
cfg=utils.readConf()
projectname=cfg['general']['project_name']
workspace=cfg['geoserver']['workspaceName']
geoserver_url=cfg['geoserver']['url']
logging.getLogger().setLevel(cfg['general']['log_level'])

cat=Catalog(geoserver_url+ "/rest/", "admin", "geoserver")

#Check if Config File is correct and NETCDF File existing
if not os.path.exists(sys.path[0]+'/../outputFiles/'+projectname+'.nc'):
    logging.error('File '+sys.path[0]+'/../outputFiles/'+projectname+'.nc does not exist')
    exit
    
coveragestore=projectname
headers_zip = {'content-type': 'application/zip'}
headers_xml = {'content-type': 'text/xml'}
netcdfFile=sys.path[0]+'/../outputFiles/'+projectname+'.nc'

#prepare Session (Still needed to uploaded NetCDF Datastore (not supported by Geoserver Library))
session = requests.Session()
session.auth = ('admin', 'geoserver')

#assure AdvancedProjectionSetting is turned off (if not -> layers wont display layers correctly)
r_set_wms_options=session.put(geoserver_url+'/rest/services/wms/settings',
    data='<wms><metadata><entry key="advancedProjectionHandling">false</entry></metadata></wms>',
    headers=headers_xml)

#create Workspace if doesn't exist
if  not cat.get_workspace(workspace):
    cat.create_workspace(workspace,workspace)
#delete coveragestore with same Name if existing
if cat.get_store(coveragestore,workspace):
    cat.delete(cat.get_store(coveragestore,workspace),purge="all",recurse=True)

# zip the nc file into a zip
zfile = sys.path[0]+'/../outputFiles/data.zip'
output = zipfile.ZipFile(zfile, 'w')
output.write(netcdfFile, coveragestore + '.nc', zipfile.ZIP_DEFLATED )
output.close()

#upload zip file (creating coveragestore and layers automatically)
with open(output.filename, 'rb') as zip_file:
    r_create_layer = session.put(geoserver_url+'/rest/workspaces/' + workspace  + '/coveragestores/' + coveragestore  + '/file.netcdf',
        data=zip_file,
        headers=headers_zip)
logging.info('Upload Response: '+str(r_create_layer.status_code))
os.remove(output.filename)

#assign styles to created layers
layers= cat.get_layers()

for layer in layers:
    #GetStyleName
    layerName=layer.resource.name
    #Set Stylename
    layer.default_style=layerName

    #check if Style exists at Geoserver
    if cat.get_style(layer.default_style):
        cat.delete(cat.get_style(layer.default_style))
    #create New Style from prebuild XML File
    f = open(sys.path[0]+'/../outputFiles/styles/'+layer.default_style+'.xml')
    cat.create_style(layer.default_style, f.read())
    cat.save(layer)
    #get coverage to activate time Dimension
    from geoserver.support import DimensionInfo
    coverage = cat.get_resource(layerName,projectname,workspace=workspace)
    timeInfo = DimensionInfo("time", "true", "LIST", None, "ISO8601", None)
    coverage.metadata = ({'time': timeInfo})
    cat.save(coverage)
logging.info('App can be started at: '+cfg['frontend']['absolutePath']+'/index.html')
  