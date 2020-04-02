# -*- coding: UTF-8 -*-  

import math
#经纬度转墨卡托坐标
def wgs84ToWebMercator(latlng):
    # list=ll_wl.split(',')
    lat=float(latlng[0])
    lng=float(latlng[1])
    x =  lng* 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y = y * 20037508.34 / 180
    return [x,y]
#墨卡托坐标转经纬度坐标
def webMercatorToWgs84(x,y):
    x=float(x)
    y=float(y)
    x=x/20037508.34*180
    y=y/20037508.34*180
    y=180/math.pi*(2*math.atan(math.exp(y*math.pi/180))-math.pi/2)
    return [x,y]
