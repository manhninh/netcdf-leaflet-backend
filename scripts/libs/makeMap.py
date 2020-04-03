from jinja2 import Environment, PackageLoader, select_autoescape
import sys,os
from shutil import copy
import pathlib
from . import utils,styles
import logging

env = Environment(
    loader=PackageLoader('libs', '../../templates'),
    autoescape=select_autoescape(['html', 'js','xml'])
)
overlays=[]
heights=[]
layers=[]

cfg=utils.cfg
projectName=cfg['general']['projectName']
workspaceName=projectName

def createMap(SimDate,SimTime,SimDurationMinus1,TimeInterval,Latitude,Longitude):
    #Create ProjectFolder
    if not os.path.isdir(cfg['frontend']['path']+'/projects/'+projectName+'/'):
        pathlib.Path(cfg['frontend']['path']+'/projects/'+projectName+'/').mkdir(parents=True,exist_ok=True)
    template = env.get_template('utils.j2')
    parsed_template=template.render(SimDate=SimDate,SimTime=SimTime,SimDurationMinus1=SimDurationMinus1,TimeInterval=TimeInterval,Latitude=Latitude,Longitude=Longitude)
    path =cfg['frontend']['path']+'/projects/'+projectName+"/utils.js"
    with open(path, "w") as fh:
        fh.write(parsed_template)
    logging.info("JavascriptFile has been created: "+path)

def addOverlay(o_name,o_longname,hasHeights):
    o_objectName ='L.marker([0,0])' if hasHeights else o_name+'Layer'
    overlays.append({"longname":o_longname,"objectName":o_objectName})

def addHeight(h_name,h_longname):
    heights.append({"name":h_name,"longname":h_longname})

def addLayer(l_name,l_mappingName,minValue,maxValue,unit):
    l_MappingName =l_mappingName if l_mappingName!="" else l_name
    layers.append({"name":l_name,"mappingName":l_MappingName})
    #Generate Style and prepareLegendControl
    styles.createStyle(l_name,minValue,maxValue,l_MappingName,unit)

def addHeightLayer(l_name,l_height,l_longName,minValue,maxValue,unit):
    addLayer(l_name,l_longName+'-'+l_height,minValue,maxValue,unit)

def _createLegend():
    styles.createLegend()

def _createOverlays():
    template = env.get_template('overlays.j2')
    parsed_template=template.render(heights=heights,overlays=overlays,layers=layers,url=cfg['geoserver']['url'],workspaceName=workspaceName) #use unmodified url from configfile
    path=cfg['frontend']['path']+'/projects/'+projectName+'/overlays.js'
    with open(path, "w") as fh:
        fh.write(parsed_template)
    logging.info("JavascriptFile has been created: "+path)
def _createProjectHandling():
    template = env.get_template('projectHandling.j2')
    #Delete Unused Static Files and getting List of available projects
    if 'cleanup' in cfg['frontend'] and not cfg['frontend']['cleanup']==False:
        projects=utils.cleanupProjects([projectName])
    else:
        projects=utils.getFrontendDirs()
    parsed_template=template.render(projects=projects)
    path=cfg['frontend']['path']+'/projects/projectHandling.js'
    with open(path, "w") as fh:
        fh.write(parsed_template)
    logging.info("JavascriptFile has been created: "+path)

def finalizeMap():
    _createOverlays()
    _createLegend()
    _createProjectHandling()
    copy(cfg['frontend']['path']+'/src/index.html',cfg['frontend']['path']+'/projects/'+projectName+'/')


    