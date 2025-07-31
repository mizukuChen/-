import machine
import struct

mpu = JY61P(1)
mpu.uart

class JY61P:
    def __init__(self, uart_port, baudrate=115200):
        """
        初始化JY61P陀螺仪模块
        
        :param uart_port: UART端口号 (0, 1, 2等)
        :param baudrate: 串口波特率，默认为9600
        """
        self.uart = machine.UART(uart_port, baudrate=baudrate)
        self.rx_buffer = bytearray(11)  # 接收数据数组
        self.rx_state = 0                # 接收状态标志位
        self.rx_index = 0                # 接收数组索引
        
        # 角度数据
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0                   # 累积的Yaw角度
        self.yaw_tran = 0.0              # 暂态Yaw
        self.yaw_cur = 0.0               # 当前Yaw
        self.yaw_flag = 0                # Yaw处理标志
        self.new_data = False            # 新数据标志

    def process_byte(self, rx_data):
        """
        处理接收到的单个字节数据
        
        :param rx_data: 接收到的字节
        """
        # 状态0: 等待包头0x55
        if self.rx_state == 0:
            if rx_data == 0x55:  # 收到包头
                self.rx_buffer[0] = rx_data
                self.rx_state = 1
                self.rx_index = 1
            else:
                self.reset_state()
        
        # 状态1: 等待数据标识0x53
        elif self.rx_state == 1:
            if rx_data == 0x53:  # 角度输出标识
                self.rx_buffer[1] = rx_data
                self.rx_state = 2
                self.rx_index = 2
            else:
                self.reset_state()
        
        # 状态2: 接收数据
        elif self.rx_state == 2:
            self.rx_buffer[self.rx_index] = rx_data
            self.rx_index += 1
            
            # 接收完成 (11字节包)
            if self.rx_index == 11:
                # 计算校验和
                checksum = sum(self.rx_buffer[:10]) & 0xFF
                
                # 校验成功
                if checksum == self.rx_buffer[10]:
                    # 解析Yaw角度 (大端序)
                    yaw_raw = struct.unpack('>h', self.rx_buffer[6:8])[0]
                    self.yaw_cur = yaw_raw / 32768.0 * 180.0
                    
                    # 处理Yaw角度累积
                    if self.yaw_flag == 0:
                       # self.yaw = self.yaw_cur
                        self.yaw_flag = 1
                    elif self.yaw_flag == 1:
                        #self.yaw_tran = self.yaw_cur
                        
                        # 计算角度差并处理360°跳变
                        dyaw = self.yaw_cur - self.yaw_tran
                        self.yaw_tran = self.yaw_cur;
                        if dyaw > 180:
                            dyaw -= 360
                        elif dyaw < -180:
                            dyaw += 360
                        
                        self.yaw += dyaw
                    
                    self.new_data = True
                jytime =0;
                # 重置状态机
                self.reset_state()

    def reset_state(self):
        """重置接收状态"""
        self.rx_state = 0
        self.rx_index = 0

    def update(self):
        """从串口读取并处理所有可用数据"""
        while self.uart.any():
            byte = self.uart.read(1)
            if byte:
                self.process_byte(byte[0])

    def get_angles(self):
        """
        获取最新的角度数据
        
        :return: (roll, pitch, yaw) 元组
        :说明: 当前实现只处理Yaw，Roll和Pitch需要扩展解析
        """
        self.new_data = False
        return self.roll, self.pitch, self.yaw

    def has_new_data(self):
        """检查是否有新数据"""
        return self.new_data

    def calibrate(self, duration=10):
        """
        简单的校准过程
        :param duration: 校准持续时间(秒)
        """
        print("Starting calibration... Keep sensor still.")
        start = time.ticks_ms()
        yaw_samples = []
        
        while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
            self.update()
            if self.has_new_data():
                _, _, yaw = self.get_angles()
                yaw_samples.append(yaw)
            time.sleep_ms(10)
        
        if yaw_samples:
            avg_yaw = sum(yaw_samples) / len(yaw_samples)
            self.yaw -= avg_yaw
            print(f"Calibration complete. Offset: {avg_yaw:.2f}°")
        else:
            print("Calibration failed. No data received.")