import time, os, sys, gc, struct

from media.sensor import * #Import the sensor module and use the camera API
from media.display import * #Import the display module and use display API
from media.media import * #Import the media module and use meida API

from machine import Pin
from machine import FPIOA
from machine import UART

from time import sleep_ms



#user constant
laser_threshold = [(32, 100, 9, 127, -22, -1)] #invert=False
laser_on_line_threshold =[(22, 100, 6, 127, -47, 39)] #invert=False
laser_combine_threshold = [(22, 100, 6, 127, -47, 39), (32, 100, 9, 127, -22, -1)]#invert=False
black_line_threshold =[(100, 16, -128, 127, -128, 127)] #invert=True

def transfer_vector(uart, vector_x, vector_y):
    # 使用struct.pack将short整数（有符号2字节）打包为二进制数据，使用大端序（little_endian）（'<'）
    packed_data_x = struct.pack('<h', vector_x)
    packed_data_y = struct.pack('<h', vector_y)
    print(packed_data_x) # debug
    print(packed_data_y) # debug
    # 创建一个100字节的缓冲区，并将打包后的数据复制到开头
    send_buf = bytearray(4)
    send_buf[0:2] = packed_data_x[0:2]
    send_buf[2:4] = packed_data_y[0:2]
    print(send_buf) # debug
    uart.write(send_buf[0:4])



#init

#sensor init
sensor = Sensor(width=1280, height=960) #Build a camera object and set the camera image length and width to 4:3
sensor.reset() # reset the Camera
sensor.set_framesize(width=640, height=480) #Set the frame size to resolution (320x240), default channel 0
sensor.set_pixformat(Sensor.RGB565) #Set the output image format, channel 0

#display init
Display.init(Display.ST7701, to_ide=True) #Use 3.5-inch mipi screen and IDE buffer to display images at the same time

#MediaManager init
MediaManager.init() #Initialize the media resource manager

#sensor run
sensor.run() #Start the camera

clock = time.clock()

#UART init
fpioa = FPIOA()
fpioa.set_function(3,FPIOA.UART1_TXD)
fpioa.set_function(4,FPIOA.UART1_RXD)
uart=UART(UART.UART1,115200) #设置串口号1和波特率




#infinite loop
while True:
    clock.tick()
    img = sensor.snapshot()
    target_blobs = img.find_blobs(black_line_threshold, invert=True, roi=(160, 120, 320, 240)) #检测指定色块，需给定threshold和invert
    if target_blobs:
        target_blob = max(target_blobs, key = lambda b: b[4])#提取最大色块
        img.draw_cross(target_blob.cx(), target_blob.cy(), color=(0,0,0))#中心画十字
        img.draw_rectangle(target_blob[0:4])#周围画边框
        print(target_blob.cx(), target_blob.cy())#打印色块中心位置

    print(clock.fps()) #FPS
    Display.show_image(img, x=round((800-sensor.width())/2),y=round((480-sensor.height())/2))

