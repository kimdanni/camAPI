# -*- coding:utf-8 -*-
import cv2
import platform
import numpy as np
from datetime import datetime
import sys, os
from rdsType import *

from flask import Flask ,jsonify, request
from flask_cors import CORS
from flask import make_response

import json
import base64
import logging

import random

import timeit
from pathlib import Path 
from playsound import playsound
import pymysql
from datetime import datetime

app = Flask(__name__)
CORS(app)

file_path = 'catAns/catting.json'
mp3_path = 'catGtts/'

src = 0
thresh = 100
max_diff = 1500 # pixel 이 총 1500 개 정도 찍히면 그때 고양이라고 판단

#RDS info


def connect_RDS(hosted, username, password, database):
    try:
        conn = pymysql.connect(host=hosted,port=3306,user=username,passwd = password,db=database,
                          charset ='utf8')
        cursor = conn.cursor()

    except:
        logging.error("RDS에 연결되지 않았음")
        sys.exit(1)

    return conn, cursor


def motion_detect(pre_img1, pre_img2, pre_img3, thres, diff):
    # 이미지 영상을 읽어 밝기 값 차이 판

    diff1 = cv2.absdiff(pre_img1, pre_img2)
    diff2 = cv2.absdiff(pre_img2, pre_img3)

    ret, diff1_t = cv2.threshold(diff1, thresh, 255, cv2.THRESH_BINARY)
    ret, diff2_t = cv2.threshold(diff2, thresh, 255, cv2.THRESH_BINARY)

    diff = abs(diff1_t - diff2_t)
    k = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, k)
    diff_cnt = cv2.countNonZero(diff)

    if (diff_cnt > max_diff):
        nzero = np.nonzero(diff)
        return True

    return False


def timeToKey(current_hour):
    if(22 < current_hour <= 24 or
        0 <= current_hour <= 6):
        return 0
    elif(6 < current_hour <= 16):
        return 1
    elif(16 < current_hour <= 22):
        return 2
    
    
def chooseAnswer(isCat = True):
    with open(file_path, "r") as json_file:
        cat_data = json.load(json_file)

    if(not isCat):
        textList = cat_data['4']
    else:
        choice1 = random.randrange(0,2)
        if(choice1):
            now = datetime.now()
            current_hour_key = timeToKey(int(now.hour))
            textList = cat_data[str(current_hour_key)]
        else:
            textList = cat_data['3']
            
    textnum = random.randrange(0, len(textList))
    return textList[textnum]


def getGtts():
    num = random.randrange(1,5)
    path = mp3_path + str(num) + ".mp3"
    print(str(path))
    #playsound(path)


def writeDatabase(cat_id, chatt_id, cat_img, cat_answer):
    #write Img to local folder 
    file_name = "./catImg/{}_c{}_chat.jpg".format(cat_id, chatt_id)
    if(cat_img != ""):
        cv2.imwrite(file_name, cat_img)
    conn, cursor = connect_RDS(HOST,USERNAME,PASSWORD,DATABASE)

    """TODO: 만약 python server 에서 응답이 중간에 끊겼을 경우 -> foreign references(update, delete 동시에 가능) (id mapping 이 안될경우 처리)"""
    query = "INSERT INTO cattsge(answer, cid) VALUES ('{}', {});".format(cat_answer, cat_id)
    cursor.execute(query)
    print("//")
    conn.commit()



def cam_work(cat_id, chatt_id, uid):
    cat_id = 1
    user_id = 1
    getGtts()
    #img_token = datetime.now().strftime('%Y-%m-%d %H%M%S') +"cat{}user{}".format(cat_id, user_id) 
    test_command = "python ./yolov5/detect.py --img 416 --weights best.pt --source ruru.mp4"
    stream_command = "python ./yolov5/detect.py --img 416 --weights best.pt --source 0"
    #cv2.imwrite("temp.jpg", frame3)
    os.system(stream_command)

    if(os.path.exists('temp-1.jpg')):
       
        chosenAnswer = chooseAnswer(True)
        frame3 = cv2.imread('temp-1.jpg')
        jpg_img = cv2.imencode('.jpg', frame3)
        dstr = base64.b64encode(jpg_img[1]).decode('utf8')
        cat_id = int(cat_id)
        cat_response = { 'uid' : uid, 'cat_id' : cat_id, 'catImg': dstr, 'catAnswer': chosenAnswer}, 200
        #writeDatabase(cat_id, chatt_id, frame3, chosenAnswer)
        return jsonify(cat_response)

    else:
        chosenAnswer = chooseAnswer(False)
        cat_response = {'cat_id' : int(cat_id), 'catImg': None, 'catAnswer': chosenAnswer}, 200
        #writeDatabase(cat_id, chatt_id, "", chosenAnswer)
        return jsonify(cat_response)


# get api
@app.route("/getCat", methods=['POST'])
def getCat():
    params = request.json
    uid = params['uid']
    cat_id = params['cid']
    chatt_id = params['chattid']
    return cam_work(cat_id=cat_id, chatt_id=chatt_id, uid=uid)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080")