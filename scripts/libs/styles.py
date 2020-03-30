from jinja2 import Environment, PackageLoader, select_autoescape
import sys,logging,os
from . import utils

cfg ,workdir, frontend_path, _logLevel=utils.readConf()
projectName=cfg['general']['projectName']

env = Environment(
    loader=PackageLoader('libs', '../../templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
styles=[]

def _generateValues(styles,minValue,maxValue,nClasses):
    values=[]
    nDigits=2 # Number of digits uses for rounding
    values.append(round(minValue,nDigits))
    classStep=((maxValue-minValue)/(nClasses-1))
    for i in range(nClasses-2):
        values.append(round(minValue+classStep*(i+1),nDigits))
    values.append(round(maxValue,nDigits))
    return values

def _createColorMapping(colors,values):
    colorMapping=[]
    for i in range(len(colors)):
        colorMapping.append({"color":colors[i],"value":values[i]})
    return colorMapping
def createStyle(styleName,minValue,maxValue,layerMappingName,unit):

    #Check if Style has own description in Config
    if styleName in cfg['styles']['customStyles']:
        colors=cfg['styles']['customStyles'][styleName]['colors']
        #Check if Style has custom Values
        if "values" in cfg['styles']['customStyles'][styleName]:
            values=cfg['styles']['customStyles'][styleName]['values']
        else:
            values=_generateValues(styles,minValue,maxValue,len(colors))
    #Use Default Styleconfig
    else:
        colors=cfg['styles']['DefaultColors']
        values=_generateValues(styles,minValue,maxValue,len(colors))

    template = env.get_template('style.j2')


    #create StyleObject (used by Legend)
    style={"name":styleName,"colors":colors,"values":values,"layerMappingName":layerMappingName,"unit":unit}
    styles.append(style)

    colorMapping=_createColorMapping(colors,values)
    #create SLD Style which is used by Geoserver
    parsed_template=template.render(styleName=styleName,colorMapping=colorMapping)
    if not os.path.isdir(workdir+'/outputFiles/styles/'):
        os.mkdir(workdir+'/outputFiles/styles/')
    with open(workdir+'/outputFiles/styles/'+styleName+'.xml', "w") as fh:
        fh.write(parsed_template)



def createLegend():
    template = env.get_template('legend.j2')
    parsed_template=template.render(styles=styles)
    path =frontend_path+"/projects/"+projectName+"/legend.js"
    with open(path, "w") as fh:
        fh.write(parsed_template)
    logging.info("JavascriptFile has been created: "+path)
    
