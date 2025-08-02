from media.display import *
from media.media import *
from media.sensor import *
import time, os, sys, gc
from machine import TOUCH
from machine import Pin
from machine import FPIOA

#显示的宽高
DISPLAY_WIDTH = ALIGN_UP(800, 16)
DISPLAY_HEIGHT = 480

#视频分辨率
VIDEO_WIDTH = 800
VIDEO_HEIGHT = 480

#按键GPIO Number，根据硬件修改
PRESS_KEY_NUM = 21

#保存图片的起始编号，可以修改
save_num = 0

#数据采集标准框，采集的物体最好在这个框框内
grab_x = 0
grab_y = 0
grab_w = 0
grab_h = 0

#保存图片的位置和图片名称开头，根据需要修改
IMG_SAVE_PATH="data/"
IMG_SAVE_NAME_BEGIN="1_"

LOGO_FILE="/sdcard/examples/16-AI-Cube/logo.jpg"

FONT_X = int(DISPLAY_WIDTH/2-50)
FONT_Y = int(DISPLAY_HEIGHT/2-10)

#sensor = None

def media_init():
    global sensor
    # 根据硬件选择显示的方法，默认为IDE显示
    # use LCD for display
    Display.init(Display.ST7701, width = DISPLAY_WIDTH, height = DISPLAY_HEIGHT, to_ide = True, osd_num=1)

    # use hdmi for display
    # Display.init(Display.LT9611, width = DISPLAY_WIDTH, height = DISPLAY_HEIGHT, to_ide = True, osd_num=1)

    # use IDE for display
    #Display.init(Display.VIRT, width = DISPLAY_WIDTH, height = DISPLAY_HEIGHT, fps = 60)

    sensor = Sensor(width=1920, height=1080, fps=30)
    sensor.reset()
    sensor.set_hmirror(True)
    sensor.set_vflip(True)
    sensor.set_framesize(w=VIDEO_WIDTH, h=VIDEO_HEIGHT,chn=CAM_CHN_ID_0)
    sensor.set_pixformat(Sensor.RGB565)
    sensor.set_framesize(w=VIDEO_WIDTH, h=VIDEO_HEIGHT, chn=CAM_CHN_ID_2)
    sensor.set_pixformat(Sensor.RGB565, chn=CAM_CHN_ID_2)
    MediaManager.init()
    sensor.run()
    cal_grab_rect()

def cal_grab_rect():
    global grab_x, grab_y, grab_w, grab_h

    if VIDEO_WIDTH > VIDEO_HEIGHT:
        grab_h = int(VIDEO_HEIGHT*6/7)
        grab_y = int((VIDEO_HEIGHT - grab_h)/2)
        grab_w = grab_h
        grab_x = int((VIDEO_WIDTH - grab_w)/2)
    else:
        grab_w = int(VIDEO_WIDTH*6/7)
        grab_x = int((VIDEO_WIDTH - grab_w)/2)
        grab_h = grab_w
        grab_y = int((VIDEO_HEIGHT - grab_h)/2)

    print("cal_grab_rect x: " + str(grab_x) + ",y: " + str(grab_y) + ",w: " + str(grab_w) + ",h: " + str(grab_h))

def media_deinit():
    global sensor
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    sensor.stop()
    time.sleep_ms(50)
    Display.deinit()
    MediaManager.deinit()

def save_file(img_0):
    global save_num
    img_1 = img_0.to_jpeg()
    img_name = IMG_SAVE_NAME_BEGIN + str(save_num) + ".jpg"
    img_1.save(IMG_SAVE_PATH + img_name)
    print("save img " + IMG_SAVE_PATH + img_name)
    save_num += 1
    gc.collect()
    return img_name

def gpio_init():
    global KEY
    fpioa = FPIOA()
    fpioa.set_function(PRESS_KEY_NUM,FPIOA.GPIO21)
    KEY=Pin(PRESS_KEY_NUM, Pin.IN, Pin.PULL_UP) #构建KEY对象


def show_logo():
    logo_img = image.Image(LOGO_FILE)
    print("show logo w: " + str(logo_img.width()) + ", h: " + str(logo_img.height()))
    Display.show_image(logo_img.to_rgb888())
    time.sleep(2)


def index_init():
    global save_num
    for file in os.listdir(IMG_SAVE_PATH):
        if file is None:
            break
        if file.startswith(IMG_SAVE_NAME_BEGIN):
            index = file.split('_')[1]
            index = int(index.split('.')[0])
            if save_num <= index:
                save_num = index + 1
    print("index_init start " + str(save_num))

def key_handle(img):
    global KEY, grab_x, grab_y, grab_w, grab_h
    if KEY.value()==0:   #按键被按下
        time.sleep_ms(10) #消除抖动
        if KEY.value()==0: #确认按键被按下
            print('KEY')
            img_name = save_file(img)
            img.draw_string_advanced(FONT_X, FONT_Y, 100, img_name, color = (0, 0, 255),)
            img.draw_rectangle(grab_x, grab_y, grab_w, grab_h, color = (255, 0, 0), thickness = 2, fill = False)
            Display.show_image(img)
            time.sleep(2)
            while not KEY.value(): #检测按键是否松开
                pass
    else:
        img.draw_rectangle(grab_x, grab_y, grab_w, grab_h, color = (255, 0, 0), thickness = 2, fill = False)
        Display.show_image(img_show) #显示图片

try:
    media_init()
    gpio_init()
    index_init()
    fpioa = FPIOA()
    fpioa.set_function(42,FPIOA.GPIO42)
    laser=Pin(42,Pin.OUT) #构建led对象，GPIO52,输出
    laser.on()
    while True:
        laser.on()
        img = sensor.snapshot(chn=CAM_CHN_ID_0) #拍摄一张图
        img.binary([(16, 100, 85, -122, -124, 127)])
        img_show = sensor.snapshot(chn=CAM_CHN_ID_2)
        rects = img.find_rects()
        if rects:
            print("ok")
            target_rect = max(rects, key = lambda b: b[4])#提取最大矩形
            for corner in target_rect.corners():
                img_show.draw_cross(corner)

            blobs = img_show.find_blobs([(100, 78, 73, -128, -86, 127)], True, (target_rect.x(), target_rect.y(), target_rect.w(), target_rect.h()))
            if blobs:
                target_blob = max(blobs, key = lambda b: b[4])#提取最大矩形
                write_text = "{} {} {}".format(target_blob.cx(), target_blob.cy(), target_rect.w()*target_rect.h())
                img_show.draw_string_advanced(240, 240, 20, write_text)

        key_handle(img_show)
        time.sleep_ms(10)
except BaseException as e:
    import sys
    sys.print_exception(e)
media_deinit()
gc.collect()
