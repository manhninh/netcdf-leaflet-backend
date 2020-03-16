from jinja2 import Environment, PackageLoader, select_autoescape
import sys,utils

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
    with open(frontendPath+"/src/js/main.js", "w") as fh:
        fh.write(parsed_template)

def addOverlay(o_name,o_longname,hasHeights):
    o_objectName ='L.marker([0,0])' if hasHeights else o_name+'Layer'
    overlays.append({"longname":o_longname,"objectName":o_objectName})

def addHeight(h_name,h_longname):
    heights.append({"name":h_name,"longname":h_longname})

def addLayer(l_name,l_mappingName):
    l_MappingName =l_mappingName if l_mappingName!="" else l_name
    layers.append({"name":l_name,"mappingName":l_MappingName})

def addHeightLayer(l_name,l_height,l_longName):
    addLayer(l_name,l_longName+'-'+l_height)


def createOverlays():
    template = env.get_template('overlays.j2')
    parsed_template=template.render(heights=heights,overlays=overlays,layers=layers,url=geoserverURL,workspaceName=workspaceName)
    with open(frontendPath+'/src/js/overlays.js', "w") as fh:
        fh.write(parsed_template)