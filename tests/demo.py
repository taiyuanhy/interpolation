# -*- coding: UTF-8 -*-  
from math import pow
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt
import json
import math
import convertor
from matplotlib import cm
from matplotlib import colors
import pykrige.kriging_tools as kt
from shapely.geometry import shape
from shapely.geometry import Point
from PIL import Image,ImageDraw

def pointValue(x,y,power,smoothing,xv,yv,values,maxPoint=100,distance=500000):
    nominator=0
    denominator=0
    count = 0
    for i in range(0,len(values)):
        dist = sqrt((x-xv[i])*(x-xv[i])+(y-yv[i])*(y-yv[i])+smoothing*smoothing);
        #If the point is really close to one of the data points, return the data point value to avoid singularities
        if(dist<0.0000000001):
            return values[i]
#         if(dist<distance):
#             count+=1
#         if(count>maxPoint):
#             break
        nominator=nominator+(values[i]/pow(dist,power))
        denominator=denominator+(1/pow(dist,power))
    #Return NODATA if the denominator is zero
    if denominator > 0:
        value = nominator/denominator
    else:
        value = 0
    return value

def invDist(xv,yv,XI,YI,values,xsize=100,ysize=100,power=2,smoothing=10):
    valuesGrid = np.zeros((ysize,xsize))
    for x in range(0,xsize):
        for y in range(0,ysize):
            valuesGrid[y][x] = pointValue(XI[y][x],YI[y][x],power,smoothing,xv,yv,values)
    return valuesGrid
    

# 处理数据
def processData(path):
    try:
        f = open(path, 'r')
        file_content = f.read()
        file_json = json.loads(file_content)
        coordDataX = []
        coordDataY = []
        coordData = []
        valueData = []
        for stationData in file_json:
#             print(stationData)
            coords = stationData["geo"]
            coords_array = coords.split(",")
#             new_coords =  convertor.wgs84ToWebMercator(coords_array)
            if stationData["value"]!=0:
                coordDataX.append((float)(coords_array[1]))
                coordDataY.append((float)(coords_array[0]))
                coordData.append(coords_array)
                valueData.append(stationData["value"])
        return {"coords":coordData,"xs":coordDataX,"ys":coordDataY,"value":valueData}
    finally:
        if f:
            f.close()

def getboundary(mask_path):
    boundaryfileobject = open(mask_path)
    jsonObj = json.load(boundaryfileobject)
    jsonObj = jsonObj['features'][0]
    boundary = shape(jsonObj['geometry'])
    boundaryfileobject.close()
    return boundary

def getPixValue(value):
    if(value<=50):
        return (67,206,23,1)
    elif(value>50 and value <=100):
        return (227,201,42,1)
    elif(value>100 and value <=150):
        return (239,156,34,1)
    elif(value>150 and value <=200):
        return (240,92,23,1)
    elif(value>200 and value <=300):
        return (240,49,14,1)
    elif(value>300 ):
        return (166,18,76,1)
    
def bilinear_interpolation(img,scale):
    dst_cols=(int)(img.shape[0]*scale)
    dst_rows=(int)(img.shape[1]*scale)
    img_dst=np.zeros([dst_cols,dst_rows])
 
    for i in range(dst_cols-1):
        for j in range(dst_rows-1):
            #坐标转换
            scr_x=(i+0.5)/scale-0.5
            scr_y=(j+0.5)/scale-0.5
 
            #整数部分
            int_x=int(scr_x)
            #小数部分
            float_x=scr_x-int_x
 
            int_y=int(scr_y)
            float_y=scr_y-int_y
 
 
            if int_x==img.shape[0]-1:
                int_x_p=img.shape[0]-1
            else:
                int_x_p=int_x+1
 
            if int_y==img.shape[1]-1:
                int_y_p=img.shape[1]-1
            else:
                int_y_p=int_y+1
            
 
            img_dst[i][j]=(1-float_x)*(1-float_y)*img[int_x][int_y]+(1-float_x)*float_y*img[int_x][int_y_p]+\
                          float_x*(1-float_y)*img[int_x_p][int_y]+float_x*float_y*img[int_x_p][int_y_p]
 
    return img_dst


if __name__ == "__main__":
    power=2
    smoothing=0.2
    interval=0.5
    path = '../data/2019-05-13-10.json'
    mask_path = '../data/China.geojson'
    print('reading data......')
    data = processData(path);
    boundary = getboundary(mask_path)
    #Creating some data, with each coodinate and the values stored in separated lists
    xs = data["xs"]
    ys = data["ys"]
    values = data["value"]
    xs_origin = xs[:]
    ys_origin = ys[:]
    zs = data["value"]
    xmin = 73
    xmax = 135.5
    ymin = 17
    ymax = 55
    no_data = -999.
    #Creating the output grid (100x100, in the example)
    gridx = np.arange(xmin,xmax, interval)
    gridy = np.arange(ymin,ymax, interval)
    XI, YI = np.meshgrid(gridx, gridy)
    
    print('calculating grid......')
    #Creating the interpolation function and populating the output matrix value
    z_rh = invDist(xs_origin,ys_origin,XI, YI,values,len(gridx),len(gridy),power,smoothing)
    
    xcount = 0
    ycount = 0
    for x in gridx:
        for y in gridy:
            point = Point(x,y)
            polygon = point.buffer(0.5,cap_style=3)
            if not polygon.intersects(boundary):
                z_rh[ycount][xcount] = no_data
            else:
                if not polygon.within(boundary):
                    z_rh[ycount][xcount] = -100-z_rh[ycount][xcount] 
            ycount+=1
        xcount +=1
        ycount = 0
    
    print('writing result......')
    filename='../data/pm25.asc'
    kt.write_asc_grid(gridx, gridy, z_rh, filename,2)
    print('finished')
    
    
    print ('start drawing image....')
    scale = 800/z_rh.shape[1]
    result = bilinear_interpolation(z_rh,scale)
    imgWidth = result.shape[1]
    imgHeight = result.shape[0]
    img = Image.new("RGB",(imgWidth,imgHeight))
    draw = ImageDraw.Draw(img)
    for i in range(imgWidth):
        for j in range(imgHeight):
            draw.point((i, imgHeight-j), fill=getPixValue(result[j,i]))
    img.save('aqi.png')
    # make a color map of fixed colors
#     cmap = colors.ListedColormap(['green','yellow','orange','red','purple','grey'])
#     bounds=[0,50,100,150,200,300,1000]
#     norm = colors.BoundaryNorm(bounds, cmap.N)

    # Plotting the result
#     n = plt.normalize(0.0, 100.0)
#     plt.subplot(1,1,1)
#     plt.pcolor(XI, YI, z_rh,cmap=cm.jet)
# #     plt.scatter(xs_origin, ys_origin, 100, zs, cmap=cm.jet)
#     plt.title('IDW')
#     plt.xlim(xmin,xmax)
#     plt.ylim(ymin,ymax)
#     plt.colorbar()
# 
#     plt.show()