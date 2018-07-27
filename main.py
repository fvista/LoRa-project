
import socket
import time
import binascii
import pycom
from network import LoRa
from CayenneLPP import CayenneLPP

from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from MPL3115A2 import MPL3115A2, ALTITUDE, PRESSURE

py = Pysense()
si = SI7006A20(py)
li = LIS2HH12(py)

# Disable heartbeat LED
pycom.heartbeat(False)

# Initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN)

# create an OTAA authentication parameters
app_eui = binascii.unhexlify('70B3D57ED000D3E6')
app_key = binascii.unhexlify('52FCF7AD40BE3F1437166E4ECD46183D')
dev_eui = binascii.unhexlify('70B3D54996BEF8B1')

print("AppEUI: %s" % (binascii.hexlify(app_eui)))

print("AppKey: %s" % (binascii.hexlify(app_key)))

# lora join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    pycom.rgbled(0x140000)
    time.sleep(2.5)
    pycom.rgbled(0x000000)
    time.sleep(1.0)
    print('Not yet joined...')

print('OTAA joined')
pycom.rgbled(0x001400)

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate: 
# DR | SF
# 5  | 7
# 4  | 8
# 3  | 9
# 2  | 10
# 1  | 11
# 0  | 12
s.setsockopt(socket.SOL_LORA, socket.SO_DR,5)


s.setblocking(True)
pycom.rgbled(0x000014)
lpp = CayenneLPP()

for n in range(1,601):

  lpp.add_accelerometer(1, li.acceleration()[0], li.acceleration()[1], li.acceleration()[2])
  lpp.add_gryrometer(1, li.roll(), li.pitch(), 0)



  lpp.add_relative_humidity(1, si.humidity())
  lpp.add_temperature(1, si.temperature())

  mpPress = MPL3115A2(py,mode=PRESSURE)


  lpp.add_barometric_pressure(1, mpPress.pressure()/100)

  mpAlt = MPL3115A2(py,mode=ALTITUDE)

  lpp.add_gps(1, 0, 0, mpAlt.altitude())

  print('Sending data (uplink)...')
  s.send(bytes(lpp.get_buffer()))
  s.setblocking(False)
  data = s.recv(64)
  print('Received data (downlink)', data)
  lpp.reset()
  pycom.rgbled(0x000000)
  print(n)
  time.sleep(0.5)
  pycom.rgbled(0x001400)
  time.sleep(2.5)
