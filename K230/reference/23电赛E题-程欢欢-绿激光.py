'''
2023电赛发挥部分，绿激光追红激光走黑框

car库等没有的库，是针对我的硬件的驱动库。
如果你没有和我一样的硬件，是无法使用的。
所以程序仅供参考，可以在理解的前提下修改移植使用。

因为绿激光规则的临时修改，我手头的硬件无法完成摄像头随激光棒移动
所以这套程序仅做到跟随红激光为止，没有精细优化。
但也是极具参考价值的。

B站 @程欢欢的智能控制集 看完讲解视频
20230804
'''
import sensor, image, time, car
from time import sleep

red_threshold = [(15, 75, 18, 90, 0, 60)]   #红色光点阈值
green_threshold = [(80, 100, -65, 10, -20, 21)]#[(25, 100, -65, -15, -15, 40)]    #绿色光点阈值
black_line_threshold = [(0, 36, -128, 19, -21, 6)]  #A4靶纸阈值
servo_rotation = 1
servo_pitch = 0
servo_rotation_limit = [0,180]  #两个舵机的限位值，按需设置
servo_pitch_limit = [30,110]
servo_rotation_value = 90  #两个舵机的当前角度。程欢欢小车体系中，以度为单位，支持浮点。
servo_pitch_value = 90  #这组变量建议固定初值为90。
servo_rotation_direction = False    #自转轴舵机的方向，数值增加，光点向右为真，反之为伪
servo_pitch_direction = True    #仰俯轴舵机的方向，数值增加，光点向下为真，反之为伪
kp = 0.02
dead_zone_x = 20
dead_zone_y = 20
#修改这两个变量，可以调整跟踪分辨率和距离
refresh_data_threshold = 2  #当大于这个距离（单位像素），新的点将被记录
tracking_distance = 7 #绿点追踪红点的距离，大于它（单位像素）

servo = car.servo_motor() #声明激光电源，因为激光电源用的是舵机供电
servo.vout_off()  #关闭激光
servo.vout_on()  #打开激光
servo.channel_off(servo_rotation)   #关闭两个舵机信号
servo.channel_off(servo_pitch)
servo.channel_on(servo_rotation)   #打开两个舵机信号
servo.channel_on(servo_pitch)

def sensor_set():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    #这套系统的机位是倾斜的，为避免拍到幕布外的黑色区域，对画面做了切割
    sensor.set_windowing(40,0,280,240)
    sensor.set_vflip(True)  #针对我的硬件，颠倒画面
    sensor.set_hmirror(True)
    sensor.set_brightness(-2)   #设置亮度
    sensor.set_contrast(3) #对比度
    #sensor.set_gainceiling(2)   #增益上限
    #sensor.set_auto_gain(False,gain_db=-1) #增益
    #sensor.set_auto_exposure(False,600)  #曝光速度

sensor_set()#运行一次，对摄像头初始化
'''
激光云台，以绝对舵机角度移动.
注意，所有涉及舵机控制的程序，一定要包装成子函数再调用，防止超出范围损坏云台。
'''
def laser_move_by_degress(rotation, pitch):
    global servo_rotation,servo_pitch,servo_rotation_limit,servo_pitch_limit
    pitch -= 10
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
'''

laser_move_by_degress(90,90)#回正
sleep(0.5)

clock = time.clock()
'''
红点历史记录系统
'''
#系统依次循环记录红色点的历史坐标。当红色点移动超过阈值，则记录
red_coordinates_tot_num = 10
red_coordinates = [] #红色点的历史坐标
for n in range(red_coordinates_tot_num):
    red_coordinates.append([-1,-1])
red_coordinate_n = 0 #当前记录的红色点，在列表中的序号

tracking_target = [-1,-1]   #绿点追踪的目标坐标（单位像素）

sensor_x = 50
sensor_y = 50
'''
针对黑线边框放大画面
因为OpenMV4不能开VGA画幅进行识别，而QVGA画幅下，正对着的机位效果还行
绿激光倾斜的机位，识别效果就不太好了。所以针对黑框
'''
def zoom_up_black_line():
    sensor_set()
    sleep(1)
    last_cx = -1
    last_cy = -1
    num = 0
    while True:
        img = sensor.snapshot()
        balck_line_blobs = img.find_blobs(black_line_threshold)
        if balck_line_blobs:
            balck_line_blob = max(balck_line_blobs, key = lambda b: b[4])
            img.draw_cross(balck_line_blob.cx(),balck_line_blob.cy(),color=(0,0,0))
            img.draw_rectangle(balck_line_blob[0:4])
            print(balck_line_blob[0:4])
            if abs(last_cx - balck_line_blob.cx()) < 4 and abs(last_cy - balck_line_blob.cy()) < 4:
                num += 1
            if num > 100:#定位成功
                sensor.set_framesize(sensor.VGA)
                #因为最初的画面，左侧是切掉40的，所以x轴补偿40。另外两轴分别再补偿20，基本方框可以完整显示。
                sensor.set_windowing(round(balck_line_blob[0]*2)+60, round(balck_line_blob[1]*2)-20 ,320,320)
                print(round(balck_line_blob[0]*2))
                break
            last_cx = balck_line_blob.cx()
            last_cy = balck_line_blob.cy()

'''
跟随移动中的红激光点
'''
def follow_moving_laser():
    global red_threshold,green_threshold,refresh_data_threshold,\
            tracking_distance,tracking_target,red_coordinate_n
    while True:
        clock.tick()
        img = sensor.snapshot()
        #找红色点
        red_blobs = img.find_blobs(red_threshold)
        if red_blobs:
            red_blob = max(red_blobs, key = lambda b: b[4])
            img.draw_cross(red_blob.cx(),red_blob.cy(),color=(0,0,0))
            #计算当前坐标和上一个坐标的距离
            if red_coordinate_n == 0:
                distance = ((red_blob.cx() - red_coordinates[red_coordinates_tot_num-1][0])**2 + (red_blob.cy() - red_coordinates[red_coordinates_tot_num-1][1])**2)**0.5
            else:
                distance = ((red_blob.cx() - red_coordinates[red_coordinate_n-1][0])**2 + (red_blob.cy() - red_coordinates[red_coordinate_n-1][1])**2)**0.5
            #距离大于数据刷新阈值，则被记录
            if distance > refresh_data_threshold:
                red_coordinates[red_coordinate_n] = [red_blob.cx(), red_blob.cy()]
                red_coordinate_n += 1
                if red_coordinate_n > red_coordinates_tot_num-1:
                    red_coordinate_n = 0
            #当前坐标数据，和以往坐标计算距离，直到找到大于追踪距离阈值的数值
            n = red_coordinate_n-1#上一个坐标数据的序号
            while True:
                if red_coordinates[n][0] > 0 and red_coordinates[n][1] >0:#坐标值有效的话
                    distance = ((red_blob.cx() - red_coordinates[n][0])**2 + (red_blob.cy() - red_coordinates[n][1])**2)**0.5
                    if distance >= tracking_distance:#获得大于阈值的点
                        break
                n -= 1
                if n<0 :
                    n = red_coordinates_tot_num - 1
                elif n == red_coordinate_n: #遍历完一遍了
                    break   #跳出
            if n != red_coordinate_n:   #如果不是遍历到尽头的话，说明数值有效
                tracking_target = [red_coordinates[n][0],red_coordinates[n][1]]
                #绘制具体追踪的点
                #img.draw_circle(tracking_target[0],tracking_target[1],5,color=(0,255,0),fill=True)
                #print(tracking_target)
            else:   #否则装填无效数值
                tracking_target = [-1,-1]

        #绘制所有记录的数据，注意，这部分绘制，会影响后续程序识别画面
        #for n in range(red_coordinates_tot_num):
            #img.draw_circle(red_coordinates[n][0],red_coordinates[n][1],3,fill=True)

        #找绿色点
        green_blobs = img.find_blobs(green_threshold)
        if green_blobs:
            green_blob = max(green_blobs, key = lambda b: b[4])
            img.draw_cross(green_blob.cx(),green_blob.cy(),color=(0,0,0))

        #else:
            #sensor.set_framesize(sensor.QVGA)
        #如果红绿点都存在
        if green_blobs and tracking_target[0]>0:
            x_move = (tracking_target[0] - green_blob.cx())*kp
            y_move = (tracking_target[1] - green_blob.cy())*kp
            laser_move_increment(x_move, y_move)

        #print(clock.fps())

zoom_up_black_line()#执行看A4靶纸黑线区域，并放大它。
follow_moving_laser()

while True:
    pass
