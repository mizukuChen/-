import struct
from machine import UART
from machine import FPIOA
from time import sleep_ms

fpioa = FPIOA()
# UART1代码
fpioa.set_function(3,FPIOA.UART1_TXD)
fpioa.set_function(4,FPIOA.UART1_RXD)

uart=UART(UART.UART1,115200) #设置串口号1和波特率

