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
cfg=utils.readConf()
projectname=cfg['general']['project_name']
workspace=projectname# Has no own configuration because layers wouldn't be unique if multiple projects in one workspace
geoserver_url=cfg['geoserver']['url']
srs=cfg['general']['targetEPSG']
uploadTimeOut=cfg['geoserver']['uploadTimeOut']
logging.getLogger().setLevel(cfg['general']['log_level'])

#prepare Session (Still needed to uploaded NetCDF Datastore (not supported by Geoserver Library))
session = requests.Session()
session.auth = ('admin', 'geoserver')

def checkSession(geoserver_url:str):
    try: 
        if session.get(geoserver_url):
            logging.info("Server available at: "+geoserver_url)
            return
    except:
        logging.warn("Could not establish connection to Geoserver "+geoserver_url)
        if geoserver_url.find('localhost')>=0:
            geoserver_url=geoserver_url.replace('localhost','host.docker.internal') #Is Script Running inside Container?
            try:
                if session.get(geoserver_url):
                    logging.info("Server available at: "+geoserver_url)
                    return
            except:
                logging.error("Could not establish connection to Geoserver "+geoserver_url)
        else:
            logging.error("No more options, program will abort")
    sys.exit() 

checkSession(geoserver_url)
cat=Catalog(geoserver_url+ "/rest/", "admin", "geoserver")

#Check if Config File is correct and NETCDF File existing
if not os.path.exists(workdir+'/outputFiles/'+projectname+'.nc'):
    logging.error('File '+workdir+'/outputFiles/'+projectname+'.nc does not exist')
    sys.exit()

headers_zip = {'content-type': 'application/zip'}
headers_xml = {'content-type': 'text/xml'}
netcdfFile=workdir+'/outputFiles/'+projectname+'.nc'


def checkUpload():
    passedTime=0
    while True:
        if cat.get_store(projectname,workspace=workspace):
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
if cat.get_store(projectname,workspace):
    cat.delete(cat.get_store(projectname,workspace=workspace),purge="all",recurse=True)
if cat.get_workspace(workspace):
    cat.delete(cat.get_workspace(workspace),purge="all",recurse=True)
cat.create_workspace(workspace,geoserver_url+'/'+workspace)

# zip the ncFile
zfile = workdir+'/outputFiles/data.zip'
logging.info('Writing Zipfile '+zfile)
output = zipfile.ZipFile(zfile, 'w')
output.write(netcdfFile, projectname + '.nc', zipfile.ZIP_DEFLATED )
output.close()

#upload zip file (creating coveragestore and layers automatically)
logging.info('Uploading '+zfile)
with open(output.filename, 'rb') as zip_file:
    r_create_layer = session.put(geoserver_url+'/rest/workspaces/' + workspace  + '/coveragestores/' + projectname  + '/file.netcdf',
        data=zip_file,
        headers=headers_zip)
logging.info('Upload Response: '+str(r_create_layer.status_code))
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
        coverage = cat.get_resource(layerName,projectname,workspace=workspace)
        timeInfo = DimensionInfo("time", "true", "LIST", None, "ISO8601", None)
        #coverage.native_crs=str(srs)+'='+coverage.native_crs
        #coverage.srs=8011112 #srs #32632 #8011113
        coverage.metadata = ({'time': timeInfo})
        cat.save(coverage)
logging.info('App can be started at: '+cfg['frontend']['absolutePath']+'/projects/'+projectname+'/index.html')

