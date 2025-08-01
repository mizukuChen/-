import time, os, sys, json, gc, struct
from media.sensor import *
from media.display import *
from media.media import *
from machine import TOUCH   # 触摸系统

from time import sleep_ms

from MKS32C_uart import Stepmotor

from PID import PID

'''

'''

def task1(img, img_show, laser_threshold, blackline_threshold, laser_pid_x, laser_pid_y, motor):
    img.binary(blackline_threshold, invert = True)
    img.erode(2)
    img.dilate(2)
    rects = img.find_rects(threshold=200000)
    if rects:
        target_rect = max(rects, key = lambda b: b[4])#提取最大矩形
        corners = target_rect.corners()
        rect_center_point = (int((corners[0][0]+corners[2][0])/2), int((corners[0][1]+corners[2][1])/2))
        print(rect_center_point)
        img_show.draw_cross(rect_center_point, color=(255, 255, 255))
        output = laser_pid_x.compute(rect_center_point[0])
        print(output)
        print(laser_pid_x._last_error)
        print(laser_pid_y._last_error)
        motor.position_mode(2, round(output))

    pass

def task2(img, img_show, laser_threshold, blackline_threshold, laser_pid_x, laser_pid_y, motor):
    rect_point = [[], []]
    rect_point_mid = []
    rects = img.find_rects(roi=(160, 0, 480, 240), threshold=60000)
    for index, rect in enumerate(rects):
        corners = rect.corners() # debug
        for corner in corners:
            img_show.draw_cross(corner, color=(255,0,0))
            if len(rects) == 2:
                rect_point[index].append(corner)
    if len(rects) == 2:
        for i in range(4):
            x_mid = int((rect_point[0][i][0]+rect_point[1][i][0])/2)
            y_mid = int((rect_point[0][i][1]+rect_point[1][i][1])/2)
            rect_point_mid.append((x_mid, y_mid))
            img_show.draw_cross(int(x_mid), int(y_mid), color=(255,255,255))
        for i in range(3):
            img_show.draw_line(rect_point_mid[i][0], rect_point_mid[i][1], rect_point_mid[i+1][0], rect_point_mid[i+1][1], color=(255,255,255))
        img_show.draw_line(rect_point_mid[3][0], rect_point_mid[3][1], rect_point_mid[0][0], rect_point_mid[0][1], color=(255,255,255))

    if rect_point_mid:
        img_show.rotation_corr(corners = rect_point_mid)
        #img_show.gaussian(2)
        target_blobs = img_show.find_blobs(laser_threshold, invert=False, roi=(80, 40, 480, 400), merge=True) #检测指定色块，需给定threshold和invert
        if target_blobs:
            target_blob = max(target_blobs, key = lambda b: b[4])#提取最大色块
            img_show.draw_cross(target_blob.cx(), target_blob.cy(), color=(0,255,0))#中心画十字
            img_show.draw_rectangle(target_blob[0:4], color=(0, 255, 255))#周围画边框
            img_show.draw_cross((320, 240))
            print(target_blob.cx(), target_blob.cy())#打印色块中心位置
            output = laser_pid_x.compute(target_blob.cx())
            print(output)
            print(laser_pid_x._last_error)
            motor.position_mode(4, round(output))

    rect_point = [[],[]]
    rect_point_mid = []
