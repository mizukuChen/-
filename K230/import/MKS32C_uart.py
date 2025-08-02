import machine
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

