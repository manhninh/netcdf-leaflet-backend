#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#=======================================================================
# name: list_project.py
#
# category: python script
# Part 1
# description:
#   List Project Folder and Workspaces in Geoserver
#
# author: Elias Borngässer
#=======================================================================

from libs import utils
import shutil, sys, os, logging
from geoserver.catalog import Catalog

cfg=utils.cfg


offline=False
error,geoserver_url= utils.checkConnection(cfg['geoserver']['url']+ "/rest/",cfg['geoserver']['user'], cfg['geoserver']['password'])
if error:
    logging.warning("Could not connect to geoserver, will only list folders")
    offline=True

#List Project Folders
for _r, dirs, _f in os.walk(cfg['frontend']['path']+'/projects/'):
    if len(dirs)==0:
        logging.info("No Frontend Folders found at "+cfg['frontend']['path']+'/projects/')
    for d in dirs:
        logging.info("Found Frontend Folder "+d)

#List Geoserver Workspaces 
if not offline:
    cat=Catalog(geoserver_url, cfg['geoserver']['user'], cfg['geoserver']['password'])
    workspaces=cat.get_workspaces()
    if len(workspaces)==0:
        logging.info("No workspaces found at Geoserver " + cfg['geoserver']['url'])
    else:
        for w in workspaces:   
            logging.info('Found workspace "'+w.name+'" at geoserver')






