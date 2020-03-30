#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#=======================================================================
# name: utils.py
#
# category: python script
# Part 1
# description:
#   General methods used in main scripts
#
# author: Elias Borngässer
#=======================================================================


import math,yaml,os,sys,shutil,logging,requests
from urllib.request import urlopen
from geoserver.catalog import Catalog


def readConf():
    import yaml
    if 'CONFIGFILE' in os.environ:
        with open(os.environ['CONFIGFILE'], 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
    else:
        logging.error("No ConfigFile specified (export CONFIGFILE)")
        sys.exit(1)
    #Overwrite Config Vars
    if 'PROJECTNAME' in os.environ:
        cfg['general']['projectName']=os.environ['PROJECTNAME']
    if 'INPUTFILE' in os.environ:
        cfg['general']['inputFile']=os.environ['INPUTFILE']

    # Optional Vars
    if 'workdir' in cfg['general']:
        workdir=cfg['general']['workdir']
    else:
        workdir='.' # default config
    if 'logLevel' in cfg['general']:
        logLevel=cfg['general']['logLevel']
    else:
        logLevel='WARN' # default config
    if 'path' in cfg['frontend']:
        frontend_path=cfg['frontend']['path']
    else:
        frontend_path=workdir+'/frontend/app' #default config
    
    #Check if Config File is correct and Paths are existing
    filePaths=[cfg['general']['inputFile'],frontend_path]
    for path in filePaths:
        if not os.path.exists(path):
            logging.error('Path: '+path+' does not exist')
            sys.exit(1)
        return cfg, workdir, frontend_path, logLevel

cfg, workdir, frontend_path, logLevel=readConf()
def checkURL(geoserver_url:str):
    try: 
        if requests.get(geoserver_url):
            logging.info("Server available at: "+geoserver_url)
            return False,geoserver_url
    except:
        logging.warn("Could not establish connection to Geoserver "+geoserver_url)
        if geoserver_url.find('localhost')>=0:
            geoserver_url=geoserver_url.replace('localhost','host.docker.internal') #Is Script Running inside Container?
            try:
                if requests.get(geoserver_url):
                    logging.info("Server available at: "+geoserver_url)
                    return False,geoserver_url
            except:
                logging.error("Could not establish connection to Geoserver "+geoserver_url)
        else:
            logging.error("No more options, program will abort")
    return True,""
def cleanupProjects(ignore):
    error,geoserver_url=checkURL(cfg['geoserver']['url'])
    projects=[]
    if error:
        logging.warn("Could not establish connection to Geoserver, projectHandling may not working")
        return projects
    cat=Catalog(geoserver_url+ "/rest/", "admin", "geoserver")
    workspaces=[o.name for o in cat.get_workspaces()]
    for _r, dirs, _f in os.walk(frontend_path+'/projects/'):
        for d in dirs:
            if d not in workspaces and d not in ignore:
                shutil.rmtree(frontend_path+'/projects/'+d)
            else:
                projects.append(d)
    return projects

def addGridMappingVars(var,locationLat,locationLon,rotation):
    var.grid_mapping_name= "mercator"
    var.standard_parallel= 0.0
    var._CoordinateTransformType= "Projection"
    var._CoordinateAxisTypes= "GeoX GeoY"
    var.spatial_ref= 'PROJCS["Hotine_Oblique_Mercator_Azimuth_Center",GEOGCS["GCS_WGS_1984",DATUM["D_unknown",SPHEROID["WGS84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Hotine_Oblique_Mercator_Azimuth_Center"],PARAMETER["latitude_of_center",'+str(locationLat)+'],PARAMETER["longitude_of_center",'+str(locationLon)+'],PARAMETER["rectified_grid_angle",'+str(-rotation)+'],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["m",1.0], AUTHORITY["EPSG","8011112"]]'
    return var
