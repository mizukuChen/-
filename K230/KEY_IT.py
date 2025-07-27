# Untitled - By: 86151 - Sun Jul 27 2025

from machine import Pin
from machine import FPIOA

fpioa = FPIOA()

fpioa.set_function(52,FPIOA.GPIO52)
fpioa.set_function(35,FPIOA.GPIO35)

led = Pin(52,Pin.OUT,pull=Pin.PULL_UP)
key = Pin(35,Pin.IN,pull=Pin.PULL_NONE)

key.value(1)
led.value(1)

flag = 0

def irq_hander(value):
    global flag
    print("value:",value)
    flag = not flag
    led.value(0)

key.irq(irq_hander,Pin.IRQ_FALLING)

while True:
    pass




















