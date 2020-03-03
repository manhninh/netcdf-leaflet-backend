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
# reference:
#   http://unidata.github.io/netcdf4-python/
#
# author: Elias Borngässer
#=======================================================================


import math,yaml,os,sys


def calculatePixelSize(latitude,pixelWidth,pixelHeight): #calculate Resolution in degrees when given resolution in meters
    r_earth = 6378.137  #radius of the earth in kilometer

    resX = (1/((2*math.pi/360) * r_earth * math.cos(latitude))) /1000* pixelWidth
    resY = (1 / ((2 * math.pi / 360) * r_earth)) / 1000 * pixelHeight#111 km / degree 
    return resX,resY

def readConf():
    import yaml
    with open(os.path.join(sys.path[0], "conf/config.yml"), 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        return cfg