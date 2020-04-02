# -*- coding: utf-8 -*-  
import numpy as np
import time

def bilinear_interpolation(img,scale):
    dst_cols=(int)(img.shape[0]*scale)
    dst_rows=(int)(img.shape[1]*scale)
    img_dst=np.zeros([dst_cols,dst_rows])
 
    for i in range(dst_cols):
        for j in range(dst_rows):
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


def getPixValue(value,minValue,maxValue,valueArray=None,colorArray=None):
    if(valueArray is None):
        per = (value - minValue)/(maxValue-minValue)
        rValue = int(255*per);
        return (rValue,0,0,255)
    else:
        if value<valueArray[0] :
            return colorArray[0]
        elif value>valueArray[len(valueArray)-1] :
            return colorArray[len(valueArray)-1]
        else:
            for i in range(len(valueArray)-1):
                if(value<=valueArray[i+1] and value>valueArray[i]):
                    return colorArray[i+1]

def getValueArray(min,max,count):
    array = []
    interval = (float)(max-min)/count
    for i in range(count):
        array.append(min+(i+1)*interval)
    return array
# 获取当前时间
get_now_milli_time = lambda: int(time.time() * 1000)
