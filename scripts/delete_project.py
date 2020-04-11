#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# =======================================================================
# name: delete_project.py
#
# description:
#   Delete Project Folder and Workspace in Geoserver
#
# author: Elias Borngässer
# =======================================================================

from libs import utils, makeMap
import shutil
import sys
import os
import logging
from geoserver.catalog import Catalog

cfg = utils.cfg
project = cfg['general']['projectName']

offline = False
error, geoserver_url = utils.checkConnection(cfg['geoserver']['url'] + "/rest/", cfg['geoserver']['user'], cfg['geoserver']['password'])
if error:
    logging.warning("Could not connect to geoserver, will only delete folders")
    offline = True

logging.info("Deleting Project " + project)
# Delete Project Folders
if os.path.isdir(cfg['frontend']['path'] + '/projects/' + project + '/'):
    shutil.rmtree(cfg['frontend']['path'] + '/projects/' + project)
    logging.info("Deleted Frontend folder " + project)
    makeMap.createProjectHandling()
    logging.info("Project Handling Updated")
else:
    logging.warning("Could not find Frontend folder " + cfg['frontend']['path'] + '/projects/' + project)


# Delete Geoserver Workspaces
if not offline:
    cat = Catalog(geoserver_url, cfg['geoserver']['user'], cfg['geoserver']['password'])
    if cat.get_workspace(project):
        cat.delete(cat.get_workspace(project), purge="all", recurse=True)
        logging.info("Deleted workspace " + project)
    else:
        logging.warning("Could not find workspace " + project)
