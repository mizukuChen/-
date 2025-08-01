# 程序 4-1-UI_Design
# 2025.7.25

# -----导入模块-----
import time, os, sys, json, gc, struct
from media.sensor import *
from media.display import *
from media.media import *
from machine import TOUCH   # 触摸系统

from time import sleep_ms

from MKS32C_uart import Stepmotor

from PID import PID

from task import *

# -----建立变量-----
lcd_size     = [800, 480]
frame_size   = [640, 480]
lcd_width = 800
lcd_height = 480
frame_width = 640
frame_height = 480
box_width  = 120
box_height = 40
top_margin = 10
box_spacing = 60
SetKeyNum = 16

sensor = None
tp = TOUCH(0)
flag = 1
touch_counter = 0
a, b, c, d = 10, 80, 10, 25

#threshold
black_line_threshold = [(29, 72)]
laser_threshold = []

# 配置文件路径
CONFIG_PATH = "/sdcard/config.json"

# -----配置相关功能-----
def save_config(LAB, Gray):
    config = {"LAB": LAB, "Gray": Gray}
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f)
        print("配置已保存到SD卡")
    except Exception as e:
        print(f"保存配置失败: {e}")

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        print("配置已加载")
        return config.get("LAB", [0,0,0,0,0,0]), config.get("Gray", [0,0])
    except Exception as e:
        print(f"加载配置失败: {e}")
        return [0,0,0,0,0,0], [0,0]

LAB, Gray = load_config()
LAB_test = LAB.copy()
Gray_test = Gray.copy()

try:
    motor = Stepmotor(1, 0)

    laser_pid_x = PID(kp=-2, ki=0, kd=0, setpoint=320, output_limits=(-20,20))
    laser_pid_y = PID(kp=-2, ki=0, kd=0, setpoint=320, output_limits=(-20,20))

    print("camera_test")
    sensor = Sensor(width=1280, height=960)
    sensor.reset()
    sensor.set_framesize(chn=CAM_CHN_ID_0, width=640, height=480)
    sensor.set_framesize(chn=CAM_CHN_ID_1, width=640, height=480)
    sensor.set_pixformat(Sensor.GRAYSCALE, chn=CAM_CHN_ID_0)
    sensor.set_pixformat(Sensor.RGB565, chn=CAM_CHN_ID_1)

    Display.init(Display.ST7701, to_ide=True)
    MediaManager.init()
    sensor.run()
    clock = time.clock()

    #------函数定义------
    def Key_GetNum(x, y, img, top_margin=10, SetKeyNum=16, box_w=box_width, box_h=box_height, box_s=box_spacing):
        left_x = 0
        right_x = lcd_width - box_w
        img.draw_circle(x, y, 15, color=(255,0,0), thickness=2, fill=True)
        if x >= left_x and x < left_x + box_w:
            y -= top_margin
            for idx in range(1, SetKeyNum + 1, 2):
                if y >= 0 and y < box_h:
                    img.draw_string_advanced(250, 120, 30, "Key: {}".format(idx), color=(0,0,255))
                    return idx
                y -= box_spacing
        elif x >= right_x and x < right_x + box_w:
            y -= top_margin
            for idx in range(2, SetKeyNum + 2, 2):
                if y >= 0 and y < box_h:
                    img.draw_string_advanced(250, 120, 30, "Key: {}".format(idx), color=(0,0,255))
                    return idx
                y -= box_spacing
        img.draw_string_advanced(250, 120, 30, "Key: None", color=(0,0,255))
        return None

    def Display_Words(img, index, text, top_margin=10, num=15, font=25, box_w=box_width, box_h=box_height, box_s=box_spacing):
        row = (index - 1) // 2
        y = top_margin + row * box_s + box_h // 2 - num
        if index % 2 == 1:
            x = box_w // 16
        else:
            x = frame_width - box_w * 15 // 16
        img.draw_string_advanced(x, y, font, text, color=(255,0,0))

    def Draw_Menu(img, box_w=box_width, box_h=box_height, box_s=box_spacing):
        for j in [0, frame_width - box_w]:
            for i in range(10, frame_height, box_s):
                img.draw_rectangle(j, i, box_w, box_h, color=(255,0,0), thickness=3, fill=False)

    def Update_Val(Key_num, var_value, Key_De, Key_Add, step=1, min_num=0, max_num=255):
        if Key_num == None:
            return var_value
        if Key_num == Key_De:
            return max(min_num, var_value - step)
        elif Key_num == Key_Add:
            return min(max_num, var_value + step)
        else:
            return var_value

    while True:
        clock.tick()
        os.exitpoint()
        img = sensor.snapshot(chn=CAM_CHN_ID_0)
        img_show = sensor.snapshot(chn=CAM_CHN_ID_1)
        points = tp.read()

        # 按键处理
        if points:
            print(points)
            for i in range(len(points)):
                print('x'+str(i)+'=', points[i].x, 'y'+str(i)+'=', points[i].y)
                KeyNum = Key_GetNum(points[i].x, points[i].y, img_show)
                print('KeyNum: {}'.format(KeyNum))
                if (KeyNum == None):
                    continue
                if (flag == 1):
                    pass
                if (flag == 2):
                    if (KeyNum >= 1 and KeyNum <= 11):
                        flag = KeyNum
                    else:
                        pass
                if (flag == 3):
                    if (KeyNum == 1 or KeyNum == 2):
                        flag = KeyNum
                    elif (KeyNum >= 3 and KeyNum <= 10):
                        a = Update_Val(KeyNum, a, 3, 4, 2, -20)
                        b = Update_Val(KeyNum, b, 5, 6, 1)
                        c = Update_Val(KeyNum, c, 7, 8, 3)
                        d = Update_Val(KeyNum, d, 9, 10, 2)
                    else:
                        pass
                if (flag == 4):
                    if (KeyNum == 1 or KeyNum == 2):
                        flag = KeyNum
                    elif (KeyNum >= 3 and KeyNum <= 14):
                        LAB_test[0] = Update_Val(KeyNum, LAB_test[0], 3, 4, 3, 0, 100)
                        LAB_test[1] = Update_Val(KeyNum, LAB_test[1], 5, 6, 3, 0, 100)
                        LAB_test[2] = Update_Val(KeyNum, LAB_test[2], 7, 8, 3, -128, 127)
                        LAB_test[3] = Update_Val(KeyNum, LAB_test[3], 9, 10, 3, -128, 127)
                        LAB_test[4] = Update_Val(KeyNum, LAB_test[4], 11, 12, 3, -128, 127)
                        LAB_test[5] = Update_Val(KeyNum, LAB_test[5], 13, 14, 3, -128, 127)
                    elif (KeyNum == 15):
                        pass
                    elif (KeyNum == 16):
                        LAB = LAB_test.copy()
                        save_config(LAB, Gray)
                    else:
                        pass
                if (flag == 5):
                    if (KeyNum == 1 or KeyNum == 2):
                        flag = KeyNum
                    elif (KeyNum >= 3 and KeyNum <= 6):
                        Gray_test[0] = Update_Val(KeyNum, Gray_test[0], 3, 4, 3, 0, 255)
                        Gray_test[1] = Update_Val(KeyNum, Gray_test[1], 5, 6, 3, 0, 255)
                    elif (KeyNum == 7):
                        pass
                    elif (KeyNum == 8):
                        Gray = Gray_test.copy()
                        save_config(LAB, Gray)
                    else:
                        pass

        # 长按进入菜单
        if len(points) > 0 and flag == 1:
            touch_counter += 1
            if touch_counter > 10:
                flag = 2
        else:
            touch_counter -= 2
            touch_counter = max(0, touch_counter)

        # UI绘制及阈值实时效果
        if (flag == 1):
            pass
        if (flag == 2):
            Draw_Menu(img_show)
            Display_Words(img_show, 1, "回到主页")
            Display_Words(img_show, 2, "回到菜单")
            Display_Words(img_show, 3, "调参模式")
            Display_Words(img_show, 4, "LAB调节")
            Display_Words(img_show, 5, "灰度调节")

        if (flag == 3):
            Draw_Menu(img_show)
            Display_Words(img_show, 1, "回到主页")
            Display_Words(img_show, 2, "回到菜单")
            Display_Words(img_show, 3, "a--")
            Display_Words(img_show, 4, "a++")
            Display_Words(img_show, 5, "b--")
            Display_Words(img_show, 6, "b++")
            Display_Words(img_show, 7, "c--")
            Display_Words(img_show, 8, "c++")
            Display_Words(img_show, 9, "d--")
            Display_Words(img_show, 10, "d++")

        if (flag == 4):
            # 实时应用LAB_test阈值到图像
            try:
                img_show.binary([(LAB_test[0], LAB_test[1], LAB_test[2], LAB_test[3], LAB_test[4], LAB_test[5])], auto=False)
            except Exception as e:
                img_show.draw_string_advanced(250, 200, 30, "LAB阈值异常", color=(255,0,0))
            Draw_Menu(img_show)
            Display_Words(img_show, 1, "回到主页")
            Display_Words(img_show, 2, "回到菜单")
            Display_Words(img_show, 3, "L_Min--")
            Display_Words(img_show, 4, "L_Min++")
            Display_Words(img_show, 5, "L_Max--")
            Display_Words(img_show, 6, "L_Max++")
            Display_Words(img_show, 7, "A_Min--")
            Display_Words(img_show, 8, "A_Min++")
            Display_Words(img_show, 9, "A_Max--")
            Display_Words(img_show, 10, "A_Max++")
            Display_Words(img_show, 11, "B_Min--")
            Display_Words(img_show, 12, "B_Min++")
            Display_Words(img_show, 13, "B_Max--")
            Display_Words(img_show, 14, "B_Max++")
            Display_Words(img_show, 15, "切换LAB")
            Display_Words(img_show, 16, "保存LAB")

        if (flag == 5):
            # 实时应用Gray_test阈值到图像
            try:
                img_show.binary([(Gray_test[0], Gray_test[1], -128, 127, -128, 127)], auto=False)
            except Exception as e:
                img_show.draw_string_advanced(250, 200, 30, "灰度阈值异常", color=(255,0,0))
            Draw_Menu(img_show)
            Display_Words(img_show, 1, "回到主页")
            Display_Words(img_show, 2, "回到菜单")
            Display_Words(img_show, 3, "G_Min--")
            Display_Words(img_show, 4, "G_Min++")
            Display_Words(img_show, 5, "G_Max--")
            Display_Words(img_show, 6, "G_Max++")
            Display_Words(img_show, 7, "切换灰度")
            Display_Words(img_show, 8, "保存灰度")

        if (flag == 6):
            task1(img=img, img_show=img_show, laser_threshold=[], blackline_threshold=black_line_threshold,
                  laser_pid_x=laser_pid_x, laser_pid_y=laser_pid_y, motor=motor)

        if (flag == 7):
            task2(img=img, img_show=img_show, laser_threshold=[], blackline_threshold=black_line_threshold,
                  laser_pid_x=laser_pid_x, laser_pid_y=laser_pid_y, motor=motor)
            pass

        if (flag == 8):
            pass

        if (flag == 9):
            pass

        if (flag == 10):
            pass

        if (flag == 11):
            pass


        #-----Draw画板-----
        img_show.draw_string_advanced(250, 160, 30, "a: {}".format(a), color=(0,255,255))
        img_show.draw_string_advanced(130, 200, 30, "LAB_test:" + str(LAB_test), color=(0,255,255))
        img_show.draw_string_advanced(130, 240, 30, "LAB_real:" + str(LAB), color=(0,255,255))
        img_show.draw_string_advanced(130, 280, 30, "G_test:" + str(Gray_test), color=(0,255,255))
        img_show.draw_string_advanced(130, 320, 30, "G_real:" + str(Gray), color=(0,255,255))

        #-----尾处理-----
        time.sleep_ms(5)
        img_show.draw_string_advanced(250, 80, 30, "flag: {}".format(flag), color=(0,255,255))
        img_show.draw_string_advanced(250, 40, 30, "fps: {}".format(clock.fps()), color=(0,255,255))
        Display.show_image(img_show, x=round((800-sensor.width())/2), y=round((480-sensor.height())/2))
        #print("fps: {}".format(clock.fps()))

except KeyboardInterrupt as e:
    print("用户停止: ", e)
except BaseException as e:
    print(f"异常: {e}")
finally:
    if isinstance(sensor, Sensor):
        sensor.stop()
    Display.deinit()
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)
    MediaManager.deinit()
