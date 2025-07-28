from machine import Pin
from machine import FPIOA
import time
from Stepmotor import Stepper

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
