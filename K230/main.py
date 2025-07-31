import time, os, sys, gc, struct

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
target_threshold = [(190, 255)]

rect_point = [[],[]]
rect_point_mid = []
target_corners = []

#init
motor = Stepmotor(1, 0)

laser_pid = PID(kp=-2, ki=0, kd=0, setpoint=320, output_limits=(-20,20))

#sensor init
sensor = Sensor(width=1280, height=960) #Build a camera object and set the camera image length and width to 4:3
sensor.reset() # reset the Camera
sensor.set_framesize(chn=CAM_CHN_ID_0, width=640, height=480) #Set the frame size to resolution (320x240), default channel 0
sensor.set_framesize(chn=CAM_CHN_ID_1, width=640, height=480)
sensor.set_pixformat(Sensor.GRAYSCALE, chn=CAM_CHN_ID_0) #Set the output image format, channel 0
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
    img.binary([(29, 72)], invert = True)
    img.erode(2)
    img.dilate(2)
    rects = img.find_rects(threshold=200000)
    if rects:
        target_rect = max(rects, key = lambda b: b[4])#提取最大矩形
        corners = target_rect.corners()
        rect_center_point = (int((corners[0][0]+corners[2][0])/2), int((corners[0][1]+corners[2][1])/2))
        print(rect_center_point)
        img_show.draw_cross(rect_center_point, color=(255, 255, 255))
        output = laser_pid.compute(rect_center_point[0])
        print(output)
        print(laser_pid._last_error)
        motor.position_mode(2, round(output))

    target_corners = []
    gc.collect()
    print(clock.fps()) #FPS
    fps_text = "{}".format(clock.fps())
    img_show.draw_string_advanced(32, 40, 20, fps_text)
    Display.show_image(img_show, x=round((800-sensor.width())/2),y=round((480-sensor.height())/2))
