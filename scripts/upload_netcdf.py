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
import time

#get config variables
cfg, workdir,frontend_path,logLevel=utils.readConf()
projectName=cfg['general']['projectName']
workspace=projectName# Has no own configuration because layers wouldn't be unique if multiple projects in one workspace
# This could be fixed by using custom layernames (projectname-layername)

uploadTimeOut=cfg['geoserver']['uploadTimeOut']
logging.getLogger().setLevel(logLevel)

#prepare Session (Still needed to upload NetCDF Datastore (not supported by Geoserver Library))
session = requests.Session()
session.auth = ('admin', 'geoserver')

error,geoserver_url= utils.checkURL(cfg['geoserver']['url'])
if error:
    sys.exit()
cat=Catalog(geoserver_url+ "/rest/", "admin", "geoserver")

#Check if Config File is correct and NETCDF File existing
if not os.path.exists(workdir+'/outputFiles/'+projectName+'.nc'):
    logging.error('File '+workdir+'/outputFiles/'+projectName+'.nc does not exist')
    sys.exit()

headers_zip = {'content-type': 'application/zip'}
headers_xml = {'content-type': 'text/xml'}
netcdfFile=workdir+'/outputFiles/'+projectName+'.nc'


def checkUpload():
    passedTime=0
    while True:
        if cat.get_store(projectName,workspace=workspace):
            return
        elif (passedTime>uploadTimeOut):
            logging.error('TIMEOUT: Failed to upload NetCDF File')
            exit(1)
        else:
            time.sleep(1)
            passedTime+=1

#ensure AdvancedProjectionSetting is turned off (if not -> layers wont display layers correctly)
r_set_wms_options=session.put(geoserver_url+'/rest/services/wms/settings',
    data='<wms><metadata><entry key="advancedProjectionHandling">false</entry></metadata></wms>',
    headers=headers_xml)

# Delete old workspace and create new one
if cat.get_store(projectName,workspace):
    cat.delete(cat.get_store(projectName,workspace=workspace),purge="all",recurse=True)
if cat.get_workspace(workspace):
    cat.delete(cat.get_workspace(workspace),purge="all",recurse=True)
cat.create_workspace(workspace,geoserver_url+'/'+workspace)

# zip the ncFile
zfile = workdir+'/outputFiles/data.zip'
logging.info('Writing Zipfile '+zfile)
output = zipfile.ZipFile(zfile, 'w')
output.write(netcdfFile, projectName + '.nc', zipfile.ZIP_DEFLATED )
output.close()

#upload zip file (creating coveragestore and layers automatically)
logging.info('Uploading '+zfile)
with open(output.filename, 'rb') as zip_file:
    r_create_layer = session.put(geoserver_url+'/rest/workspaces/' + workspace  + '/coveragestores/' + projectName  + '/file.netcdf',
        data=zip_file,
        headers=headers_zip)
if r_create_layer.status_code==201:
    logging.info('Succecssfully uploaded Zipfile')
else:
    logging.error('TIMEOUT: Failed to upload NetCDF File')
    exit(1)
os.remove(output.filename)

#Wait until CoverageStore has been created
checkUpload()
#assign styles to created layers
layers= cat.get_layers()

for layer in layers:
    if layer.resource.workspace.name==workspace:
        #GetStyleName
        layerName=layer.resource.name
        #Set Stylename
        layer.default_style=layerName

        #create New Style from prebuild XML File
        f = open(workdir+'/outputFiles/styles/'+layer.default_style+'.xml')
        cat.create_style(layer.default_style, f.read(),workspace=workspace,overwrite=True)
        cat.save(layer)
        #get coverage to activate time Dimension
        from geoserver.support import DimensionInfo
        coverage = cat.get_resource(layerName,projectName,workspace=workspace)
        timeInfo = DimensionInfo("time", "true", "LIST", None, "ISO8601", None)
        coverage.metadata = ({'time': timeInfo})
        cat.save(coverage)
logging.info('App can be started at: '+cfg['frontend']['path']+'/projects/'+projectName+'/index.html')

