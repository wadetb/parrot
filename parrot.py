import subprocess

from flask import Flask
from flask import render_template, request
app = Flask(__name__)

import atexit

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

mh = Adafruit_MotorHAT(addr=0x60)

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

def off():
    for m in [1, 2, 3, 4]:
        mh.getMotor(m).run(Adafruit_MotorHAT.RELEASE)
    GPIO.output(20, GPIO.LOW)
    GPIO.output(21, GPIO.LOW)
atexit.register(off)

@app.route('/reboot')
def reboot():
    subprocess.check_output('sudo shutdown -r now', shell=True)
    return "OK"

@app.route('/wifi')
def wifi():
    iwconfig_out = subprocess.check_output(['iwconfig'])
    return render_template('wifi.html', iwconfig_out=iwconfig_out)

@app.route('/')
def index():
    local_ip = subprocess.check_output("ip addr show wlan0 | grep -Po 'inet \K[\d.]+'", shell=True)
    return render_template('parrot.html', local_ip=local_ip)

@app.route('/start')
def start():
    motor = request.args.get('motor')
    if motor == 'beak':
        m = mh.getMotor(3)
        m.setSpeed(200)
        m.run(Adafruit_MotorHAT.BACKWARD)
    if motor == 'wings_down':
        m = mh.getMotor(2)
        m.setSpeed(200)
        m.run(Adafruit_MotorHAT.BACKWARD)
    if motor == 'wings_up':
        m = mh.getMotor(2)
        m.setSpeed(200)
        m.run(Adafruit_MotorHAT.FORWARD)
    if motor == 'head':
        m = mh.getMotor(4)
        m.setSpeed(200)
        m.run(Adafruit_MotorHAT.FORWARD)
    if motor == 'left_eye':
        GPIO.output(20, GPIO.HIGH)
    if motor == 'right_eye':
        GPIO.output(21, GPIO.HIGH)
    return 'OK'

@app.route('/stop')
def stop():
    motor = request.args.get('motor')
    if motor == 'beak':
        m = mh.getMotor(3)
        m.run(Adafruit_MotorHAT.RELEASE)
    if motor in ['wings_up', 'wings_down']:
        m = mh.getMotor(2)
        m.run(Adafruit_MotorHAT.RELEASE)
    if motor == 'head':
        m = mh.getMotor(4)
        m.run(Adafruit_MotorHAT.RELEASE)
    if motor == 'left_eye':
        GPIO.output(20, GPIO.LOW)
    if motor == 'right_eye':
        GPIO.output(21, GPIO.LOW)
    return 'OK'
