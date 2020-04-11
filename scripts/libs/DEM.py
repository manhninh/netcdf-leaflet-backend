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
from netCDF4 import Variable
import numpy as np


def getDEMArray(emptyArray, var, varDEMOFFSet, hIndex: int):
    DEMArray = emptyArray  # create Empty Array with Same _FillValue
    for t in range(len(var[:])):
        for y in range(len(var[t][hIndex][:])):
            for x in range(len(var[t][hIndex][y][:])):
                demOffset = int(varDEMOFFSet[t][y][x])  # Determine DEMOffset for specific cell
                if not isinstance(var[t][hIndex + demOffset][y][x], np.ma.core.MaskedConstant):  # exclude NaN Values
                    DEMArray[t][y][x] = var[t][hIndex + demOffset][y][x]
    return DEMArray
