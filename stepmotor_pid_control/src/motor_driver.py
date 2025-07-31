import machine
import struct

class Stepmotor:
    ANGLE_MODE = 1.8
    STEP_MODE = 16
    STEPS_PER_CIRCLE = int(360 / ANGLE_MODE * STEP_MODE)
    DEG_PER_STEP = 1.0 / ANGLE_MODE * STEP_MODE
    TURN_FORWARD = 1
    TURN_REVERSE = 0

    def __init__(self, uart, motor_id):
        self.uart = machine.UART(uart, baudrate=9600, timeout=50)
        self.motor_id = motor_id

    @staticmethod
    def get_check_sum(data):
        return sum(data) & 0xFF

    def speed_mode(self, direction, speed):
        speed = max(0, min(127, speed))
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0xF6
        tx_data[2] = (direction << 7) | (speed & 0x7F)
        tx_data[3] = self.get_check_sum(tx_data[:3])
        self.uart.write(tx_data)

    def position_mode(self, speed, angle):
        direction = self.TURN_FORWARD if angle >= 0 else self.TURN_REVERSE
        abs_angle = abs(angle)
        pulses = int(abs_angle * self.STEP_MODE / self.ANGLE_MODE)
        speed = max(0, min(127, speed))
        tx_data = bytearray(8)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0xFD
        tx_data[2] = (direction << 7) | (speed & 0x7F)
        tx_data[3:7] = struct.pack('>I', pulses)
        tx_data[7] = self.get_check_sum(tx_data[:7])
        self.uart.write(tx_data)

    def stop(self):
        tx_data = bytearray(3)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0xF7
        tx_data[2] = self.get_check_sum(tx_data[:2])
        self.uart.write(tx_data)

    def enable(self, status):
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0xF3
        tx_data[2] = 1 if status else 0
        tx_data[3] = self.get_check_sum(tx_data[:3])
        self.uart.write(tx_data)

    def save_speed(self):
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0xFF
        tx_data[2] = 0xC8
        tx_data[3] = self.get_check_sum(tx_data[:3])
        self.uart.write(tx_data)

    def clear_speed(self):
        tx_data = bytearray(4)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0xFF
        tx_data[2] = 0xCA
        tx_data[3] = self.get_check_sum(tx_data[:3])
        self.uart.write(tx_data)

    def read_encoder(self):
        tx_data = bytearray([0xE0 + self.motor_id, 0x30, 0x00])
        tx_data[2] = self.get_check_sum(tx_data[:2])
        self.uart.write(tx_data)
        rx_data = self.uart.read(8)
        if not rx_data or len(rx_data) < 8:
            return 0.0
        encoder_val = (rx_data[5] << 8) | rx_data[6]
        return encoder_val * 360.0 / 65536

    def read_pulses(self):
        tx_data = bytearray([0xE0 + self.motor_id, 0x33, 0x00])
        tx_data[2] = self.get_check_sum(tx_data[:2])
        self.uart.write(tx_data)
        rx_data = self.uart.read(6)
        if not rx_data or len(rx_data) < 6:
            return 0
        return int.from_bytes(rx_data[1:5], 'big', signed=True)

    def read_position(self):
        tx_data = bytearray([0xE0 + self.motor_id, 0x36, 0x00])
        tx_data[2] = self.get_check_sum(tx_data[:2])
        self.uart.write(tx_data)
        rx_data = self.uart.read(6)
        if not rx_data or len(rx_data) < 6:
            return 0.0
        position_val = int.from_bytes(rx_data[1:5], 'big', signed=True)
        return position_val * 360.0 / 65536

    def read_error(self):
        tx_data = bytearray([0xE0 + self.motor_id, 0x39, 0x00])
        tx_data[2] = self.get_check_sum(tx_data[:2])
        self.uart.write(tx_data)
        rx_data = self.uart.read(4)
        if not rx_data or len(rx_data) < 4:
            return 0.0
        error_val = (rx_data[1] << 8) | rx_data[2]
        return error_val * 360.0 / 65536

    def reset(self):
        tx_data = bytearray(3)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0x3F
        tx_data[2] = self.get_check_sum(tx_data[:2])
        self.uart.write(tx_data)

    def set_kp(self, kp):
        tx_data = bytearray(5)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0xA1
        tx_data[2] = (kp >> 8) & 0xFF
        tx_data[3] = kp & 0xFF
        tx_data[4] = self.get_check_sum(tx_data[:4])
        self.uart.write(tx_data)

    def set_ki(self, ki):
        tx_data = bytearray(5)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0xA2
        tx_data[2] = (ki >> 8) & 0xFF
        tx_data[3] = ki & 0xFF
        tx_data[4] = self.get_check_sum(tx_data[:4])
        self.uart.write(tx_data)

    def set_kd(self, kd):
        tx_data = bytearray(5)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0xA3
        tx_data[2] = (kd >> 8) & 0xFF
        tx_data[3] = kd & 0xFF
        tx_data[4] = self.get_check_sum(tx_data[:4])
        self.uart.write(tx_data)

    def set_acc(self, acc):
        tx_data = bytearray(5)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0xA4
        tx_data[2] = (acc >> 8) & 0xFF
        tx_data[3] = acc & 0xFF
        tx_data[4] = self.get_check_sum(tx_data[:4])
        self.uart.write(tx_data)

    def set_maxt(self, maxt):
        tx_data = bytearray(5)
        tx_data[0] = 0xE0 + self.motor_id
        tx_data[1] = 0xA5
        tx_data[2] = (maxt >> 8) & 0xFF
        tx_data[3] = maxt & 0xFF
        tx_data[4] = self.get_check_sum(tx_data[:4])
        self.uart.write(tx_data)