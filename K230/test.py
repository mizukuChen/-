from machine import Pin
from machine import FPIOA
import time




# 实例化FPIOA
fpioa = FPIOA()

#将所需引脚配置为普通GPIO
fpioa.set_function(52,FPIOA.GPIO52)
fpioa.set_function(51,FPIOA.GPIO51)
fpioa.set_function(50,FPIOA.GPIO50)
fpioa.set_function(49,FPIOA.GPIO49)
fpioa.set_function(48,FPIOA.GPIO48)
fpioa.set_function(47,FPIOA.GPIO47)
fpioa.set_function(46,FPIOA.GPIO46)
fpioa.set_function(45,FPIOA.GPIO45)

# 常量定义
STEPS_PER_CIRCLE = 4096  # 每圈步数
DEG_PER_STEP = 360.0 / STEPS_PER_CIRCLE  # 每步角度

# 步进序列 (8步驱动)
STEP_SEQUENCE = (
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 1, 0),
    (0, 0, 1, 1),
    (0, 0, 0, 1),
    (1, 0, 0, 1)
)

class Stepper:
    def __init__(self, Xin_pins, Yin_pins):
        """
        初始化步进电机控制器
        :param Xin_pins: 横向电机引脚列表 [IN1, IN2, IN3, IN4]
        :param Yin_pins: 纵向电机引脚列表 [IN1, IN2, IN3, IN4]
        """
        # 初始化横向电机引脚
        self.Xin = [Pin(pin, Pin.OUT) for pin in Xin_pins]
        # 初始化纵向电机引脚
        self.Yin = [Pin(pin, Pin.OUT) for pin in Yin_pins]
        # 当前步进位置
        self.step_pos = [0, 0]  # [横向位置, 纵向位置]

    def _write_pins(self, pins, states):
        """设置指定引脚组的状态"""
        for pin, state in zip(pins, states):
            pin.value(state)

    def step(self, motor_idx, steps, delay_ms):
        """
        驱动步进电机移动指定步数
        :param motor_idx: 电机索引 (0=横向, 1=纵向)
        :param steps: 步数 (正数=正向, 负数=反向)
        :param delay_ms: 步间延迟(毫秒)，控制速度
        """
        direction = 1 if steps >= 0 else -1
        steps = abs(steps)

        for _ in range(steps):
            # 获取当前步进状态
            current_step = self.step_pos[motor_idx]

            # 设置对应电机
            if motor_idx == 0:  # 横向电机
                self._write_pins(self.Xin, STEP_SEQUENCE[current_step])
            else:  # 纵向电机
                self._write_pins(self.Yin, STEP_SEQUENCE[current_step])

            # 步间延迟
            time.sleep_ms(delay_ms)

            # 更新步进位置 (确保在0-7范围内)
            self.step_pos[motor_idx] = (current_step + direction) % 8

    def turn_angle(self, motor_idx, angle_deg, delay_ms):
        """
        旋转指定角度
        :param motor_idx: 电机索引 (0=横向, 1=纵向)
        :param angle_deg: 旋转角度(度)
        :param delay_ms: 步间延迟(毫秒)
        """
        steps = int(angle_deg / DEG_PER_STEP + 0.5)
        self.step(motor_idx, steps, delay_ms)

    def turn_circle(self, motor_idx, circles, delay_ms):
        """
        旋转指定圈数
        :param motor_idx: 电机索引 (0=横向, 1=纵向)
        :param circles: 圈数 (正数=正向, 负数=反向)
        :param delay_ms: 步间延迟(毫秒)
        """
        steps = int(circles * STEPS_PER_CIRCLE)
        self.step(motor_idx, steps, delay_ms)


Xin = [12,14,16,18]
Yin = [32,33,34,35]
fpioa.set_function(32,FPIOA.GPIO32)
fpioa.set_function(33,FPIOA.GPIO33)
fpioa.set_function(34,FPIOA.GPIO34)
fpioa.set_function(35,FPIOA.GPIO35)
#fpioa.set_function(13,FPIOA.GPIO13)
stepper = Stepper(Xin,Yin)
while True:
    stepper.step(1, -50, 3)
    time.sleep(2)
    pass
