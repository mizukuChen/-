import time, os, sys, gc, struct, math

from media.sensor import * #Import the sensor module and use the camera API
from media.display import * #Import the display module and use display API
from media.media import * #Import the media module and use meida API

from machine import Pin
from machine import FPIOA
from machine import UART

from time import sleep_ms

from MKS32C_uart import Stepmotor

from PID import PID

#user constant
laser_threshold = [(32, 100, 9, 127, -22, -1)] #invert=False
laser_on_line_threshold =[(22, 100, 6, 127, -47, 39)] #invert=False
laser_combine_threshold = [(22, 100, 6, 127, -47, 39), (32, 100, 9, 127, -22, -1)]#invert=False
black_line_threshold =[(100, 16, -128, 127, -128, 127)] #invert=True
target_threshold = [(66, 100, -5, 4, -1, 32)]

rect_point = [[],[]]
rect_point_mid = []

def transfer_vector(uart, vector_x, vector_y):
    # 使用struct.pack将short整数（有符号2字节）打包为二进制数据，使用大端序（little_endian）（'<'）
    packed_data_x = struct.pack('<h', vector_x)
    packed_data_y = struct.pack('<h', vector_y)
    # print(packed_data_x) # debug
    # print(packed_data_y) # debug
    # 创建一个100字节的缓冲区，并将打包后的数据复制到开头
    send_buf = bytearray(4)
    send_buf[0:2] = packed_data_x[0:2]
    send_buf[2:4] = packed_data_y[0:2]
    # print(send_buf) # debug
    uart.write(send_buf[0:4])



#init

motor = Stepmotor(1, 0)

laser_pid = PID(kp=0.2, ki=0, kd=0.05, setpoint=320, output_limits=(-20,20))

#sensor init
sensor = Sensor(width=1280, height=960) #Build a camera object and set the camera image length and width to 4:3
sensor.reset() # reset the Camera
sensor.set_framesize(chn=CAM_CHN_ID_0, width=640, height=480) #Set the frame size to resolution (320x240), default channel 0
sensor.set_framesize(chn=CAM_CHN_ID_1, width=640, height=480)
sensor.set_pixformat(Sensor.RGB565, chn=CAM_CHN_ID_0) #Set the output image format, channel 0
sensor.set_pixformat(Sensor.GRAYSCALE, chn=CAM_CHN_ID_1)

#display init
Display.init(Display.ST7701, to_ide=True) #Use 3.5-inch mipi screen and IDE buffer to display images at the same time

#MediaManager init
MediaManager.init() #Initialize the media resource manager

#sensor run
sensor.run() #Start the camera

clock = time.clock()

#infinite loop
while True:
    clock.tick()

    img_show = sensor.snapshot(chn=CAM_CHN_ID_0)
    img = sensor.snapshot(chn=CAM_CHN_ID_1)
    # img.binary([(29, 72)], invert = False)
    # img.erode(2)
    # img.dilate(0)
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
        target_blobs = img_show.find_blobs(target_threshold, invert=False, roi=(80, 40, 480, 400), merge=True) #检测指定色块，需给定threshold和invert
        if target_blobs:
            target_blob = max(target_blobs, key = lambda b: b[4])#提取最大色块
            img_show.draw_cross(target_blob.cx(), target_blob.cy(), color=(0,255,0))#中心画十字
            img_show.draw_rectangle(target_blob[0:4], color=(0, 255, 255))#周围画边框
            img_show.draw_cross((320, 240))
            print(target_blob.cx(), target_blob.cy())#打印色块中心位置
            output = laser_pid.compute(target_blob.cx())
            print(output)
            print(laser_pid._last_error)
            motor.position_mode(4, round(output))

        #for c in img_show.find_circles(roi=(60, 40, 520, 400), threshold = 2000, x_margin = 3, y_margin= 3,
        #                          r_margin = 3,r_min = 2, r_max = 100, r_step = 2):
        #    #Draw a red circle as an indication
        #    img_show.draw_circle(c.x(), c.y(), c.r(), color = (0, 0, 0),thickness=2)
        #    print(c)

    rect_point = [[],[]]
    rect_point_mid = []

    gc.collect()
    #print(clock.fps()) #FPS
    fps_text = "{}".format(clock.fps())
    img_show.draw_string_advanced(32, 40, 20, fps_text)
    Display.show_image(img_show, x=round((800-sensor.width())/2),y=round((480-sensor.height())/2))
