#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#=======================================================================
# name: styles.py
#
# description:
#   Handles style and legend creation
#
# author: Elias Borngässer
#=======================================================================
from jinja2 import Environment, PackageLoader, select_autoescape
import sys,logging,os
from string import digits
from . import utils

cfg =utils.cfg
projectName=cfg['general']['projectName']

env = Environment(
    loader=PackageLoader('libs', '../../templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
styles=[]

def _generateValues(styles,minValue,maxValue,nClasses):
    values=[]
    nDigits=cfg['styles']['nDigits'] # Number of digits used for rounding
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
    varName=styleName.rstrip(digits)
    #Check if Style has own description in Config
    if varName in cfg['styles']['customStyles']:
        colors=cfg['styles']['customStyles'][varName]['colors']
        #Check if Style has custom Values
        if "values" in cfg['styles']['customStyles'][varName]:
            values=cfg['styles']['customStyles'][varName]['values']
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
    if not os.path.isdir(cfg['general']['workdir']+'/outputFiles/'+projectName+'/styles/'):
        os.mkdir(cfg['general']['workdir']+'/outputFiles/'+projectName+'/styles/')
    with open(cfg['general']['workdir']+'/outputFiles/'+projectName+'/styles/'+styleName+'.xml', "w") as fh:
        fh.write(parsed_template)



def createLegend():
    template = env.get_template('legend.j2')
    parsed_template=template.render(styles=styles)
    path =cfg['frontend']['path']+"/projects/"+projectName+"/legend.js"
    with open(path, "w") as fh:
        fh.write(parsed_template)
    logging.debug("JavascriptFile has been created: "+path)
    
