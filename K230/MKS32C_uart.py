import machine
import struct

# 常量定义
ANGLE_MODE = 1.8
STEP_MODE = 16
STEPS_PER_CIRCLE = int(360 / ANGLE_MODE * STEP_MODE)
DEG_PER_STEP = 1.0 / ANGLE_MODE * STEP_MODE
TURN_FORWARD = 1
TURN_REVERSE = 0

# 初始化UART（根据实际硬件连接修改引脚）
# 示例：UART(3) for STM32, UART(2) for ESP32等
uart = machine.UART(1, baudrate=115200, timeout=50)

def get_check_sum(data):
    """计算校验和（求和取低8位）"""
    return sum(data) & 0xFF

def speed_mode_uart(motor_id, direction, speed):
    """速度模式控制"""
    # 确保速度在0-127范围内
    speed = max(0, min(127, speed))
    tx_data = bytearray(4)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0xF6             # 功能码
    tx_data[2] = (direction << 7) | (speed & 0x7F)  # 方向+速度
    tx_data[3] = get_check_sum(tx_data[:3])  # 校验和

    uart.write(tx_data)

def position_mode_uart(motor_id, speed, angle):
    """位置模式控制"""
    # 计算脉冲数并确定方向
    direction = TURN_FORWARD if angle >= 0 else TURN_REVERSE
    abs_angle = abs(angle)
    pulses = int(abs_angle * STEP_MODE / ANGLE_MODE)

    # 确保速度在0-127范围内
    speed = max(0, min(127, speed))

    tx_data = bytearray(8)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0xFD             # 功能码
    tx_data[2] = (direction << 7) | (speed & 0x7F)  # 方向+速度
    # 脉冲数(32位大端序)
    tx_data[3:7] = struct.pack('>I', pulses)
    tx_data[7] = get_check_sum(tx_data[:7])  # 校验和

    uart.write(tx_data)

def stop_uart(motor_id):
    """停止电机"""
    tx_data = bytearray(3)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0xF7             # 功能码
    tx_data[2] = get_check_sum(tx_data[:2])  # 校验和

    uart.write(tx_data)

def enable_uart(motor_id, status):
    """使能/禁用电机"""
    tx_data = bytearray(4)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0xF3             # 功能码
    tx_data[2] = 1 if status else 0  # 状态
    tx_data[3] = get_check_sum(tx_data[:3])  # 校验和

    uart.write(tx_data)

def save_speed_uart(motor_id):
    """保存当前速度"""
    tx_data = bytearray(4)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0xFF             # 功能码
    tx_data[2] = 0xC8             # 保存指令
    tx_data[3] = get_check_sum(tx_data[:3])  # 校验和

    uart.write(tx_data)

def clear_speed_uart(motor_id):
    """清除保存的速度"""
    tx_data = bytearray(4)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0xFF             # 功能码
    tx_data[2] = 0xCA             # 清除指令
    tx_data[3] = get_check_sum(tx_data[:3])  # 校验和

    uart.write(tx_data)

def read_encoder_uart(motor_id):
    """读取编码器角度（0-360°）"""
    tx_data = bytearray([0xE0 + motor_id, 0x30, 0x00])
    tx_data[2] = get_check_sum(tx_data[:2])

    uart.write(tx_data)

    rx_data = uart.read(8)
    if not rx_data or len(rx_data) < 8:
        return 0.0

    encoder_val = (rx_data[5] << 8) | rx_data[6]
    return encoder_val * 360.0 / 65536

def read_pulses_uart(motor_id):
    """读取脉冲计数值"""
    tx_data = bytearray([0xE0 + motor_id, 0x33, 0x00])
    tx_data[2] = get_check_sum(tx_data[:2])

    uart.write(tx_data)

    rx_data = uart.read(6)
    if not rx_data or len(rx_data) < 6:
        return 0

    # 解析32位有符号整数 (大端序)
    return int.from_bytes(rx_data[1:5], 'big', signed=True)

def read_position_uart(motor_id):
    """读取电机位置（角度）"""
    tx_data = bytearray([0xE0 + motor_id, 0x36, 0x00])
    tx_data[2] = get_check_sum(tx_data[:2])

    uart.write(tx_data)

    rx_data = uart.read(6)
    if not rx_data or len(rx_data) < 6:
        return 0.0

    position_val = int.from_bytes(rx_data[1:5], 'big', signed=True)
    return position_val * 360.0 / 65536

def read_error_uart(motor_id):
    """读取位置偏差角度"""
    tx_data = bytearray([0xE0 + motor_id, 0x39, 0x00])
    tx_data[2] = get_check_sum(tx_data[:2])

    uart.write(tx_data)

    rx_data = uart.read(4)
    if not rx_data or len(rx_data) < 4:
        return 0.0

    error_val = (rx_data[1] << 8) | rx_data[2]
    return error_val * 360.0 / 65536

def reset_uart(motor_id):
    """复位电机"""
    tx_data = bytearray(3)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0x3F             # 功能码
    tx_data[2] = get_check_sum(tx_data[:2])  # 校验和

    uart.write(tx_data)

def set_kp_uart(motor_id, kp):
    """设置比例增益Kp"""
    tx_data = bytearray(5)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0xA1             # 功能码
    tx_data[2] = (kp >> 8) & 0xFF  # 高字节
    tx_data[3] = kp & 0xFF         # 低字节
    tx_data[4] = get_check_sum(tx_data[:4])  # 校验和

    uart.write(tx_data)

def set_ki_uart(motor_id, ki):
    """设置积分增益Ki"""
    tx_data = bytearray(5)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0xA2             # 功能码
    tx_data[2] = (ki >> 8) & 0xFF  # 高字节
    tx_data[3] = ki & 0xFF         # 低字节
    tx_data[4] = get_check_sum(tx_data[:4])  # 校验和

    uart.write(tx_data)

def set_kd_uart(motor_id, kd):
    """设置微分增益Kd"""
    tx_data = bytearray(5)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0xA3             # 功能码
    tx_data[2] = (kd >> 8) & 0xFF  # 高字节
    tx_data[3] = kd & 0xFF         # 低字节
    tx_data[4] = get_check_sum(tx_data[:4])  # 校验和

    uart.write(tx_data)

def set_acc_uart(motor_id, acc):
    """设置加速度"""
    tx_data = bytearray(5)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0xA4             # 功能码
    tx_data[2] = (acc >> 8) & 0xFF  # 高字节
    tx_data[3] = acc & 0xFF         # 低字节
    tx_data[4] = get_check_sum(tx_data[:4])  # 校验和

    uart.write(tx_data)

def set_maxt_uart(motor_id, maxt):
    """设置最大转矩"""
    tx_data = bytearray(5)
    tx_data[0] = 0xE0 + motor_id  # 地址
    tx_data[1] = 0xA5             # 功能码
    tx_data[2] = (maxt >> 8) & 0xFF  # 高字节
    tx_data[3] = maxt & 0xFF         # 低字节
    tx_data[4] = get_check_sum(tx_data[:4])  # 校验和

    uart.write(tx_data)

