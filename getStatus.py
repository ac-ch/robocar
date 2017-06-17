import smbus
import time
import struct

bus = smbus.SMBus(1)

alimentation=bus.read_byte(0x0c)
accumulateur=bus.read_byte(0x0e)
sortie=bus.read_byte(0x0d)

bus.close()

print("ALIMENTATION:",alimentation)
print("ACCUMULATEUR:",accumulateur)
print("SORTIE:",sortie)
