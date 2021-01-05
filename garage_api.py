#!/usr/bin/env python3
# doorapi.py
# Flask API for garage doors with smart point-of-presence
# David Cook, 2020
# Child program of garage_main.py
# Provides the API services for the Rpi intelligent POP returned
# in JSON format.
#
# Returns records for the garage doors and PIR motion status. Here
# is a sample for returning both garage doors together.
#  [
#    {
#      "id": 1,
#      "closed": 0
#    },
#    {
#      "id": 2,
#      "closed": 0
#    }
#  ]
#
# Retrieving the status field of first element (0) via curl can be
# done as follows:
# $ curl https://xxxx/garage/door/status 2>/dev/null | jq .[0].status
#

# Import required modules
import flask
from flask import request, jsonify, make_response
import automationhat		# Pimironi AutomationHAT library
import Adafruit_DHT as dht      # Adafruit temperature sensor


# flask limiter so we can throttle api hits
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Define vars/constants
DEBUG=1				# 0=OFF/1=ON
DHT_TYPE=dht.AM2302             # DHT Sensor type
DHT_PIN=15                      # DHT sensor GPIO pin connection


# Configure defaults
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10000 per day", "1000 per hour"]
)

# Error Handler
@app.errorhandler(404)
def not_found(eror):
   return make_response(jsonify({'error': 'Not found'}), 404)


# Return garage door status
# Available externally via reverse proxy on jobs-01 that maps from
# https/443 to http/5000 locally.
#
# Retrieve door #1 status
# $ curl -s https://fw-01.advan.ca/garage/door/v1/1 | jq .closed
#
@app.route('/garage/door/v1/<int:id>', methods=['GET'])
@limiter.limit("")
def api_doorx(id):

   # All doors
   if id == 0:
      tmp = []
      door_closed=bool(automationhat.input.one.read())
      result = {'id': 1,'closed': door_closed}
      tmp.append(result)
      door_closed=bool(automationhat.input.two.read())
      result = {'id': 2,'closed': door_closed}
      tmp.append(result)
      return jsonify(tmp)
   # Door 1
   if id == 1:
      door_closed=bool(automationhat.input.one.read())
      result = {'id': id,'closed': door_closed}
      return jsonify(result)
   # Door 2
   if id == 2:
      door_closed=bool(automationhat.input.two.read())
      result = {'id': id,'closed': door_closed}
      return jsonify(result)
      

# Retrieve PIR #1 status
# $ curl -s https://fw-01.advan.ca/garage/pir/v1/1 | jq .triggered
#
@app.route('/garage/pir/v1/<int:id>', methods=['GET'])
@limiter.limit("")
def api_pirx(id):

   # Retreive the PIR status
   pir_status=not bool(automationhat.input.three.read())
   if id == 0:
      result = {'id': 1,'triggered': pir_status}
      return jsonify(result)

   if id == 1:
      result = {'id': 1,'triggered': pir_status}
      return jsonify(result)

# Retrieve the temperature/humidity
#
@app.route('/garage/temp/v1', methods=['GET'])
@limiter.limit("")
def api_temp():

   # Read the sensor
   h,t = dht.read(DHT_TYPE, DHT_PIN)
 
   # Round the result  
   hround=round(h,1)
   tround=round(t,1) 

   if DEBUG > 0:
      print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(t,h))

   result = {"location": "garage", "temp": tround, "humidity": hround} 
   return jsonify(result)


# Run the api app
app.run(host='0.0.0.0')

#
# EOF
#

