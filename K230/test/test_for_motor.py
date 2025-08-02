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

#init

#laser init
fpioa = FPIOA()
fpioa.set_function(42,FPIOA.GPIO42)
laser=Pin(42,Pin.OUT) #构建led对象，GPIO52,输出
laser.off()

fpioa.set_function(11, FPIOA.UART2_TXD)
fpioa.set_function(12, FPIOA.UART2_RXD)
uart2 = machine.UART(2, baudrate=25000)

fpioa.set_function(3, FPIOA.UART1_TXD)
fpioa.set_function(4, FPIOA.UART1_RXD)
uart1 = UART(UART.UART1, 25000)

#motor init
motor_x = Stepmotor(uart1, 0)
motor_y = Stepmotor(uart2, 0)

#pid init
laser_pid_x = PID(kp=-1.5, ki=-0, kd=-0.8, setpoint=320, output_limits=(-20,20))
laser_pid_y = PID(kp=   2, ki=0, kd=0, setpoint=320, output_limits=(-20,20))

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

#motor_x.position_mode(10, 100)
motor_x.speed_mode(1, 20)

#infinite loop
while True:
    pass
