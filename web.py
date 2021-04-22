import os
import subprocess

import sm
import hw

from flask import Flask
from flask import render_template, request
app = Flask(__name__)


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
'''.format(hw.SPEAKER_DEV), shell=True).decode()
    return render_template('bluetooth.html', bluetoothctl_out=bluetoothctl_out)


@app.route('/wifi')
def wifi():
    iwconfig_out = subprocess.check_output(['iwconfig']).decode()
    return render_template('wifi.html', iwconfig_out=iwconfig_out)


@app.route('/')
def index():
    local_ip = subprocess.check_output(
        "ip addr show wlan0 | grep -Po 'inet \K[\d.]+'", shell=True).decode()
    audio_files = [name.split('.')[0]
                   for name in os.listdir('static') if name.endswith('.wav')]
    return render_template('parrot.html', local_ip=local_ip, audio_files=audio_files)


@app.route('/button')
def button():
    b = request.args.get('b')
    s = request.args.get('s')
    if b == 'b1':
        hw.b1.web_pressed = (s == 'down')
    if b == 'b2':
        hw.b2.web_pressed = (s == 'down')
    return "OK"


@app.route('/motor')
def motor():
    m = request.args.get('m')
    s = request.args.get('s')
    if s == 'on':
        if m == 'beak':
            hw.mk.motor3.throttle = 0.5
        if m == 'wings_down':
            hw.mk.motor2.throttle = -0.2
        if m == 'wings_up':
            hw.mk.motor2.throttle = 1
        if m == 'head':
            hw.mk.motor4.throttle = -0.5
        if m == 'left_eye':
            hw.leye.value = True
        if m == 'right_eye':
            hw.reye.value = True
    else:
        if m == 'beak':
            hw.mk.motor3.throttle = None
        if m in ['wings_up', 'wings_down']:
            hw.mk.motor2.throttle = None
        if m == 'head':
            hw.mk.motor4.throttle = None
        if m == 'left_eye':
            hw.leye.value = False
        if m == 'right_eye':
            hw.reye.value = False
    return 'OK'


@app.route('/say_file')
def say_file():
    audio_file = 'static/' + request.args.get('file') + '.wav'
    sm.oob_queue.append(('say_file', [audio_file]))
    return "OK"


@app.route('/start_sm')
def start_sm():
    sm.start()
    return "OK"


@app.route('/stop_sm')
def stop_sm():
    sm.stop()
    return "OK"


def serve():
    app.run(debug=True, host='0.0.0.0', port=5000)
