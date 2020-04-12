#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# =======================================================================
# name: utils.py
#
# description:
#   General methods used in main scripts
#
# author: Elias Borngässer
# =======================================================================

"""General methods used in main scripts.

name:   utils.py
author: Elias Borngässer
"""

import math
import yaml
import os
import sys
import shutil
import logging
import requests
from urllib.request import urlopen
from geoserver.catalog import Catalog



def _readConf():
    """Reads Config File specified in main.sh, if no configFile specified using ./config.yml.

    Returns:
        [dict] -- [Dictionary, containing global vars]
    """
    if 'CONFIGFILE' in os.environ:
        _cfgFile = os.environ['CONFIGFILE']
    elif os.path.exists("./config.yml"):
        logging.warning("No ConfigFile specified (export CONFIGFILE), using default one")
        _cfgFile = "./config.yml"
    else:
        logging.error("Could not find Configfile")
        sys.exit(1)
    with open(_cfgFile, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    if 'GEOSERVER_PASSWORD' in os.environ:
        cfg['geoserver']['password'] = os.environ['GEOSERVER_PASSWORD']
    else:
        cfg['geoserver']['password'] = 'geoserver'
        logging.warning("No Geoserver Password specified (export GEOSERVER_PASSWORD), using default one")
    # Overwrite Config Vars
    if 'PROJECTNAME' in os.environ:
        cfg['general']['projectName'] = os.environ['PROJECTNAME']
    if 'INPUTFILE' in os.environ:
        cfg['general']['inputFile'] = os.environ['INPUTFILE']

    # Optional Vars
    if 'nDigits' not in cfg['styles']:
        cfg['styles']['nDigits'] = 2
    if 'workdir' not in cfg['general']:
        cfg['general']['workdir'] = '.'  # default config
    if 'frontend' not in cfg or 'path' not in cfg['frontend']:
        if 'frontend' not in cfg:
            cfg['frontend'] = {}
        cfg['frontend']['path'] = cfg['general']['workdir'] + '/frontend/app'  # default config
    if not os.path.exists(cfg['frontend']['path']):
        logging.error('Frontendpath: ' + cfg['frontend']['path'] + ' does not exist')
        sys.exit(1)
    if 'logLevel' not in cfg['general']:
        cfg['general']['logLevel'] = 'INFO'  # default config
    logging.getLogger().setLevel(cfg['general']['logLevel'])
    return cfg


cfg = _readConf()


def checkConnection(geoserver_url: str, user: str, password: str):
    """Trys to connect to a secure Url.

    Returns:
        [bool] -- [Determines if connection could be established]
    """
    session = requests.Session()
    session.auth = (cfg['geoserver']['user'], cfg['geoserver']['password'])
    try:
        if session.get(geoserver_url):
            logging.info("Server available at: " + geoserver_url)
            return False, geoserver_url
    except BaseException:
        logging.warning("Could not establish connection to Geoserver " + geoserver_url)
        if geoserver_url.find('localhost') >= 0:
            geoserver_url = geoserver_url.replace('localhost', 'host.docker.internal')  # Is Script Running inside Container?
            try:
                if session.get(geoserver_url):
                    logging.info("Server available at: " + geoserver_url)
                    return False, geoserver_url
            except BaseException:
                logging.error("Could not establish connection to Geoserver " + geoserver_url)
        else:
            logging.error("No more options, program will abort")
    return True, ""


()


def getFrontendDirs():
    """[Retrieving list of Frontend Directories]

    Returns:
        [array] -- [List of Frontend Directories]
    """
    for _r, dirs, _f in os.walk(cfg['frontend']['path'] + '/projects/'):
        return dirs


def cleanupProjects(ignore):
    """[Deleting workspaces at geoserver, which haven't a frontend Directory with the same name]

    Returns:
        [array] -- [List of projects that do exist]
    """
    error, geoserver_url = checkConnection(cfg['geoserver']['url'] + "/rest/", cfg['geoserver']['user'], cfg['geoserver']['password'])
    projects = []
    if error:
        logging.warning("Could not establish connection to Geoserver, projectHandling may not working")
        return projects
    cat = Catalog(geoserver_url, "admin", "geoserver")
    workspaces = [o.name for o in cat.get_workspaces()]
    dirs = getFrontendDirs()
    for d in dirs:
        if d not in workspaces and d not in ignore:
            shutil.rmtree(cfg['frontend']['path'] + '/projects/' + d)
            logging.info("Deleted Frontend Folder for Project " + d)
        else:
            projects.append(d)
    return projects


def addGridMappingVars(var, locationLat:float, locationLon:float, rotation:float):
    """[adds grid Mapping Vars to a given Variable, that can be handled by Geoserver]

    Returns:
        [NetCDF-Variable] -- [returns variable with added grid#_mapping_information]
    """
    var.grid_mapping_name = "mercator"
    var.standard_parallel = 0.0
    var._CoordinateTransformType = "Projection"
    var._CoordinateAxisTypes = "GeoX GeoY"
    var.spatial_ref = 'PROJCS["Hotine_Oblique_Mercator_Azimuth_Center",GEOGCS["GCS_WGS_1984",DATUM["D_unknown",SPHEROID["WGS84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Hotine_Oblique_Mercator_Azimuth_Center"],PARAMETER["latitude_of_center",' + str(locationLat) + '],PARAMETER["longitude_of_center",' + str(locationLon) + '],PARAMETER["rectified_grid_angle",' + str(-rotation) + '],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["m",1.0], AUTHORITY["EPSG","8011112"]]'
    return var
