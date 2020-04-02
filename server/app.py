# coding: utf-8
import math
# import matplotlib.pyplot as plt
import json
import time
import os
from flask import Flask
from flask import request
import ssl
import requests
import json
import traceback
import sys
import numpy as np
sys.path.append('../src/')

import idw2 as idw 
import kriging as kriging 
import util
import interpolation

#全局取消证书验证
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
# logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
#                     level=logging.INFO)
logger = app.logger

outputPath = 'e:\\osmdownloader'
staticUrl = 'http://192.168.21.119:90/osmdata/'

@app.route('/')
def hello_world():
    logger.info('test')
    return 'osm downloader is running on port 5060'

@app.route('/interpolateData')
def interpolateData():
    logger.info('interpolateData...')
    method = request.args['method']
    dataUrl = request.args['dataUrl']
    gridSize = 100
#     colorArray = [(67,206,23,255),(227,201,42,255),(239,156,34,255),(240,92,23,255),(240,49,14,255),(166,18,76,255)]
    valueField = request.args['valueField']
    maxPoints = None
    power = 2
    extent = None
    valueArray = None
    imageSize = 800
    if request.args.has_key('maxPoints'):
        maxPoints = int(request.args['maxPoints'])
    if request.args.has_key('gridSize'):
        gridSize = int(request.args['gridSize'])
    if request.args.has_key('extent'):
        extent = request.args['extent']
#     if request.args.has_key('valueArray'):
#         valueArray = request.args['valueArray']
    if request.args.has_key('power'):
        power = int(request.args['power'])
#     if request.args.has_key('colorArray'):
#         colorArray = request.args['colorArray']
    try:    
        r0 = requests.get(dataUrl)
        geojsonContent = r0.content
        geojsonObj = json.loads(geojsonContent)
        dataList = []
    #     minValue = sys.maxint
    #     maxValue = -sys.maxint
        for feature in geojsonObj['features']:
            data = []
            coords = feature['geometry']['coordinates']
            value = float(feature['properties'][valueField])
            data = [coords[0],coords[1],value]
            dataList.append(data)
#         if value>maxValue:
#             maxValue = value
#         if value<minValue:
#             minValue = value
    
    
        interpolateConfig = interpolation.prepareData(dataList,extent)
        outputFileName = method+'_'+ str(util.get_now_milli_time())+'.png'
        outputObj = {'success':1,'extent':interpolateConfig['extent']}
        
#         if(valueArray is None):
#             valueArray = util.getValueArray(minValue,maxValue,len(colorArray))
        if method == 'idw':
            if(maxPoints is None):
                maxPoints = 12
            result = interpolation.interpolateIdw(interpolateConfig['xyList'],interpolateConfig['valueList'],interpolateConfig['extent'],gridSize,power,maxPoints)
        elif method == 'kriging':
            result = interpolation.interpolateKriging(interpolateConfig['xList'],interpolateConfig['yList'],interpolateConfig['valueList'],interpolateConfig['extent'],gridSize,verbose=False, enable_plotting=False, n_closest_points = maxPoints)
        minValue = np.min(result)
        maxValue = np.max(result)
        print('min:',minValue,'max:', maxValue)
        interpolation.drawImage(result,imageSize,outputPath+os.sep+outputFileName,minValue,maxValue)
        outputUrl = staticUrl +outputFileName
        outputObj['imgaeUrl'] = outputUrl
        return json.dumps(outputObj)
    except Exception, e:
        traceback.print_exc()
        return json.dumps({"message":str(e),"success":0})

if __name__ != '__main__':
#     log_handler.set_logger(logger)
    logger.info('server started by gunicorn')

if __name__ == '__main__':
#     print(111)
#     log_handler.set_logger(logger)
    logger.info('server started')
    app.run(host="0.0.0.0", port=5060)