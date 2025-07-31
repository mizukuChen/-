'''
2023电赛发挥部分，绿激光追红激光走黑框

car库等没有的库，是针对我的硬件的驱动库。
如果你没有和我一样的硬件，是无法使用的。
所以程序仅供参考，可以在理解的前提下修改移植使用。

B站 @程欢欢的智能控制集 看完讲解视频
20230804
'''
import sensor, image, time, car, text
from time import sleep
'''
声明库部分
'''
#声明屏幕，程欢欢智能小车专属库。
screen=car.screen()
#声明蜂鸣器，程欢欢智能小车专属库。
buzzer=car.buzzer()

'''
全局变量
'''
pencil_points = [[67, 30], [248, 16], [294, 216], [37, 229], [166, 110]]  #铅笔画的方形的定点坐标和中心点坐标，共5组
laser_on_pencil_servo_value = [[102.243, 72.6351], [79.8784, 71.8379], [79.5676, 96.3784], [102.689, 96.5541], [91.6757, 84.8243], [102.392, 72.3919], [79.7973, 71.7027], [79.6081, 95.6487], [102.851, 96.2297], [91.3379, 84.4189]] #激光在铅笔痕迹上时，舵机的角度。用于校准
servo_rotation = 1  #自转轴舵机序号，程欢欢智能小车专属库。
servo_pitch = 0 #仰俯轴舵机序号，程欢欢智能小车专属库。
servo_rotation_value = 90  #两个舵机的当前角度。程欢欢小车体系中，以度为单位，支持浮点。
servo_pitch_value = 90  #这组变量建议固定初值为90。
servo_rotation_limit = [30,110]  #两个舵机的限位值，按需设置
servo_pitch_limit = [30,110]
servo_rotation_direction = False    #自转轴舵机的方向，数值增加，光点向右为真，反之为伪
servo_pitch_direction = True    #仰俯轴舵机的方向，数值增加，光点向下为真，反之为伪
taruge_rect_in_QQVGA = []   #A4纸黑线的定点坐标列表
function_running_num = 0 #当前运行功能选择
#0：停留在第一页面，没运行，
#1：停留在第二页面没运行，
#2：摄像头校准与激光棒自动校准，
#3：题目2绕铅笔路径，
#4：绕A4靶纸黑框的校准环节
#5：绕A4靶纸黑框

red_threshold = [(15, 75, 20, 90, 0, 60)]   #红色光点阈值
green_threshold = [(50, 100, -65, -15, -15, 40)]    #绿色光点阈值
laser_threshold=[(15, 75, 20, 90, 0, 60)]#[(85, 100, -20, 20, -20, 20)]   #激光颜色阈值
black_line_threshold=[(0, 30, -20, 20, -20, 20)]   #激光颜色阈值

clock = time.clock()

servo = car.servo_motor() #声明激光电源，因为激光电源用的是舵机供电
#servo.vout_off()  #关闭激光
servo.vout_on()  #打开激光
servo.channel_off(servo_rotation)   #关闭两个舵机信号
servo.channel_off(servo_pitch)
servo.channel_on(servo_rotation)   #打开两个舵机信号
servo.channel_on(servo_pitch)
'''
设置摄像头QVGA、降低亮度
'''
def sensor_set_QVGA_dark():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_vflip(True)  #针对我的硬件，颠倒画面
    sensor.set_hmirror(True)
    sensor.set_brightness(0)   #设置亮度
    sensor.set_contrast(0) #对比度
    #sensor.set_gainceiling(2)   #增益上限
    #sensor.set_auto_gain(False,gain_db=-1) #增益
    sensor.set_auto_exposure(False,500)  #曝光速度
sensor_set_QVGA_dark()#运行一次，对摄像头初始化

'''
激光云台，以绝对舵机角度移动.
注意，所有涉及舵机控制的程序，一定要包装成子函数再调用，防止超出范围损坏云台。
'''
def laser_move_by_degress(rotation, pitch):
    global servo_rotation,servo_pitch,servo_rotation_limit,servo_pitch_limit
    if servo_rotation_limit[0] < rotation < servo_rotation_limit[1]:
        servo.degree(servo_rotation,rotation)
    if servo_pitch_limit[0] < pitch < servo_pitch_limit[1]:
        servo.degree(servo_pitch,pitch)

'''
激光云台以画布增量坐标移动，坐标为原始值，并非实际像素值。
仅用于闭环移动程序
'''
def laser_move_increment(x,y):
    global servo_rotation,servo_pitch,servo_rotation_value,servo_pitch_value,\
        servo_rotation_limit,servo_pitch_limit,servo_rotation_direction,servo_pitch_direction
    if not servo_rotation_direction:#根据设置，是否调转x轴方向
        x = -x
    if not servo_pitch_direction:#根据设置，是否调转y轴方向
        y = -y
    #在限位内，驱动X轴，Y轴移动
    if servo_rotation_limit[0] < servo_rotation_value + x < servo_rotation_limit[1]:
        servo_rotation_value += x
        servo.degree(servo_rotation,servo_rotation_value)
    if servo_pitch_limit[0] < servo_pitch_value + y < servo_pitch_limit[1]:
        servo_pitch_value += y
        servo.degree(servo_pitch,servo_pitch_value)
'''
激光云台闭环移动到目标点（画布像素点）
只用了比例P，可能是我的舵机够好
要加PID可以使用OpenMV自带的PID库，直接加上
参数：
target_x,target_y-希望移动到的坐标
laser_x,laser_y-激光点的坐标
'''
def laser_move_to_traget_close_loop(target_x, target_y, laser_x, laser_y):
    laser_move_increment((target_x - laser_x)*0.03, (target_y - laser_y)*0.03)

'''
现场校准程序，手动将激光点，从左上角开始，顺时针依次落在铅笔正方形的角上
然后按下触屏（或其他输入装置）
最后落在中心点上，一共5个点。
'''
def cam_calibration():
    global pencil_points,laser_threshold
    pencil_points = []  #先清空原有数据
    sensor.set_brightness(-3)   #设置亮度
    sensor.set_contrast(3) #对比度
    sensor.set_auto_exposure(False,500)  #曝光速度
    servo.channel_off(servo_rotation)   #打开两个舵机信号
    servo.channel_off(servo_pitch)
    loop = True
    while loop:
        img = sensor.snapshot()
        blobs = img.find_blobs(laser_threshold)
        if blobs:
            img.draw_cross(blobs[0].cx(),blobs[0].cy(),color=(0,0,0))
            screen.get_touch()  #获取触屏触摸
            if screen.touch_exist():    #如果触摸存在
                if len(pencil_points)<5:#少于5组数据，未输入完成
                    #坐标追加如
                    pencil_points.append([blobs[0].cx(),blobs[0].cy()])
                    buzzer.frequency(500)
                    sleep(0.5)
                    buzzer.frequency(0)
                else: #等于5组数据，输入完成
                    loop = False
        for n in range(len(pencil_points)):
            img.draw_cross(pencil_points[n][0],pencil_points[n][1],color=(0,0,255))
            img.draw_string(pencil_points[n][0],pencil_points[n][1],str(n),color=(0,0,255))

        screen.display(img)
    servo.channel_on(servo_rotation)   #打开两个舵机信号
    servo.channel_on(servo_pitch)

'''
激光棒校准程序
使激光点落在铅笔方框的四个定点
和一个中心点，记录舵机角度
'''
def laser_calibration():
    global laser_threshold,pencil_points,laser_on_pencil_servo_value,laser_threshold,pencil_points

    sensor.set_brightness(-3)   #设置亮度
    sensor.set_contrast(3) #对比度
    sensor.set_auto_exposure(False,500)  #曝光速度
    servo.channel_on(servo_rotation)   #打开两个舵机信号
    servo.channel_on(servo_pitch)
    laser_move_by_degress(90,90)

    laser_point_stable_n = 0 #用于判断激光点是否稳定的计数

    move_pencil_step_tot = 30 #每个边细分成多少份进行移动
    move_pencil_point_n = 0  #临时存储变量，用于存储当前执行到铅笔方形的哪个角
    move_pencil_step_n = 0  #临时存储变量，用于存储在当前边的第几步。步总数参考上述变量。
    laser_calibration_enter_mode = True #录入模式，停止移动。录入完成后继续移动。
    loop = True
    while loop:
        img = sensor.snapshot()
        blobs = img.find_blobs(laser_threshold)
        if blobs:
            img.draw_cross(blobs[0].cx(),blobs[0].cy(),color=(0,0,0))
            if move_pencil_point_n == 4: #最后一定点，需要和第一个点作差
                x = (pencil_points[0][0] - pencil_points[4][0]) / move_pencil_step_tot *move_pencil_step_n + pencil_points[4][0]
                y = (pencil_points[0][1] - pencil_points[4][1]) / move_pencil_step_tot *move_pencil_step_n + pencil_points[4][1]
            else:
                x = (pencil_points[move_pencil_point_n + 1][0] - pencil_points[move_pencil_point_n][0]) / move_pencil_step_tot *move_pencil_step_n +pencil_points[move_pencil_point_n][0]
                y = (pencil_points[move_pencil_point_n + 1][1] - pencil_points[move_pencil_point_n][1]) / move_pencil_step_tot *move_pencil_step_n +pencil_points[move_pencil_point_n][1]
            print('x:'+str(x)+',y:'+str(y))
            laser_move_to_traget_close_loop(x, y, blobs[0].cx(),blobs[0].cy())
            if not laser_calibration_enter_mode:
                move_pencil_step_n += 1 #每边细分的步骤加1
                if move_pencil_step_n > move_pencil_step_tot:   #每边加满
                    laser_calibration_enter_mode = True #进入录入模式
                    move_pencil_step_n = 0  #步数清零
                    move_pencil_point_n += 1    #边序号加一
                    if move_pencil_point_n > 4: #边序号满
                        move_pencil_point_n = 0 #边序号清零
                        loop = False
            if laser_calibration_enter_mode:    #录入模式
                print(blobs[0].cx() - pencil_points[move_pencil_point_n][0])
                if abs(blobs[0].cx() - pencil_points[move_pencil_point_n][0]) < 3 and abs(blobs[0].cy() - pencil_points[move_pencil_point_n][1]) < 3:
                    laser_point_stable_n += 1
                else:
                    laser_point_stable_n = 0
                if laser_point_stable_n > 50:
                    laser_on_pencil_servo_value.append([servo.degree_state(servo_rotation), servo.degree_state(servo_pitch)])
                    laser_calibration_enter_mode = False

'''
绘制屏幕所显示的按键
page=1:
'''
def draw_button_on_screen(page):
    img = sensor.snapshot()
    img.clear()
    if page == 1:
        text.paragraph(img,40,45,'校准场地')
        text.paragraph(img,200,45,'开始运行')
    elif page == 2:
        text.paragraph(img,10,45,'题目2：绕场移动')
        text.paragraph(img,180,45,'题目3/4：A4靶纸')
    text.paragraph(img,60,165,'复位')
    text.paragraph(img,220,165,'暂停')
    img.draw_line(0,120,320,120)
    img.draw_line(160,0,160,240)
    screen.display(img)

draw_button_on_screen(1)
'''
针对规则的触屏功能按键。放在各个执行光点移动的循环里。
只有两个功能，分别为按屏幕左半边和右半边。
可以简单化的改成两个按键。
功能分别为：左半边复位(光点回到原点)，右半边暂停
停止状态下
'''
def screen_function_touch_button():
    global laser_on_pencil_servo_value,function_running_num
    screen.get_touch()  #获取触屏触摸
    if screen.touch_exist(): #如果触摸存在
        if screen.touch_y() <120:
            if screen.touch_x() < 160:  #左上角按键
                if function_running_num == 0: #在第一页面
                    function_running_num = 2 #校准场地
                    buzzer.frequency(500)
                    sleep(0.5)
                    buzzer.frequency(0)
                else:   #在第二页面
                    function_running_num = 3 #绕铅笔路径移动
                    buzzer.frequency(500)
                    sleep(0.5)
                    buzzer.frequency(0)

            else:   #右上角按键
                if function_running_num == 0: #在第一页面
                    function_running_num = 1 #进入第二页面
                    draw_button_on_screen(2)    #显示第二页面
                    buzzer.frequency(500)
                    sleep(0.5)
                    buzzer.frequency(0)
                else: #在第二页面
                    function_running_num = 4    #A4靶纸黑框校准
                    buzzer.frequency(500)
                    sleep(0.5)
                    buzzer.frequency(0)
        else:
            if screen.touch_x() < 160:  #左下角按键，固定为复位
                #暂存之前舵机角度
                last_rotation_value = servo.degree_state(servo_rotation)
                last_pitch_value = servo.degree_state(servo_pitch)
                #移动到中点
                laser_move_by_degress(laser_on_pencil_servo_value[-1][0], laser_on_pencil_servo_value[-1][1])
                buzzer.frequency(500)#蜂鸣器提示，外加0.5秒延迟防误触
                sleep(0.5)
                buzzer.frequency(0)
                while True:
                    screen.get_touch()  #获取触屏触摸
                    if screen.touch_exist():    #触摸任意位置返回
                        #之前的角度执行回去，不进行这个操作，直接回到之前的的闭环程序，极容易超调。
                        laser_move_by_degress(last_rotation_value,last_pitch_value)
                        buzzer.frequency(500)
                        sleep(0.5)
                        buzzer.frequency(0)
                        break
            else:   #右下角按键，固定为暂停
                buzzer.frequency(500)
                sleep(0.5)
                buzzer.frequency(0)
                while True:
                    screen.get_touch()  #获取触屏触摸
                    if screen.touch_exist():
                        if screen.touch_y() < 120:
                            if screen.touch_x() < 160:  #第二页左上角按键
                                function_running_num = 3 #绕铅笔路径移动
                                buzzer.frequency(500)
                                sleep(0.5)
                                buzzer.frequency(0)
                                break
                            else:   #第二页右上角按键
                                function_running_num = 4 #A4靶纸黑框校准
                                buzzer.frequency(500)
                                sleep(0.5)
                                buzzer.frequency(0)
                                break
                        else:   #下面两个按键：取消暂停
                            buzzer.frequency(500)
                            sleep(0.5)
                            buzzer.frequency(0)
                            break
    print(function_running_num)

'''
沿着铅笔方块移动的函数
闭环执行
'''
def move_follow_pencil_close_loop():
    global laser_threshold, pencil_points, function_running_num

    laser_move_by_degress(90,90)    #激光点回证
    sleep(0.5)  #使云台保持稳定，防止超调

    move_pencil_step_tot = 80 #每个边细分成多少份进行移动
    move_pencil_point_n = 0  #临时存储变量，用于存储当前执行到铅笔方形的哪个角
    move_pencil_step_n = 0  #临时存储变量，用于存储在当前边的第几步。步总数参考上述变量。

    while function_running_num == 3: #当前为3号功能，功能序号改变后自动退出
        clock.tick()
        img = sensor.snapshot()

        blobs = img.find_blobs(laser_threshold)
        if blobs:
            img.draw_cross(blobs[0].cx(),blobs[0].cy(),color=(0,0,0))
            if move_pencil_point_n == 3: #最后一定点，需要和第一个点作差
                x = (pencil_points[0][0] - pencil_points[3][0]) / move_pencil_step_tot *move_pencil_step_n + pencil_points[3][0]
                y = (pencil_points[0][1] - pencil_points[3][1]) / move_pencil_step_tot *move_pencil_step_n + pencil_points[3][1]
            else:
                x = (pencil_points[move_pencil_point_n + 1][0] - pencil_points[move_pencil_point_n][0]) / move_pencil_step_tot *move_pencil_step_n +pencil_points[move_pencil_point_n][0]
                y = (pencil_points[move_pencil_point_n + 1][1] - pencil_points[move_pencil_point_n][1]) / move_pencil_step_tot *move_pencil_step_n +pencil_points[move_pencil_point_n][1]
            #print('x:'+str(x)+',y:'+str(y))
            laser_move_to_traget_close_loop(x, y, blobs[0].cx(),blobs[0].cy())
            move_pencil_step_n += 1 #每边细分的步骤加1
            if move_pencil_step_n > move_pencil_step_tot:   #每边加满
                move_pencil_step_n = 0  #步数清零
                move_pencil_point_n += 1    #边序号加一
                if move_pencil_point_n > 3: #边序号满
                    move_pencil_point_n = 0 #边序号清零
        screen_function_touch_button()
        print(clock.fps())
'''
输入舵机角度关键节点，自动生成插补进行移动
输入参数：points-舵机角度的数组,格式为[[自转轴,仰俯轴],[自转轴,仰俯轴]...]
step_tot-每个边的分解步骤数量，数量越多越慢，但越稳定
step_time-每个步骤的等待时间
'''
def servo_degress_points_to_move(points, step_tot=100, step_time=0.02):
    loop = True
    point_n = 0 #临时存储用。记录当前进行到第几个节点（多边形的顶点）
    step_n = 0  #临时存储用。记录当前在一条边的哪个位置
    last_points_num = len(points) - 1
    while loop:
        if point_n == last_points_num:#最后一个节点，要与第一个节点作差
            #下面分别求自转轴和仰俯轴，在当前步骤下的过渡值
            ro = (points[0][0] - points[last_points_num][0]) / step_tot * step_n + points[last_points_num][0]
            pi = (points[0][1] - points[last_points_num][1]) / step_tot * step_n + points[last_points_num][1]
        else:
            ro = (points[point_n+1][0] - points[point_n][0]) / step_tot * step_n + points[point_n][0]
            pi = (points[point_n+1][1] - points[point_n][1]) / step_tot * step_n + points[point_n][1]
        laser_move_by_degress(ro, pi)
        step_n += 1
        if step_n > step_tot:
            step_n = 0
            point_n += 1
            if point_n > last_points_num:
                point_n = 0
        sleep(step_time)

'''
识别A4纸的黑线
'''
def detect_black_line():
    global pencil_points, red_threshold, taruge_rect_in_QQVGA
    sensor.reset()  #设置摄像头
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA)  #降低分辨率
    sensor.set_vflip(True)  #针对我的硬件，颠倒画面
    sensor.set_hmirror(True)
    sensor.set_brightness(0)   #设置亮度
    sensor.set_contrast(3) #对比度
    #sensor.set_gainceiling(2)   #增益上限
    sensor.set_auto_gain(False,gain_db=5) #增益
    #sensor.set_auto_exposure(True,800)  #曝光速度
    pencil_points_in_QQVGA = [] #针对QQVGA画幅的铅笔方框顶点坐标
    for n in range(4):
            pencil_points_in_QQVGA.append([round(pencil_points[n][0]*0.5), round(pencil_points[n][1]*0.5)])
            print(pencil_points_in_QQVGA[n])
    laser_move_by_degress(90,100)    #激光点扭转到画面外，防止影响识别
    last_taruge_rect_in_QQVGA = [[0,0],[0,0],[0,0],[0,0]]  #记录上一次识别到的定点数据，用来判断数据是否稳定
    loop = True
    matching_counts = 0#记录识别稳定不变的次数，达到一定数量则判断识别成功
    while loop:
        img = sensor.snapshot() #获取画面
        img.rotation_corr(corners = (pencil_points_in_QQVGA[:4]))   #画面梯形校正
        img.draw_image(img,0,0,x_size=120,y_size=120)   #缩放画面至正常比例
        img.draw_rectangle(120,0,40,120,color=(0,0,0),fill=True)    #右侧空白处涂黑
        img.midpoint(1, bias=0.9, threshold=True, offset=5, invert=True)    #凸显黑线
        rr = img.find_rects()   #找矩形
        if rr:  #如果有目标
            for r in rr:    #遍历目标，当然，目标应该只有一个
                taruge_rect_in_QQVGA = r.corners()  #存储方框顶点坐标
                img.draw_rectangle(r.rect(), color = (255, 0, 0))   #在屏幕绘制标识框
                for p in r.corners():   #绘制四个定点的标识
                    img.draw_circle(p[0], p[1], 5, color = (0, 255, 0))
                for n in range(4):#对比方框定点坐标数据的变动情况，判断是否获取成功
                    for n2 in range(2):
                        #注意，此处判断阈值为3，如果画面不稳定，可能程序无法向后进行。可以修改阈值。另外还可以增加低通滤波。
                        if abs(taruge_rect_in_QQVGA[n][n2] - last_taruge_rect_in_QQVGA[n][n2]) < 3:
                            matching_counts += 1
                            print(matching_counts)
                        else:
                            matching_counts = 0
                            print('识别失败')
                last_taruge_rect_in_QQVGA = taruge_rect_in_QQVGA
                if matching_counts > 300:
                    loop = False
                    print('识别成功')
                    sensor_set_QVGA_dark()
                    laser_move_by_degress(90,90)    #激光点回证
                    sleep(0.5)  #使云台保持稳定，防止超调

'''
闭环跑黑线
需要先运行detect_black_line()，生成过了黑线位置数据，才能运行下列函数
'''
def floow_black_line_close_loop():
    global pencil_points, red_threshold, taruge_rect_in_QQVGA
    taruge_rect = []
    x_offset = 0 #xy轴补偿量，暂时没用上
    y_offset = 0
    zoom_offset = 2 #缩放补偿量，正数缩小
    for n in range(3, -1, -1):#之前识别出的顶点数据是倒置的，在此既缩放，又倒置
        taruge_rect.append([round((taruge_rect_in_QQVGA[n][0]+x_offset)*2), round((taruge_rect_in_QQVGA[n][1]+y_offset)*2)])
    taruge_rect[0][0] += zoom_offset    #因为识别结果尺寸偏大
    taruge_rect[0][1] += zoom_offset    #用傻瓜方法手动补偿一下
    taruge_rect[1][0] -= zoom_offset
    taruge_rect[1][1] += zoom_offset
    taruge_rect[2][0] -= zoom_offset
    taruge_rect[2][1] -= zoom_offset
    taruge_rect[3][0] += zoom_offset
    taruge_rect[3][1] -= zoom_offset

    while function_running_num == 5:
        move_pencil_step_tot = 100 #每个边细分成多少份进行移动
        move_pencil_point_n = 0  #临时存储变量，用于存储当前执行到铅笔方形的哪个角
        move_pencil_step_n = 0  #临时存储变量，用于存储在当前边的第几步。步总数参考上述变量。
        while function_running_num == 5 :
            clock.tick()
            img = sensor.snapshot()
            img.rotation_corr(corners = (pencil_points[:4]))
            img.draw_image(img,0,0,x_size=240,y_size=240)
            img.draw_rectangle(240,0,80,240,color=(0,0,0),fill=True)
            blobs = img.find_blobs(red_threshold)
            if blobs:
                img.draw_cross(blobs[0].cx(),blobs[0].cy(),color=(0,0,0))
                if move_pencil_point_n == 3: #最后一定点，需要和第一个点作差
                    x = (taruge_rect[0][0] - taruge_rect[3][0]) / move_pencil_step_tot *move_pencil_step_n + taruge_rect[3][0]
                    y = (taruge_rect[0][1] - taruge_rect[3][1]) / move_pencil_step_tot *move_pencil_step_n + taruge_rect[3][1]
                else:
                    x = (taruge_rect[move_pencil_point_n + 1][0] - taruge_rect[move_pencil_point_n][0]) / move_pencil_step_tot *move_pencil_step_n +taruge_rect[move_pencil_point_n][0]
                    y = (taruge_rect[move_pencil_point_n + 1][1] - taruge_rect[move_pencil_point_n][1]) / move_pencil_step_tot *move_pencil_step_n +taruge_rect[move_pencil_point_n][1]
                #print('x:'+str(x)+',y:'+str(y))
                laser_move_to_traget_close_loop(x, y, blobs[0].cx(),blobs[0].cy())
                move_pencil_step_n += 1 #每边细分的步骤加1
                if move_pencil_step_n > move_pencil_step_tot:   #每边加满
                    move_pencil_step_n = 0  #步数清零
                    move_pencil_point_n += 1    #边序号加一
                    if move_pencil_point_n > 3: #边序号满
                        move_pencil_point_n = 0 #边序号清零
            screen_function_touch_button()
            print(clock.fps())

'''
主函数
'''
while True:
    screen_function_touch_button()  #获取输入按键，自动赋值function_running_num，后续就可以执行对应功能

    if function_running_num == 2:#摄像头与激光笔校准功能
        cam_calibration()   #摄像头校准
        laser_calibration() #激光棒校准
        function_running_num = 1    #第二页面未选中功能
        draw_button_on_screen(2)    #绘制第二页面

    elif function_running_num == 3: #题目2：绕铅笔路径
        move_follow_pencil_close_loop()

    elif function_running_num == 4: #题目3/4：绕A4靶纸。当前序号4为识别黑框
        detect_black_line()
        function_running_num = 5    #运行绕A4靶纸
        floow_black_line_close_loop()
