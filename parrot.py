import subprocess
import os

from flask import Flask
from flask import render_template, request
app = Flask(__name__)

import atexit

from adafruit_motorkit import MotorKit

mk = MotorKit()

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

# SPEAKER_DEV = "bluealsa:HCI=hci0,DEV=90:C6:82:02:78:19,PROFILE=a2dp" # Stormtrooper
SPEAKER_DEV = "sysdefault"

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

@app.route('/bluetooth')
def bluetooth():
    bluetoothctl_out = subprocess.check_output('''sudo bluetoothctl <<EOF
info {}
quit
EOF
'''.format(SPEAKER_DEV), shell=True)
    return render_template('bluetooth.html', bluetoothctl_out=bluetoothctl_out)

@app.route('/wifi')
def wifi():
    iwconfig_out = subprocess.check_output(['iwconfig'])
    return render_template('wifi.html', iwconfig_out=iwconfig_out)

@app.route('/')
def index():
    local_ip = subprocess.check_output("ip addr show wlan0 | grep -Po 'inet \K[\d.]+'", shell=True)
    audio_files = [name.split('.')[0] for name in os.listdir('.') if name.endswith('.wav')] 
    return render_template('parrot.html', local_ip=local_ip, audio_files=audio_files)

@app.route('/start')
def start():
    motor = request.args.get('motor')
    if motor == 'beak':
        mk.motor3.throttle = 0.2
    if motor == 'wings_down':
        mk.motor2.throttle = -0.2
    if motor == 'wings_up':
        mk.motor2.throttle = 0.2
    if motor == 'head':
        mk.motor4.throttle = 0.2
    if motor == 'left_eye':
        GPIO.output(20, GPIO.HIGH)
    if motor == 'right_eye':
        GPIO.output(21, GPIO.HIGH)
    return 'OK'

@app.route('/stop')
def stop():
    motor = request.args.get('motor')
    if motor == 'beak':
        mk.motor3.throttle = None
    if motor in ['wings_up', 'wings_down']:
        mk.motor2.throttle = None
    if motor == 'head':
        mk.motor4.throttle = None
    if motor == 'left_eye':
        GPIO.output(20, GPIO.LOW)
    if motor == 'right_eye':
        GPIO.output(21, GPIO.LOW)
    return 'OK'

@app.route('/play')
def play():
    audio_file = request.args.get('audio') + '.wav'
    cmd = "aplay -D {} {}".format(SPEAKER_DEV, audio_file)
    subprocess.check_output(cmd, shell=True)
    return "OK"

