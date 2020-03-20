from jinja2 import Environment, PackageLoader, select_autoescape
import sys,utils,styles
import logging

env = Environment(
    loader=PackageLoader('makeMap', 'templates'),
    autoescape=select_autoescape(['html', 'js'])
)
overlays=[]
heights=[]
layers=[]

cfg=utils.readConf()
geoserverURL=cfg['geoserver']['url']
frontendPath=cfg['frontend']['absolutePath']
workspaceName=cfg['geoserver']['workspaceName']

def createMap(SimDate,SimTime,SimDurationMinus1,TimeInterval,Latitude,Longitude):
    template = env.get_template('main.j2')
    parsed_template=template.render(SimDate=SimDate,SimTime=SimTime,SimDurationMinus1=SimDurationMinus1,TimeInterval=TimeInterval,Latitude=Latitude,Longitude=Longitude)
    path =frontendPath+"/src/js/main.js"
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
    parsed_template=template.render(heights=heights,overlays=overlays,layers=layers,url=geoserverURL,workspaceName=workspaceName)
    path=frontendPath+'/src/js/overlays.js'
    with open(path, "w") as fh:
        fh.write(parsed_template)
    logging.info("JavascriptFile has been created: "+path)

def finalizeMap():
    _createOverlays()
    _createLegend()

    