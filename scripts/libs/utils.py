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



def _readConf():
    if 'CONFIGFILE' in os.environ:
        with open(os.environ['CONFIGFILE'], 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
    else:
        logging.warning("No ConfigFile specified (export CONFIGFILE), using default one")
        if os.path.exists("./config.yml"):
            cfg = yaml.safe_load("./config.yml")
        else:
            logging.error("Could not find Configfile")
            sys.exit
    if 'GEOSERVER_PASSWORD' in os.environ:
        cfg['geoserver']['password']=os.environ['GEOSERVER_PASSWORD']
    else:
        cfg['geoserver']['password']='geoserver'
        logging.warning("No Geoserver Password specified (export GEOSERVER_PASSWORD), using default one")
    #Overwrite Config Vars
    if 'PROJECTNAME' in os.environ:
        cfg['general']['projectName']=os.environ['PROJECTNAME']
    if 'INPUTFILE' in os.environ:
        cfg['general']['inputFile']=os.environ['INPUTFILE']

    # Optional Vars
    if not 'workdir' in cfg['general']:
        cfg['general']['workdir']='.' # default config
    if not 'frontend' in cfg or not 'path' in cfg['frontend']:
        if not 'frontend' in cfg:
            cfg['frontend']={}
        cfg['frontend']['path']=cfg['general']['workdir'] +'/frontend/app'# default config
    if not os.path.exists(cfg['frontend']['path']):
        logging.error('Frontendpath: '+cfg['frontend']['path']+' does not exist')
        sys.exit(1)
    if not 'logLevel' in cfg['general']:
        cfg['general']['logLevel']='INFO' # default config
    logging.getLogger().setLevel(cfg['general']['logLevel'])
    return cfg
cfg=_readConf()

def checkConnection(geoserver_url:str, user:str, password:str):
    session = requests.Session()
    session.auth = (cfg['geoserver']['user'], cfg['geoserver']['password'])
    try: 
        if session.get(geoserver_url):
            logging.info("Server available at: "+geoserver_url)
            return False,geoserver_url
    except:
        logging.warning("Could not establish connection to Geoserver "+geoserver_url)
        if geoserver_url.find('localhost')>=0:
            geoserver_url=geoserver_url.replace('localhost','host.docker.internal') #Is Script Running inside Container?
            try:
                if session.get(geoserver_url):
                    logging.info("Server available at: "+geoserver_url)
                    return False,geoserver_url
            except:
                logging.error("Could not establish connection to Geoserver "+geoserver_url)
        else:
            logging.error("No more options, program will abort")
    return True,""
()
def getFrontendDirs():
    for _r, dirs, _f in os.walk(cfg['frontend']['path']+'/projects/'):
        print(dirs)
    return dirs

def cleanupProjects(ignore):
    error,geoserver_url=checkConnection(cfg['geoserver']['url']+ "/rest/",cfg['geoserver']['user'],cfg['geoserver']['password'])
    projects=[]
    if error:
        logging.warning("Could not establish connection to Geoserver, projectHandling may not working")
        return projects
    cat=Catalog(geoserver_url, "admin", "geoserver")
    workspaces=[o.name for o in cat.get_workspaces()]
    dirs=getFrontendDirs()
    for d in dirs:
        if d not in workspaces and d not in ignore:
            shutil.rmtree(cfg['frontend']['path']+'/projects/'+d)
            logging.info("Deleted Frontend Folder for Project "+d)
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
