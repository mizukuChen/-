from machine import Pin
from machine import FPIOA
import time
from MKS32C_uart import Stepmotor

motor = Stepmotor(1, 0)
motor.speed_mode(0 , 1)
while True:
    motor.speed_mode(1, 1)
