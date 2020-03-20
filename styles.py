from jinja2 import Environment, PackageLoader, select_autoescape
import sys,utils

cfg=utils.readConf()

env = Environment(
    loader=PackageLoader('styles', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
def createStyle(styleName,minValue,maxValue):
    min_color=cfg['styles']['DefaultMinColor']
    max_color=cfg['styles']['DefaultMaxColor']
    #Looking up if custom style defined in Config

    if styleName in cfg['styles']['customColors']:
        min_color=cfg['styles']['customColors'][styleName]['minColor']
        max_color=cfg['styles']['customColors'][styleName]['maxColor']
    if styleName in cfg['styles']['customValues']:
        minValue=cfg['styles']['customValues'][styleName]['minValue']
        maxValue=cfg['styles']['customValues'][styleName]['maxValue']     
    template = env.get_template('style.j2')
    parsed_template=template.render(name=styleName,minValue=minValue,maxValue=maxValue,colorMin=min_color,colorMax=max_color)
    with open(sys.path[0]+'/outputFiles/styles/'+styleName+'.xml', "w") as fh:
        fh.write(parsed_template)
    
