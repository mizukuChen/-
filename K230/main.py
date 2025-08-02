import time, os, sys, gc, struct, math

from media.sensor import * #Import the sensor module and use the camera API
from media.display import * #Import the display module and use display API
from media.media import * #Import the media module and use meida API

from machine import Pin
from machine import FPIOA
from machine import UART
from machine import Timer

from time import sleep_ms



from PID import PID

import struct

class Stepmotor:
    # 类常量（所有实例共享）
    ANGLE_MODE = 1.8
    STEP_MODE = 256
    STEPS_PER_CIRCLE = int(360 / ANGLE_MODE * STEP_MODE)
    DEG_PER_STEP = 1.0 / ANGLE_MODE * STEP_MODE
    TURN_FORWARD = 1
    TURN_REVERSE = 0

    def __init__(self, uart, motor_id):
        """
        初始化步进电机对象

        :param uart: UART对象，用于通信
        :param motor_id: 电机ID (0-3)
        """

        self.uart = uart
        self.motor_id = motor_id

    @staticmethod

    def get_check_sum(data):
        """计算校验和（求和取低8位）"""
        return sum(data) & 0xFF

    def speed_mode(self, direction, speed):
        """速度模式控制"""
        # 确保速度在0-127范围内
        speed = max(0, min(127, speed))
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0xF6             # 功能码
        tx_data[2] = (direction << 7) | (speed & 0x7F)  # 方向+速度
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)

    def position_mode(self, speed, angle):
        """位置模式控制"""
        # 计算脉冲数并确定方向
        direction = self.TURN_FORWARD if angle >= 0 else self.TURN_REVERSE
        abs_angle = abs(angle)
        pulses = int(abs_angle * self.STEP_MODE / self.ANGLE_MODE)

        # 确保速度在0-127范围内
        speed = max(0, min(127, speed))

        tx_data = bytearray(8)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0xFD             # 功能码
        tx_data[2] = (direction << 7) | (speed & 0x7F)  # 方向+速度
        # 脉冲数(32位大端序)
        tx_data[3:7] = struct.pack('>I', pulses)
        tx_data[7] = self.get_check_sum(tx_data[:7])  # 校验和

        self.uart.write(tx_data)

    def stop(self):
        """停止电机"""
        tx_data = bytearray(3)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0xF7             # 功能码
        tx_data[2] = self.get_check_sum(tx_data[:2])  # 校验和

        self.uart.write(tx_data)

    def enable(self, status):
        """使能/禁用电机"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0xF3             # 功能码
        tx_data[2] = 1 if status else 0  # 状态
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)

    def save_speed(self):
        """保存当前速度"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0xFF             # 功能码
        tx_data[2] = 0xC8             # 保存指令
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)

    def clear_speed(self):
        """清除保存的速度"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0xFF             # 功能码
        tx_data[2] = 0xCA             # 清除指令
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)





    def read_encoder(self):
        """读取编码器角度（0-360°）"""
        tx_data = bytearray([0xE0 + self.motor_id, 0x30, 0x00])
        tx_data[2] = self.get_check_sum(tx_data[:2])

        self.uart.write(tx_data)

        rx_data = self.uart.read(8)
        if not rx_data or len(rx_data) < 8:
            return 0.0

        encoder_val = (rx_data[5] << 8) | rx_data[6]
        return encoder_val * 360.0 / 65536

    def read_pulses(self):
        """读取脉冲计数值"""
        tx_data = bytearray([0xE0 + self.motor_id, 0x33, 0x00])
        tx_data[2] = self.get_check_sum(tx_data[:2])

        self.uart.write(tx_data)

        rx_data = self.uart.read(6)
        if not rx_data or len(rx_data) < 6:
            return 0

        # 解析32位有符号整数 (大端序)
        return int.from_bytes(rx_data[1:5], 'big', signed=True)

    def read_position(self):
        """读取电机位置（角度）"""
        tx_data = bytearray([0xE0 + self.motor_id, 0x36, 0x00])
        tx_data[2] = self.get_check_sum(tx_data[:2])

        self.uart.write(tx_data)

        rx_data = self.uart.read(6)
        if not rx_data or len(rx_data) < 6:
            return 0.0

        position_val = int.from_bytes(rx_data[1:5], 'big', signed=True)
        return position_val * 360.0 / 65536

    def read_error(self):
        """读取位置偏差角度"""
        tx_data = bytearray([0xE0 + self.motor_id, 0x39, 0x00])
        tx_data[2] = self.get_check_sum(tx_data[:2])

        self.uart.write(tx_data)

        rx_data = self.uart.read(4)
        if not rx_data or len(rx_data) < 4:
            return 0.0

        error_val = (rx_data[1] << 8) | rx_data[2]
        return error_val * 360.0 / 65536





    def reset(self):
        """复位电机"""
        tx_data = bytearray(3)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0x3F             # 功能码
        tx_data[2] = self.get_check_sum(tx_data[:2])  # 校验和

        self.uart.write(tx_data)

    def set_kp(self, kp):
        """设置比例增益Kp"""
        tx_data = bytearray(5)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0xA1             # 功能码
        tx_data[2] = (kp >> 8) & 0xFF  # 高字节
        tx_data[3] = kp & 0xFF         # 低字节
        tx_data[4] = self.get_check_sum(tx_data[:4])  # 校验和

        self.uart.write(tx_data)

    def set_ki(self, ki):
        """设置积分增益Ki"""
        tx_data = bytearray(5)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0xA2             # 功能码
        tx_data[2] = (ki >> 8) & 0xFF  # 高字节
        tx_data[3] = ki & 0xFF         # 低字节
        tx_data[4] = self.get_check_sum(tx_data[:4])  # 校验和

        self.uart.write(tx_data)

    def set_kd(self, kd):
        """设置微分增益Kd"""
        tx_data = bytearray(5)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0xA3             # 功能码
        tx_data[2] = (kd >> 8) & 0xFF  # 高字节
        tx_data[3] = kd & 0xFF         # 低字节
        tx_data[4] = self.get_check_sum(tx_data[:4])  # 校验和

        self.uart.write(tx_data)

    def set_acc(self, acc):
        """设置加速度"""
        tx_data = bytearray(5)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0xA4             # 功能码
        tx_data[2] = (acc >> 8) & 0xFF  # 高字节
        tx_data[3] = acc & 0xFF         # 低字节
        tx_data[4] = self.get_check_sum(tx_data[:4])  # 校验和

        self.uart.write(tx_data)

    def set_maxt(self, maxt):
        """设置最大转矩"""
        tx_data = bytearray(5)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0xA5             # 功能码
        tx_data[2] = (maxt >> 8) & 0xFF  # 高字节
        tx_data[3] = maxt & 0xFF         # 低字节
        tx_data[4] = self.get_check_sum(tx_data[:4])  # 校验和

        self.uart.write(tx_data)





    def set_zero_mode(self, mode):
        """设置回零模式"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0x90             # 功能码
        tx_data[2] = mode         # 模式
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)

    def set_zero_speed(self):
        """设置零点"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0x91             # 功能码
        tx_data[2] = 00        # 方向
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)

    def set_zero_speed(self, speed):
        """设置回零速度"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0x92             # 功能码
        tx_data[2] = speed         # 方向
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)

    def set_zero_direct(self, direct):
        """设置回零方向  0为顺时针"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0x93             # 功能码
        tx_data[2] = direct         # 方向
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)

    def goto_zero(self):
        """回到零点"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0x94             # 功能码
        tx_data[2] = 00         # 回零标志
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)





    def set_Motortype(self, de_angle):
        """设置电机单步角度"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0x81             # 功能码
        tx_data[2] = 0x00 if de_angle == 0.9 else 0x01       # 单步角度
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)

    def set_current(self, current):
        """设置电流挡位"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0x82             # 功能码
        tx_data[2] = current       # 电流挡位
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)

    def set_M_step(self, M_step):
        """设置细分"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0x84             # 功能码
        tx_data[2] = M_step       # 细分数
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)

    def set_Dir(self, Dir):
        """设置旋转正方向"""
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id  # 地址
        tx_data[1] = 0x86             # 功能码
        tx_data[2] = Dir       # 细分数
        tx_data[3] = self.get_check_sum(tx_data[:3])  # 校验和

        self.uart.write(tx_data)



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

laser.on()

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
        #if (abs(rect_center_point[0]-328.04)<20 and abs(rect_center_point[1]-126.81)<15):
        #    laser.on()
        #    motor_x.stop()
        #    motor_y.stop()
        #    break
        laser_pid_x.reset_setpoint(328.04)
        laser_pid_y.reset_setpoint(126.81)
        output_x = laser_pid_x.compute(projective_delta_X(corners, 0/26.13, 0))
        output_y = laser_pid_y.compute(projective_delta_Y(corners, 0/26.13, 0))
        print(output_x, output_y)
        print(projective_delta_Y(corners, -2.6/26.13, 0))
        #blobs = img_show.find_blobs([(59, 100, -2, 33, -29, 2)], False, (target_rect.x(), target_rect.y(), target_rect.w(), target_rect.h()))
        #if blobs:
        #    target_blob = max(blobs, key = lambda b: b[4])#提取最大矩形
        #    img_show.draw_cross(target_blob.cx(), target_blob.cy())
        motor_x.position_mode(abs(round(1*output_x))+1, output_x)
        motor_y.position_mode(abs(round(1*output_y))+1, output_y)
        #for i in range(100):
        #    angle = 2*(math.pi)/100*i
        #    pos = projective_circle(corners, 6/26.13, 6/17.20, angle)
        #    img_show.draw_cross(pos, color=(255, 0, 0))
        #rect_center_point = (int((corners[0][0]+corners[1][0]+corners[2][0]+corners[3][0])/4), int((corners[0][1]+corners[1][1]+corners[2][1]+corners[3][1])/4))
        #print(rect_center_point)
        #img_show.draw_cross(rect_center_point, color=(255, 255, 255))
        #output = laser_pid.compute(rect_center_point[0])
        #print(output)
        #print(laser_pid._last_error)
        #motor.position_mode(2, round(output))

    #img_show = sensor.snapshot(chn=CAM_CHN_ID_0)
    #img = sensor.snapshot(chn=CAM_CHN_ID_1)
    #img.binary([(87, 255)], invert = True)
    #img.erode(2)
    #img.dilate(2)
    #rects = img.find_rects(roi=(160, 0, 480, 240), threshold=200000)
    #for index, rect in enumerate(rects):
    #    corners = rect.corners() # debug
    #    for i in range(100):
    #       angle = 2*(math.pi)/100*i
    #       pos = projective_circle(corners, 6/29.7, 6/21, angle)
    #       img_show.draw_cross(pos, color=(255, 0, 0))
#
    #    print(corners)
    #    for corner in corners:
    #        img_show.draw_cross(corner, color=(255,0,0))
    #        if len(rects) == 2:
    #            rect_point[index].append(corner)
    #if len(rects) == 2:
    #    for i in range(4):
    #        x_mid = int((rect_point[0][i][0]+rect_point[1][i][0])/2)
    #        y_mid = int((rect_point[0][i][1]+rect_point[1][i][1])/2)
    #        rect_point_mid.append((x_mid, y_mid))
    #        img_show.draw_cross(int(x_mid), int(y_mid), color=(255,255,255))
    #    print(rect_point_mid)
    #    for i in range(3):
    #        img_show.draw_line(rect_point_mid[i][0], rect_point_mid[i][1], rect_point_mid[i+1][0], rect_point_mid[i+1][1], color=(255,255,255))
    #    img_show.draw_line(rect_point_mid[3][0], rect_point_mid[3][1], rect_point_mid[0][0], rect_point_mid[0][1], color=(255,255,255))


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
