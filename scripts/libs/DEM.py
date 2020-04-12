#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# =======================================================================
# name: DEM.py
#
# description:
#   Calculating cleared up 3D Array with DEMOffset
#
# author: Elias Borngässer
# =======================================================================
"""Calculating cleared up 3D Array with DEMOffset"""

from netCDF4 import Variable
import numpy as np


def getDEMArray(emptyArray, var, varDEMOFFSet, hIndex: int):
    """[3D Array] -- [masked 3D Array containing the DEM cleared up Values]
    
    Arguments:
        emptyArray {maskedArray} -- [masked Array with Same _Fillvalue as var]
        var {[4D Array]} -- [the Variable to get the Data from]
        varDEMOFFSet {[3D Array]} -- [The variable containing the DEMOffset Values]
        hIndex {int} -- [The desired height to received]
    
    Returns:
        [3D Array] -- [masked 3D Array containing the DEM cleared up Values]
    """
    DEMArray = emptyArray
    for t in range(len(var[:])):
        for y in range(len(var[t][hIndex][:])):
            for x in range(len(var[t][hIndex][y][:])):
                demOffset = int(varDEMOFFSet[t][y][x])  # Determine DEMOffset for specific cell
                if not isinstance(var[t][hIndex + demOffset][y][x], np.ma.core.MaskedConstant):  # exclude NaN Values
                    DEMArray[t][y][x] = var[t][hIndex + demOffset][y][x]
    return DEMArray
