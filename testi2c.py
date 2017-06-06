import smbus
import time

bus = smbus.SMBus(1)

#addr
action = 0x12

#actions
AVANCE=0
QDT_AVANT_GAUCHE=1
QDT_AVANT_DROITE=2
RECULE=3
QDT_ARRIERE_GAUCHE=4
QDT_ARRIERE_DROITE=5
RIEN=6

#forward
bus.write_byte(action,AVANCE)
time.sleep(1)

#backward
bus.write_byte(action,RECULE)
time.sleep(1)
print 'done.'
