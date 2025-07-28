import time, os, sys, gc

from media.sensor import * #Import the sensor module and use the camera API
from media.display import * #Import the display module and use display API
from media.media import * #Import the media module and use meida API

from machine import Pin
from machine import FPIOA
from machine import UART

from Stepmotor import Stepper

laser_threshold = [(32, 100, 9, 127, -22, -1)] #invert=False
laser_on_line_threshold =[(22, 100, 6, 127, -47, 39)] #invert=False
laser_combine_threshold = [(22, 100, 6, 127, -47, 39), (32, 100, 9, 127, -22, -1)]
black_line_threshold =[(100, 16, -128, 127, -128, 127)] #invert=True

def stepper_control(uart, target_point):
    current_point = []
    inc_x = target_point[0]-current_point[0]
    inc_y = target_point[1]-current_point[1]
    if (inc_x > 0):
        inc_x_sign = 1
    else:
        inc_x_sign = 0
    if(inc_y > 0):
        inc_y_sign = 1
    else:
        inc_y_sign = 0

    write_text = "{}{}{}{}".format(inc_x_sign, abs(inc_x), inc_y_sign, abs(inc_y))
    uart.write(write_text)

def black_line_follow():
    img = sensor.snapshot()
    rects = img.findrects()

sensor = Sensor(width=1280, height=960) #Build a camera object and set the camera image length and width to 4:3
sensor.reset() # reset the Camera
sensor.set_framesize(width=640, height=480) #Set the frame size to resolution (320x240), default channel 0
sensor.set_pixformat(Sensor.RGB565) #Set the output image format, channel 0

Display.init(Display.ST7701, to_ide=True) #Use 3.5-inch mipi screen and IDE buffer to display images at the same time
#Display.init(Display.VIRT, sensor.width(), sensor.height()) #Use only the IDE buffer to display images

MediaManager.init() #Initialize the media resource manager

sensor.run() #Start the camera


while True:
    img = sensor.snapshot()
    target_blobs = img.find_blobs(laser_combine_threshold, invert=False) #检测指定色块，需给定threshold和invert
#    if target_blobs:
#        target_blob = max(target_blobs, key = lambda b: b[4])
#        img.draw_cross(target_blob.cx(), target_blob.cy(), color=(0,0,0))
#        img.draw_rectangle(target_blob[0:4])
    for target_blob in target_blobs:
        img.draw_cross(target_blob.cx(), target_blob.cy(), color=(0, 0, 0))
        img.draw_rectangle(target_blob[0:4])
#    for blue_blob in blue_blobs:
#        img.draw_cross(blue_blob.cx(), blue_blob.cy(), color=(0,0,0))
#        img.draw_rectangle(blue_blob[0:4])
    Display.show_image(img, x=round((800-sensor.width())/2),y=round((480-sensor.height())/2))

