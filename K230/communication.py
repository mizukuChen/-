import struct
from machine import UART
from machine import FPIOA
from time import sleep_ms

fpioa = FPIOA()
# UART1代码
fpioa.set_function(3,FPIOA.UART1_TXD)
fpioa.set_function(4,FPIOA.UART1_RXD)

uart=UART(UART.UART1,115200) #设置串口号1和波特率

while 1:
    read_text = uart.read(15)
    if(read_text) == b"begin\n":
        uart.write('Hello 01Studio!')#发送一条数据

        # 使用struct.pack将short整数（有符号2字节）打包为二进制数据，使用本地字节序（'@'）
        packed_data = struct.pack('@h', 254+14)

        # 创建一个100字节的缓冲区，并将打包后的数据复制到开头
        send_buf = bytearray(2)
        send_buf[0:len(packed_data)] = packed_data
        print(send_buf)

        sleep_ms(2)

        uart.write(send_buf[0:2])

        # 从缓冲区前2字节解包出short整数（有符号2字节），使用本地字节序

        receive = struct.unpack('@h', send_buf[0:2])[0]

        print(receive)
