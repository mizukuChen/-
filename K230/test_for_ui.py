from machine import TOUCH   # 触摸系统
import time, os, sys, gc, struct, ujson

from media.sensor import * #Import the sensor module and use the camera API
from media.display import * #Import the display module and use display API
from media.media import * #Import the media module and use meida API

from machine import Pin
from machine import FPIOA
from machine import UART

from time import sleep_ms

# -----建立变量-----
# 尺寸初始化
lcd_size     = [800 , 480]
frame_size   = [640 , 480]
# LCD屏幕尺寸
lcd_width = 800
lcd_height = 480
# LCD展示尺寸
frame_width = 640
frame_height = 480
# 按键尺寸
box_width  = 120
box_height = 40
# 按键方块间隔
top_margin = 10     # 第一个按键距离LCD上部的间隔(留点距离防止误触,并且美观)
box_spacing = 60    # 各个按键之间的上下间隔,记得要小于按键高度 box_height
SetKeyNum = 16      # 设定的按键数目(一般来说12个够用了,并且还宽敞)
'''
按键数目的两个调整
1.box_height = 60   box_spacing = 80    num = 20    SetKeyNum = 12
2.box_height = 40   box_spacing = 60    num = 15    SetKeyNum = 16
'''

# json导入路径
json_path = ""

# 摄像头初始化
sensor = None
# 触摸初始化
tp = TOUCH(0)
# 触摸系统变量
flag = 1            # 系统标志位初始化
touch_counter = 0   # 长按时间计时
# 一些调试参数
a, b, c, d = 10, 80, 10, 25
LAB = [0,0,0,0,0,0]
LAB_test = [0,0,0,0,0,0]
Gray = [0,0]
Gray_test = [0,0]
LAB_invert = False
Gray_invert = False
## 考虑加入invert参数

# -----配置相关功能-----
try:
    print("camera_test")
    # 初始化摄像头
    sensor = Sensor(width=1280, height=960) # width=1280, height=960
    sensor.reset()
    sensor.set_framesize(chn=CAM_CHN_ID_0, width=640, height=480) # width=320,height=240
    sensor.set_framesize(chn=CAM_CHN_ID_1, width=640, height=480)
    sensor.set_pixformat(Sensor.RGB565)

    Display.init(Display.ST7701, to_ide=True)   # 初始化显示器
    MediaManager.init()                         # 初始化媒体管理器
    sensor.run()                                # 启动 sensor
    clock = time.clock()                        # 开始计时帧率

    #------函数定义------
    # ----1.按键检测----
    def Key_GetNum(x, y, img, top_margin=10 , SetKeyNum=16 , box_w=box_width , box_h=box_height , box_s=box_spacing):
        left_x = 0            # 左边的x
        right_x = frame_width - box_w # 右边的x
        img.draw_circle(x, y, 15 , color = (255,0, 0) , thickness = 2, fill = True) # 画辅助圆指引按键位置
        # 左边列按钮
        if x >= left_x and x < left_x + box_w:
            y -= top_margin  # 去掉顶部边距方便判断
            for idx in range(1, SetKeyNum + 1, 2):  # 按钮编号1,3,5,...,11
                if y >= 0 and y < box_h:
                    # 展示按键号码
                    img.draw_string_advanced(250, 120, 30 , "Key: {}".format(idx), color = (0, 0, 255))
                    return idx
                y -= box_spacing  # 判断是否是下一个按键

        # 右边列按钮
        elif x >= right_x and x < right_x + box_w:
            y -= top_margin
            for idx in range(2, SetKeyNum + 2 , 2):  # 按钮编号2,4,6,...,12
                if y >= 0 and y < box_h:
                    # 展示按键号码
                    img.draw_string_advanced(250, 120, 30 , "Key: {}".format(idx), color = (0, 0, 255))
                    return idx
                y -= box_spacing  # 判断是否是下一个按键
        # 触摸点不在按钮范围
        img.draw_string_advanced(250, 120, 30 , "Key: None", color = (0, 0, 255))
        return None

    # ----2.字体展示换算----
    def Display_Words(img, index, text , top_margin = 10 , num = 15 , font = 25, box_w = box_width , box_h = box_height , box_s = box_spacing):
        # 计算行号（0-5），index范围1-12
        row = (index - 1) // 2

        # 计算y坐标，文字靠近按钮中心向上调整一点
        y = top_margin + row * box_s + box_h // 2 - num # 20 这个数字可更改,凭感觉调节这个数字

        # 判断左右列，左列奇数，右列偶数
        if index % 2 == 1:
            x = box_w // 16     # 经过调整,这个位置还行
        else:
            x = frame_width - box_w * 15 // 16  # 经过调整,这个位置还行

        # 绘制文字
        img.draw_string_advanced(x, y, font, text, color=(255, 255, 255))

    # ----3.菜单展示(flag = 2)----
    def Draw_Menu(img, box_w=box_width , box_h=box_height , box_s=box_spacing):
        for j in [0, frame_width-box_w]:  # 一共就两个x轴位置:左 , 右
            for i in range(10, frame_height, box_s):
                img.draw_rectangle(j, i, box_w, box_h, color=(255, 255, 255), thickness=3, fill=False)

    # ----4.按键加减处理----
    def Update_Val(Key_num, var_value, Key_De, Key_Add, step=1 , min_num=0 , max_num=255):
        if Key_num == None :
            return var_value                         # 不变
        if Key_num == Key_De:                        # 标准减少的键码
            return max(min_num, var_value-step )  # 减少
        elif Key_num == Key_Add:                     # 标准增加的键码
            return min(max_num, var_value+step )  # 增加
        else:
            return var_value                         # 不变



    while True:
        # 计算帧率
        clock.tick()
        os.exitpoint()

        # 拍照
        img = sensor.snapshot(chn=CAM_CHN_ID_0)
        img_show = sensor.snapshot(chn=CAM_CHN_ID_1)

        #-----核心代码----------------------------------------------------------------------------------
        points = tp.read()
        # 坐标展示
        if points != () :
            print(points) # 打印原始数据
            for i in range(len(points)):
                print('x'+str(i)+'=', points[i].x, 'y'+str(i)+'=', points[i].y)
                KeyNum = Key_GetNum(points[i].x, points[i].y, img)
                print('KeyNum: {}'.format(KeyNum))
                # 菜单选择功能,后端实现标志位变化
                # 要记得是先有flag设定UI界面,再有相应界面的功能,所以if 判断(后续实现相关功能)与flag有关
                if (KeyNum == None):
                    continue
                if (flag == 1):

                    pass
                if (flag == 2):
                    if (KeyNum >= 1 and KeyNum <= 5): #这样的原因在于如果不限制其他未定义按键,flag会被任意更改,造成一些问题
                        # 逻辑:按下1,回到主页(flag!=2,UI页面消失),按下2,没变 , 按下其他:去别的功能,反正flag != 2,菜单UI页面自然消失
                        flag = KeyNum
                    else :
                        pass
                if (flag == 3):
                    if (KeyNum == 1 or KeyNum == 2):
                        # 逻辑:按下1,回到主页(flag!=2,UI页面消失),按下2,回到菜单, 按下其他:进行调参
                        flag = KeyNum
                    elif (KeyNum >= 3 and KeyNum <= 10):
                        a = Update_Val(KeyNum , a , 3 , 4 , 2 , -20 )
                        b = Update_Val(KeyNum , b , 5 , 6 , 1)
                        c = Update_Val(KeyNum , c , 7 , 8 , 3)
                        d = Update_Val(KeyNum , d , 9 ,10 , 2)
                    else:
                        pass
                if (flag == 4):
                    if (KeyNum == 1 or KeyNum == 2):
                        # 逻辑:按下1,回到主页(flag!=2,UI页面消失),按下2,回到菜单, 按下其他:进行调参
                        flag = KeyNum
                    elif (KeyNum >= 3 and KeyNum <= 14):
                        LAB_test[0] = Update_Val(KeyNum , LAB_test[0] , 3 , 4 , 3 ,  0 , 100)
                        LAB_test[1] = Update_Val(KeyNum , LAB_test[1] , 5 , 6 , 3 ,  0 , 100)
                        LAB_test[2] = Update_Val(KeyNum , LAB_test[2] , 7 , 8 , 3 ,-128, 127)
                        LAB_test[3] = Update_Val(KeyNum , LAB_test[3] , 9 ,10 , 3 ,-128, 127)
                        LAB_test[4] = Update_Val(KeyNum , LAB_test[4] ,11 ,12 , 3 ,-128, 127)
                        LAB_test[5] = Update_Val(KeyNum , LAB_test[5] ,13 ,14 , 3 ,-128, 127)
                    elif (KeyNum == 15):
                        pass
                    elif (KeyNum == 16):
                        LAB = LAB_test.copy()
                    else:
                        pass
                img_show.binary(threshold=[(LAB[0], LAB[1], LAB[2], LAB[3], LAB[4], LAB[5])])##调整binary

                if (flag == 5):
                    if (KeyNum == 1 or KeyNum == 2):
                        # 逻辑:按下1,回到主页(flag!=2,UI页面消失),按下2,回到菜单, 按下其他:进行调参
                        flag = KeyNum
                    elif (KeyNum >= 3 and KeyNum <= 6):
                        Gray_test[0] = Update_Val(KeyNum , Gray_test[0] ,3 ,4 ,3 , 0, 255)
                        Gray_test[1] = Update_Val(KeyNum , Gray_test[1] ,5 ,6 ,3 , 0, 255)
                    elif (KeyNum == 7):
                        pass
                    elif (KeyNum == 8):
                        Gray = Gray_test.copy()
                    else:
                        pass
                img_show.binary(threshold=[(Gray[0], Gray[1])])##调整binary
                ## 在此处插入保存json文件代码
                #constant_dict = {'a': a, 'b': b, 'c': c, 'd': d, 'LAB': LAB, 'Gray': Gray}
                #json_str = ujson.dump(constant_dict)
                #print(json_str)
        # -----功能实现-----

        # 1.状态选择:长按1秒钟进入UI菜单
        if len(points) > 0 and flag == 1:
            touch_counter += 1
            if touch_counter > 10:
                flag = 2
        else:
            touch_counter -= 2
            touch_counter = max(0, touch_counter)

        # 2.UI菜单绘图
        if (flag == 1):
            pass
        if (flag == 2):
            Draw_Menu(img)
            Display_Words(img , 1 , "回到主页")
            Display_Words(img , 2 , "回到菜单")
            Display_Words(img , 3 , "调参模式")
            Display_Words(img , 4 , "LAB调节")
            Display_Words(img , 5 , "灰度调节")

        if (flag == 3):
            Draw_Menu(img)
            Display_Words(img , 1 , "回到主页")
            Display_Words(img , 2 , "回到菜单")
            Display_Words(img , 3 , "a--")
            Display_Words(img , 4 , "a++")
            Display_Words(img , 5 , "b--")
            Display_Words(img , 6 , "b++")
            Display_Words(img , 7 , "c--")
            Display_Words(img , 8 , "c++")
            Display_Words(img , 9 , "d--")
            Display_Words(img ,10 , "d++")

        if (flag == 4):
            Draw_Menu(img)
            Display_Words(img , 1 , "回到主页")
            Display_Words(img , 2 , "回到菜单")

            Display_Words(img , 3 , "L_Min--")
            Display_Words(img , 4 , "L_Min++")

            Display_Words(img , 5 , "L_Max--")
            Display_Words(img , 6 , "L_Max++")

            Display_Words(img , 7 , "A_Min--")
            Display_Words(img , 8 , "A_Min++")

            Display_Words(img , 9 , "A_Max--")
            Display_Words(img ,10 , "A_Max++")

            Display_Words(img ,11 , "B_Min--")
            Display_Words(img ,12 , "B_Min++")

            Display_Words(img ,13 , "B_Max--")
            Display_Words(img ,14 , "B_Max++")

            Display_Words(img ,15 , "切换LAB")
            Display_Words(img ,16 , "保存LAB")

        if (flag == 5):
            Draw_Menu(img)
            Display_Words(img , 1 , "回到主页")
            Display_Words(img , 2 , "回到菜单")

            Display_Words(img , 3 , "G_Min--")
            Display_Words(img , 4 , "G_Min++")

            Display_Words(img , 5 , "G_Max--")
            Display_Words(img , 6 , "G_Max++")

            Display_Words(img , 7 , "切换灰度")
            Display_Words(img , 8 , "保存灰度")
        #-----Draw画板-----

        img.draw_string_advanced(250, 160, 30 , "a: {}".format(a), color = (0, 255, 255))

        img.draw_string_advanced(130, 200, 30 , "LAB_test:" + str(LAB_test), color = (0, 255, 255))
        img.draw_string_advanced(130, 240, 30 , "LAB_real:" + str(LAB), color = (0, 255, 255))

        img.draw_string_advanced(130, 280, 30 , "G_test:" + str(Gray_test), color = (0, 255, 255))
        img.draw_string_advanced(130, 320, 30 , "G_real:" + str(Gray), color = (0, 255, 255))

        #-----尾处理------------------------------------------------------------------------------------
        # 延时,防止系统boom
        time.sleep_ms(50)
        # 展示标志位
        img.draw_string_advanced(250, 80, 30 , "flag: {}".format(flag), color = (0, 255, 255))
        # 展示图像和帧率
        img.draw_string_advanced(250, 40, 30 , "fps: {}".format(clock.fps()), color = (0, 255, 255))

        # 画面裁切:增加帧率 , 宽和高必须是8的倍数
        #img = img.copy(roi = (296,132,320,256))
        #img.compressed_for_ide()    # 伸展图像到正中间
        Display.show_image(img_show) # 由于画面没有充满全屏,如果将画面进行居中处理会使得按下位置与实际位置不合,所以先使用默认配置x,y = 0
        print("fps: {}".format(clock.fps()))

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

'''
语法:
1.

'''

'''
思路:
    使用flag
    flag = 1 : 比赛模式

    flag = 2 : 选择功能模式

    flag = 3 : 数字增减模式
    flag = 4 : 阈值调节模式:LAB
    flag = 5 : 阈值调节模式:灰度
    flag = 6 : 待开发
本质上都是调节某一个数字的值而已
建立一个左6右6的UI界面,一共12个功能,理论上一定够用了
数字增减为底层基础
阈值调节:
    回到主程序   回到菜单
    L_min       L_max
    A_min       L_max
    B_min       B_max
    保存         重置
        其他按键
灰度调节:
    回到主程序   回到菜单
    min        max
    保存        重置
'''

""" def read_deploy_config(config_path):
    # 打开JSON文件以进行读取deploy_config
    with open(config_path, "r") as json_file:
        try:
            # 从文件中加载JSON数据
            config = ujson.load(json_file)
        except ValueError as e:
            print("JSON 解析错误:", e)
    return config """