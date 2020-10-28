#!/usr/bin/env python3
# test_read_am2302.py

import automationhat
import Adafruit_DHT as dht

DHT_TYPE=dht.AM2302
DHT_PIN=15

h,t = dht.read(DHT_TYPE, DHT_PIN)
print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(t,h))


#
# EOF
#
