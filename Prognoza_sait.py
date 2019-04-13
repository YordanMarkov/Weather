#!/usr/bin/env python3
import time
import bme280
import smbus2
import serial
import json
from flask import Flask, render_template

temp=0
pre=0
hum=0
pm10 = 0
pm2_5 = 0
color10 = 'yellow'
color2_5 = 'yellow'

address = 0x76
bus = smbus2.SMBus(1)
calibration_params = bme280.load_calibration_params(bus, address)

dev = serial.Serial('/dev/ttyUSB0', 9600)
if not dev.isOpen():
   dev.open()

def read_sensors():
    global dev, bus, address, calibration_params, temp, pre, hum, pm10 , pm2_5 , color10 , color2_5

    # Read BME280
    data = bme280.sample(bus, address, calibration_params)
    temp=round(data.temperature, 1)
    pre=int(data.pressure)
    hum=int(data.humidity)

    # Read PM
    dev.flushInput()
    msg = dev.read(10)
    assert msg[0] == ord(b'\xaa')
    assert msg[1] == ord(b'\xc0')
    assert msg[9] == ord(b'\xab')
    checksum = sum(v for v in msg[2:8]) % 256
    assert checksum == msg[8]
    pm2_5 = (msg[3] * 256 + msg[2]) / 10
    pm10 = (msg[5] * 256 + msg[4]) / 10

    color10 = 'yellow'
    color2_5 = 'yellow'
    if pm10 > 40:
      color10 = 'red'
    if pm2_5 > 30:
      color2_5 = 'red'


app = Flask(__name__)

@app.route('/')
def index():
    try:
      read_sensors()
    except Exception as ex:
      print(ex)
    return render_template('sait.html', temp=temp, hum=hum, pre=pre, pm10=pm10, pm2_5=pm2_5, color10=color10, color2_5=color2_5)

@app.route('/data')
def get_data():
    try:
      read_sensors()
      return app.response_class(
          response=json.dumps({
		'temp': temp,
		'hum': hum,
		'pre': pre,
		'pm10': pm10,
		'pm2_5': pm2_5,
		'color10': color10,
		'color2_5': color2_5
 	  }),
          status=200,
          mimetype='application/json'
      )
    except Exception as ex:
      return app.response_class(
          response=str(ex),
          status=500,
          mimetype='application/text'
      )

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
