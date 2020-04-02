import pykrige.kriging_tools as kt
from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging
import numpy as np
import json
# -*- coding: utf-8 -*-  
def interpolate(lonlist, latlist, valuelist,extent,gridSize,variogram_model='spherical',verbose=False, enable_plotting=False, n_closest_points=None):
    minXY = [extent[0],extent[2]]
    maxXY = [extent[1],extent[3]]
    interval = (float)(maxXY[0]-minXY[0])/gridSize
    gridx = np.arange(minXY[0],maxXY[0], interval)
    gridy = np.arange(minXY[1],maxXY[1], interval)
    OK_rh = OrdinaryKriging(lonlist, latlist, valuelist, variogram_model=variogram_model,verbose=verbose, enable_plotting=enable_plotting)
    if(n_closest_points is not None):
        print('n_closest_points=',n_closest_points)
        z_rh, ss_rh = OK_rh.execute('grid', gridx, gridy, backend='loop', n_closest_points=n_closest_points)
    else:
        z_rh, ss_rh = OK_rh.execute('grid', gridx, gridy)
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
        valuelist.append(data[2])
    extent = [73,135.5,17,55]
#     extent = [min(lonlist),max(lonlist),min(latlist),max(latlist)]
    interpolate(lonlist,latlist,valuelist,extent,50,n_closest_points = 12)
    
if __name__ == '__main__':
    demo()