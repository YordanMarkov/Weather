#!/usr/bin/env python3
import time
import bme280
import smbus2
import serial
from flask import Flask, render_template

def read_dust_sensor():
    dev = serial.Serial('/dev/ttyUSB0', 9600)
    if not dev.isOpen():
        dev.open()
    msg = dev.read(10)
    assert msg[0] == ord(b'\xaa')
    assert msg[1] == ord(b'\xc0')
    assert msg[9] == ord(b'\xab')
    pm2_5 = (msg[3] * 256 + msg[2]) / 10.0
    pm10 = (msg[5] * 256 + msg[4]) / 10.0
    checksum = sum(v for v in msg[2:8]) % 256
    assert checksum == msg[8]
    return {'PM10': pm10, 'PM2_5': pm2_5}

app = Flask(__name__)

@app.route('/')
def index():
    port = 1
    address = 0x76
    bus = smbus2.SMBus(port)
    calibration_params = bme280.load_calibration_params(bus, address)
    data = bme280.sample(bus, address, calibration_params)
    temp=int(data.temperature)
    pre=int(data.pressure)
    hum=int(data.humidity)
    data = read_dust_sensor()
    pm10 = data['PM10']
    pm2_5 = data['PM2_5']
    color10 = 'yellow'
    color2_5 = 'yellow'
    if pm10 > 40:
      color10 = 'red'
    if pm2_5 > 30:
      color2_5 = 'red'
    return render_template('sait.html', temp=temp, hum=hum, pre=pre, pm10=pm10, pm2_5=pm2_5, color10=color10, color2_5=color2_5)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

