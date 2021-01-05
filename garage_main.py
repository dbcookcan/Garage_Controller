#!/usr/bin/env python3
# garage_main.py
# Garage intelligent point of presence on RaspberryPi
# Provides local control over garage doors replacing the standard wall
# switches, plus acts as an intelligent point of presence adding
# - garage door state detection
# - PIR alarm sensor
# - temp/humidity for the garage
# - api's for polling state and push to integrated home controls.

# David Cook, 2020
# History
#######################################################################
# V0.1	Aug 25/20	dbc	Initial delivery
# V0.2  Oct 08/20	dbc	Add API subprocess
#				Refactor for /v1/[0|1|2] format 
#				Swap values to boolean and return
#				true|false
#				Add temp sensor lib
#                               Replace all tabs for Python3 compat
# V0.3	Oct 28/20	dbc	Fixed typos in docs
# V0.4	Jan 05/21	dbc	Add HA push webhook

# Import required modules
import time                     # time libraries
import datetime                 # date functions
import automationhat            # Pimironi AutomationHAT lib
import logging                  # OS logging functions
import os                       # OS shell functions
#import socket			# DNS library support
import Adafruit_DHT as dht      # Adafruit temperature sensor

# Define constants
DEBUG=1                         # 0=OFF/1=ON
API=1                           # 0=No API/1=API process running
SLEEPTIME=0.1                   # loop sleep time
DHT_TYPE=dht.AM2302             # DHT Sensor type
DHT_PIN=15                      # DHT sensor GPIO pin connection
MAX_LOOP=10000                  # Loop cycles to read temperature
HA_WEBHOOK=1			# 0=no/1=yes | Add HA Webhook support
HA_PIR_ALARM="http://192.168.0.58:8123/api/webhook/garage-pir-triggered"
HA_PIR_CLEAR="http://192.168.0.58:8123/api/webhook/garage-pir-cleared"

# Define variabltes
lastDoorOne=0                   # last status door 1
currDoorOne=0                   # current status door 1
lastDoorTwo=0                   # last status door 2
currDoorTwo=0                   # current status door 2
lastPIR=0                       # last status PIR sensor
currPIR=0                       # current status PIR sensor
loopcount=0                     # loop counter

# Setup logging
logging.basicConfig(filename='/var/log/garage.log',level=logging.DEBUG)
logging.info('garage_main.py: ******************************')
logging.info('garage_main.py: STARTING MAIN')


# Launch api subprocess
if API == 1:
    logging.info('garage_main.py: STARTING API subprocess')
    os.system("python3 /home/pi/Documents/Garage_Controller/garage_api.py &")


#
# MAIN

# Initial read of the temperature and humidity
h,t = dht.read(DHT_TYPE, DHT_PIN)
logging.info('garage_main.py: Init Temp/Humid sensor')
logging.info('garage_main.py: Temp %.1f *C | Humid %.1f', t,h)
#print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(t,h))


# Service Loop
while True:

    # DNS lookup - feed the cache
    #addr1 = socket.gethostbyname('google.ca')
    #os.system('ping -c 2 -W 1 google.ca')
     
    # Read the temperature & humidity every 10000 cycles so it doesn't
    # waste HW cycles.
    if loopcount > MAX_LOOP :
       h,t = dht.read(DHT_TYPE, DHT_PIN)
       logging.info('garage_main.py: Temp %.1f *C | Humid %.1f', t,h)
       loopcount=0
       

    # Check if Door 1 is Open/Closed 
    # Read value into variable so we don't have to keep going
    # back to the hardware to get the information.
    currDoorOne = automationhat.input.one.read()
    if currDoorOne == 0 : 			# Door Open
	
        # Check current against last status of the door
        # variable. Only write to the hardware registers if
        # the status has changed = saves cycles.
        if lastDoorOne != currDoorOne :
           automationhat.output.one.off()
           lastDoorOne = currDoorOne
           logging.info('garage_main.py: Door 1 OPEN')
           if DEBUG > 0 :
              print(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + " - Door 1 is OPEN")

    else :					# Door Closed
	# Check curreent against last status of the door
        # variable. Only write to the hardware registers if
        # the status has changed = saves cycles.
        if lastDoorOne != currDoorOne :
           automationhat.output.one.on()
           lastDoorOne = currDoorOne
           logging.info('garage_main.py: Door 1 CLOSED (OK)')
           if DEBUG > 0 :
              print(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + " - Door 1 is CLOSED (OK)")


    # Check if Door 2 is Open/Closed
    # Read value into variable so we don't have to keep going
    # back to the hardware to get the information.
    currDoorTwo = automationhat.input.two.read()
    if currDoorTwo == 0 :                       # Door Open

        # Check current against last status of the door
        # variable. Only write to the hardware registers if
        # the status has changed = saves cycles.
        if lastDoorTwo != currDoorTwo :
           automationhat.output.two.off()
           lastDoorTwo = currDoorTwo
           logging.info('garage_main.py: Door 2 OPEN')
           if DEBUG > 0 :
              print(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + " - Door 2 is OPEN")

    else :                                      # Door Closed
        # Check curreent against last status of the door
        # variable. Only write to the hardware registers if
        # the status has changed = saves cycles.
        if lastDoorTwo != currDoorTwo :
           automationhat.output.two.on()
           lastDoorTwo = currDoorTwo
           logging.info('garage_main.py: Door 2 CLOSED (OK)')
           if DEBUG > 0 :
              print(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + " - Door 2 is CLOSED (OK)")


    # Check if PIR is activated
    # Read value into variable so we don't have to keep going
    # back to the hardware to get the information.
    currPIR = automationhat.input.three.read()
    if currPIR == 0 :                           # PIR Alarmed

        # Check current against last status of the PIR
        # variable. Only write to the hardware registers if
        # the status has changed = saves cycles.
        if lastPIR != currPIR :
           automationhat.output.three.off()
           
           # Turn on relay #3
           automationhat.relay.three.on()
           
           # if HA, push webhook
           if HA_WEBHOOK == 1:
              os.system("curl -m 5 -XPOST "+HA_PIR_ALARM)
            
           # Save state
           lastPIR = currPIR
           logging.info('garage_main.py:   >>> PIR ALARM <<<')
           if DEBUG > 0 :
              print(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + " -   >>> PIR ALARM <<<")

    else :                                      # PIR Cleared
        # Check curreent against last status of the PIR
        # variable. Only write to the hardware registers if
        # the status has changed = saves cycles.
        if lastPIR != currPIR :
           automationhat.output.three.on()
           
	   # If HA, push webhook
           if HA_WEBHOOK == 1:
              os.system("curl -m 5 -XPOST "+HA_PIR_CLEAR)
           
           # Turn off relay #3
           automationhat.relay.three.off()
           
           # Save state
           lastPIR = currPIR
           logging.info('garage_main.py: PIR CLEAR (OK)')
           if DEBUG > 0 :
              print(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + " - PIR CLEAR (OK)")

    # Initiate wait/sleep so CPU won't run amuck
    time.sleep(SLEEPTIME)

    # Increment the loop counter
    loopcount += 1

#
# EOF
#
