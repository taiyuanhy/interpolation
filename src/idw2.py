# -*- coding: utf-8 -*-  
import sys ,os
import numpy as np
import pandas as pd
from math import pow
from math import sqrt
import json
from scipy.spatial import cKDTree as KDTree

def pointValue(x,y,values,maxDistance,smoothing,distances, ix ):
    nominator=0
    denominator=0
#     count = 0
    for i in range(0,len(distances)):
        dist = distances[i]+smoothing*smoothing;
        #If the point is really close to one of the data points, return the data point value to avoid singularities
        if(dist<0.0000000001):
            return values[ix[i]]
        if(dist>maxDistance):
            continue
#         if(dist<distance):
#             count+=1
#         if(count>maxPoint):
#             break
        nominator=nominator+(values[ix[i]]/dist)
        denominator=denominator+(1/dist)
    #Return NODATA if the denominator is zero
    if denominator > 0:
        value = nominator/denominator
    else:
        value = 0
    return value

def invDist(xylist,values,gridList,XI,YI,maxPoints=8,maxDistance=1e10,power=2,smoothing=10):
    xsize = XI.shape[0]
    ysize = XI.shape[1]
    #行数列数
    valuesGrid = np.zeros((xsize,ysize))
    kdtree =  KDTree( xylist, leafsize=10)
    if(maxPoints> len(values)):
        maxPoints = len(values)
    distances, ix = kdtree.query( gridList, k=maxPoints, eps=0,p=power)
    for x in range(0,xsize):
        for y in range(0,ysize):
            valuesGrid[x][y] = pointValue(gridList[y+x*ysize][0],gridList[y+x*ysize][1],values,maxDistance,smoothing,distances[y+x*ysize], ix[y+x*ysize] )
    return valuesGrid

def interpolate(xylist,valuelist,extent,gridSize,power=2,maxPoints=8,maxDistance=1e10,smoothing=0.2):
    gridSizeX = gridSize
    gridSizeY = gridSizeX*(extent[3] - extent[2])/(extent[1]-extent[0])
    intervalX =(float)(extent[1] - extent[0])/gridSizeX
    intervalY =(float)(extent[3] - extent[2])/gridSizeY
    gridx = np.arange(extent[0],extent[1], intervalX)
    gridy = np.arange(extent[2],extent[3], intervalY)
    XI, YI = np.meshgrid(gridx, gridy)
    gridList = []
    for i in range(len(gridy)):
        for j in range(len(gridx)):
            gridList.append([gridx[j],gridy[i]])
    z_rh = invDist(xylist,valuelist,gridList,XI, YI,maxPoints,maxDistance,power,smoothing)
    return z_rh

def demo():
    data_path ='../data/aqi_20200312.txt'
    fileobject = open(data_path)
    datalist= json.load(fileobject)
    lonlist = []
    latlist = []
    lonlatlist = []
    valuelist = []
    for data in datalist:
        lonlist.append(data[0])
        latlist.append(data[1])
        lonlatlist.append([data[0],data[1]])
        valuelist.append(data[2])
    extent = [73,135.5,17,55]
#     extent = [min(lonlist),max(lonlist),min(latlist),max(latlist)]
    interpolate(lonlatlist,valuelist,extent,50,2)
    
if __name__ == '__main__':
    demo()