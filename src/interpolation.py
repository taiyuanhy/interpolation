# -*- coding: utf-8 -*-  
import sys ,os
import numpy as np
import pandas as pd
from math import pow
from math import sqrt
import pykrige.kriging_tools as kt
from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import json
from PIL import Image,ImageDraw
import convertor
from shapely.geometry import shape
from shapely.geometry import Point
sys.path.append('../src/')
import idw2 as idw 
import kriging as kriging 
import util


def prepareData(datalist,extent=None):
	print 'reading data...'
	lonlist = []
	latlist = []
	lonlatlist = []
	valuelist = []
	for data in datalist:
	#     if(data[2]!=0):
	#     coords = convertor.wgs84ToWebMercator(coords)
	    lonlist.append(data[1])
	    latlist.append(data[0])
	    lonlatlist.append([data[1],data[0]])
	    valuelist.append(data[2])
	    
	if extent is None:
	    extent= [min(lonlist),max(lonlist),min(latlist),max(latlist)]
	print(extent)
	return {'xList':lonlist,'yList':latlist,'xyList':lonlatlist,'valueList':valuelist,'extent':extent }

def interpolateIdw(xyList,valuelist,extent,gridSize,power=2,maxPoints=1e10,maxDistance=1e10):
    print 'interpolating idw...'
    z_rh = idw.interpolate(xyList,valuelist,extent,gridSize,power,maxPoints,maxDistance)
    return z_rh
def interpolateKriging(lonlist, latlist, valuelist,extent,gridSize,variogram_model='spherical',verbose=False, enable_plotting=False, n_closest_points = None):
    print 'interpolating kriging...'
    z_rh = kriging.interpolate(lonlist,latlist,valuelist,extent,gridSize,variogram_model,verbose, enable_plotting, n_closest_points)
    return z_rh

def drawImage(z_rh,imageSize,outputPath,minValue,maxValue,valueArray=None,colorArray=None):
    print 'start drawing image....'
    scale = imageSize/z_rh.shape[1]
    result = util.bilinear_interpolation(z_rh,scale)
    # result = z_rh
    imgWidth = result.shape[1]
    imgHeight = result.shape[0]
    img = Image.new("RGBA",(imgWidth,imgHeight))
    draw = ImageDraw.Draw(img)
    for i in range(imgWidth):
        for j in range(imgHeight):
            draw.point((i, imgHeight-1-j), fill=util.getPixValue(result[j,i],minValue,maxValue,valueArray,colorArray))
    img.save(outputPath)


##print hour+"_rh.acs saved."
##grid_array1=kt.read_asc_grid(filename, footer=0)
##print grid_array1
def drawPlot(gridSize,z_rh,extent):
    print "basemap_working..."
    alists=[]
    
    gridSizeX = gridSize
    gridSizeY = gridSizeX*(extent[3] - extent[2])/(extent[1]-extent[0])
    intervalX =(float)(extent[1] - extent[0])/gridSizeX
    intervalY =(float)(extent[3] - extent[2])/gridSizeY
    gridx = np.arange(extent[0],extent[1], intervalX)
    gridy = np.arange(extent[2],extent[3], intervalY)
    
    for lonnum in range(0,gridx.size):
        for latnum in range(0,gridy.size):
            list0=list([gridx[lonnum],gridy[latnum],z_rh[latnum][lonnum]])
            latnum=latnum+1
            alists.append(list0)
        lonnum=lonnum+1
    df1=pd.DataFrame(alists,columns=('1','2','3'))
    # 用来正常显示中文
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 用来正常显示负号
    plt.rcParams['axes.unicode_minus'] = True
    # 剔除无效值NAN
    df1 = df1.dropna(axis=0, how='any')
    #获取经纬度
    lat = np.array(df1["2"][:])
    lon = np.array(df1["1"][:])
    rhvalue = np.array(df1["3"][:], dtype=float)
    # 画图
    fig = plt.figure(figsize=(16, 9))
    plt.rc('font', size=15, weight='bold')
    ax = fig.add_subplot(111)
    # 添加标题
    # plt.title(hour[0:4]+u'年'+hour[4:6]+u'月'+hour[6:8]+u'日'+hour[8:10]+u'时'+u'中国AQI分布', size=25, weight='bold')
    # 创建底图,等经纬度投影
    mp = Basemap(llcrnrlon=extent[0], llcrnrlat=extent[2],
                 urcrnrlon=extent[1], urcrnrlat=extent[3],
                 projection='cyl', resolution='h')
    # 添加海岸线
    mp.drawcoastlines()
    # 添加国家行政边界
    mp.drawcountries()
    # 读取中国行政区边界
    mp.readshapefile('../data/gadm36_CHN_shp/gadm36_CHN_1',
                      'states',drawbounds=True)
    # 设置colorbar中颜色间隔个数
    ##levels = np.linspace(np.min(rhvalue), np.max(rhvalue), 20)
    # levels = np.linspace(0, np.min(rhvalue), np.max(rhvalue),endpoint=False, retstep=False, dtype=None)
    # 设置颜色表示数值大小
    cf = mp.scatter(lon, lat, rhvalue, c=rhvalue, cmap='jet', alpha=1)#alpha=0.75
    # 设置上下标以及单位的希腊字母
    cbar = mp.colorbar(cf, location='right', format='%d', size=0.3,
                       ticks=np.linspace(0, np.min(rhvalue), np.max(rhvalue),endpoint=False, retstep=False, dtype=None))#,label='AQI'
    #ticks=np.linspace(np.min(rhvalue), np.max(rhvalue), 10),
    #label='$\mathrm{PM}_{2.5}$($\mu$g/$\mathrm{m}^{3}$)'
    # plt.savefig('Hour_map_'+hour+'_AQI.png')
    plt.show()
    print "OK."
if __name__ == '__main__':
    
    data_path ='../data/pm25.json'
    config = {}
    #格网大小
    gridSize=50
    #数据展示范围
    extent = [73,135.5,17,55]
    #最大临近点
    maxPoints = 10
    #距离幂值 1-曼哈顿距离 2-欧氏距离
    power=2
    #搜索半径
    maxDistance=5
    #图片像素
    imageSize = 800
    colorArray = [(67,206,23,255),(227,201,42,255),(239,156,34,255),(240,92,23,255),(240,49,14,255),(166,18,76,255)]
    valueArray = [50,100,150,200,300]
    interpolateConfig = prepareData(data_path,extent)
    result = interpolateIdw(interpolateConfig['xyList'],interpolateConfig['valueList'],interpolateConfig['extent'],gridSize,power,maxPoints)
#     result = interpolateKriging(interpolateConfig['xList'],interpolateConfig['yList'],interpolateConfig['valueList'],interpolateConfig['extent'],gridSize,verbose=False, enable_plotting=False, n_closest_points = maxPoints)
    print('min:',np.min(result),'max:', np.max(result))
    drawImage(result,imageSize,'aqi.png',minValue,maxValue,valueArray,colorArray)
    drawPlot(gridSize ,result,extent)