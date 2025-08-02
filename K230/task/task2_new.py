import time, os, sys, gc, struct, math

from media.sensor import * #Import the sensor module and use the camera API
from media.display import * #Import the display module and use display API
from media.media import * #Import the media module and use meida API

from machine import Pin
from machine import FPIOA
from machine import UART
from machine import Timer

from time import sleep_ms

from MKS32C_uart import Stepmotor

from PID import PID

from task import *

import struct


def projective_circle(corners, radius_a, radius_b, angle, delta_x, delta_y):
    rsin = radius_b * math.sin(angle) + delta_x
    rcos = radius_a * math.cos(angle) + delta_y
    alter_A = (0.5 - rcos) * (0.5 - rsin)
    alter_B = (0.5 + rcos) * (0.5 - rsin)
    alter_C = (0.5 + rcos) * (0.5 + rsin)
    alter_D = (0.5 - rcos) * (0.5 + rsin)
    pos_x = alter_D * corners[0][0] +\
            alter_C * corners[1][0] +\
            alter_B * corners[2][0] +\
            alter_A * corners[3][0]

    pos_y = alter_D * corners[0][1] +\
            alter_C * corners[1][1] +\
            alter_B * corners[2][1] +\
            alter_A * corners[3][1]

    return (round(pos_x), round(pos_y))
    


def projective_delta(corners, delta_x, delta_y):
    alter_A = (0.5 - delta_x) * (0.5 - delta_y)
    alter_B = (0.5 + delta_x) * (0.5 - delta_y)
    alter_C = (0.5 + delta_x) * (0.5 + delta_y)
    alter_D = (0.5 - delta_x) * (0.5 + delta_y)
    pos_x = alter_D * corners[0][0] +\
            alter_C * corners[1][0] +\
            alter_B * corners[2][0] +\
            alter_A * corners[3][0]

    pos_y = alter_D * corners[0][1] +\
            alter_C * corners[1][1] +\
            alter_B * corners[2][1] +\
            alter_A * corners[3][1]

    return (pos_x, pos_y)

def projective_middle(corners):
    pos_x = (corners[0][0] +corners[1][0] +corners[2][0] +corners[3][0])/4

    pos_y = (corners[0][1] +corners[1][1] +corners[2][1] +corners[3][1])/4

    return (round(pos_x), round(pos_y))

def projective_delta_X(corners, delta_x, delta_y):
    alter_A = (0.5 - delta_x) * (0.5 - delta_y)
    alter_B = (0.5 + delta_x) * (0.5 - delta_y)
    alter_C = (0.5 + delta_x) * (0.5 + delta_y)
    alter_D = (0.5 - delta_x) * (0.5 + delta_y)
    pos_x = alter_D * corners[0][0] +\
            alter_C * corners[1][0] +\
            alter_B * corners[2][0] +\
            alter_A * corners[3][0]

    return (pos_x)


def projective_delta_Y(corners, delta_x, delta_y):
    alter_A = (0.5 - delta_x) * (0.5 - delta_y)
    alter_B = (0.5 + delta_x) * (0.5 - delta_y)
    alter_C = (0.5 + delta_x) * (0.5 + delta_y)
    alter_D = (0.5 - delta_x) * (0.5 + delta_y)
    pos_y = alter_D * corners[0][1] +\
            alter_C * corners[1][1] +\
            alter_B * corners[2][1] +\
            alter_A * corners[3][1]

    return (pos_y)

#user constant
laser_threshold = [(32, 100, 9, 127, -22, -1)] #invert=False
laser_on_line_threshold =[(22, 100, 6, 127, -47, 39)] #invert=False
laser_combine_threshold = [(22, 100, 6, 127, -47, 39), (32, 100, 9, 127, -22, -1)]#invert=False
black_line_threshold =[(100, 16, -128, 127, -128, 127)] #invert=True
target_threshold = [(190, 255)]

rect_point = [[],[]]
rect_point_mid = []
target_corners = []

angle = 0
k = 0.2

#init

#laser init
fpioa = FPIOA()
fpioa.set_function(42,FPIOA.GPIO42)
laser=Pin(42,Pin.OUT) #构建led对象，GPIO52,输出
laser.off()

fpioa.set_function(11, FPIOA.UART2_TXD)
fpioa.set_function(12, FPIOA.UART2_RXD)
uart2 = UART(UART.UART2, baudrate=25000)
fpioa.set_function(3,FPIOA.UART1_TXD)
fpioa.set_function(4,FPIOA.UART1_RXD)
uart1=UART(UART.UART1,25000) #设置串口号1和波特率


#motor init
motor_x = Stepmotor(uart2, 0)
motor_y = Stepmotor(uart1, 0)

#pid init
laser_pid_x = PID(kp=-0.8*k, ki=-0.005*k, kd=-0.45*k, setpoint=320, output_limits=(-20,20))
laser_pid_y = PID(kp=0.6*k, ki=0.003*k, kd=0.35*k, setpoint=160, output_limits=(-20,20))

#sensor init
sensor = Sensor(width=1920, height=1080) #Build a camera object and set the camera image length and width to 4:3
sensor.reset() # reset the Camera
sensor.set_hmirror(True)
sensor.set_vflip(True)
sensor.set_framesize(chn=CAM_CHN_ID_0, width=640, height=360) #Set the frame size to resolution (320x240), default channel 0
sensor.set_framesize(chn=CAM_CHN_ID_1, width=640, height=360)
sensor.set_pixformat(Sensor.RGB565, chn=CAM_CHN_ID_0) #Set the output image format, channel 0
sensor.set_pixformat(Sensor.GRAYSCALE, chn=CAM_CHN_ID_1)

#display init
Display.init(Display.ST7701, to_ide=True) #Use 3.5-inch mipi screen and IDE buffer to display images at the same time

#MediaManager init
MediaManager.init() #Initialize the media resource manager

#sensor run
sensor.run() #Start the camera

clock = time.clock()

#laser.on()

#infinite loop
while True:
    clock.tick()

    img_show = sensor.snapshot(chn=CAM_CHN_ID_0)
    img = sensor.snapshot(chn=CAM_CHN_ID_1)
    img.binary([(87, 255)], invert = True)
    img.erode(1)
    #img.dilate(2)
    rects = img.find_rects(threshold=200000)
    #motor_x.speed_mode(1, 20)
    if rects:
        #motor_x.speed_mode(1, 0)
        target_rect = max(rects, key = lambda b: b[4])#提取最大矩形
        #print(target_rect)
        corners = target_rect.corners()
        for corner in corners:
            img_show.draw_cross(corner, color=(255, 0, 0))
        rect_center_point = (int((corners[0][0]+corners[1][0]+corners[2][0]+corners[3][0])/4), int((corners[0][1]+corners[1][1]+corners[2][1]+corners[3][1])/4))
        print(rect_center_point)
        img_show.draw_cross(rect_center_point, color=(255, 0, 0))
        if (abs(rect_center_point[0]-328.04)<20 and abs(rect_center_point[1]-126.81)<15):
            laser.on()
            motor_x.stop()
            motor_y.stop()
            break
        laser_pid_x.reset_setpoint(328.04)
        laser_pid_y.reset_setpoint(126.81)
        output_x = laser_pid_x.compute(projective_delta_X(corners, 0/26.13, 0))
        output_y = laser_pid_y.compute(projective_delta_Y(corners, 0/26.13, 0))
        print(output_x, output_y)
        print(projective_delta_Y(corners, -2.6/26.13, 0))

        motor_x.position_mode(abs(round(1*output_x))+1, output_x)
        motor_y.position_mode(abs(round(1*output_y))+1, output_y)


    rect_point = [[],[]]
    rect_point_mid = []

    target_corners = []
    gc.collect()
    #print(clock.fps()) #FPS
    fps_text = "{}".format(clock.fps())
    img_show.draw_string_advanced(32, 40, 20, fps_text)
    Display.show_image(img_show, x=round((800-sensor.width())/2),y=round((480-sensor.height())/2))

while True:
    pass
