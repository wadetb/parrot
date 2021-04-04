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


@app.route('/start')
def start():
    motor = request.args.get('motor')
    if motor == 'beak':
        hw.mk.motor3.throttle = 0.2
    if motor == 'wings_down':
        hw.mk.motor2.throttle = -0.2
    if motor == 'wings_up':
        hw.mk.motor2.throttle = 0.2
    if motor == 'head':
        hw.mk.motor4.throttle = -0.5
    if motor == 'left_eye':
        hw.leye.value = True
    if motor == 'right_eye':
        hw.reye.value = True
    return 'OK'


@app.route('/stop')
def stop():
    motor = request.args.get('motor')
    if motor == 'beak':
        hw.mk.motor3.throttle = None
    if motor in ['wings_up', 'wings_down']:
        hw.mk.motor2.throttle = None
    if motor == 'head':
        hw.mk.motor4.throttle = None
    if motor == 'left_eye':
        hw.leye.value = False
    if motor == 'right_eye':
        hw.reye.value = False
    return 'OK'


@app.route('/play')
def play():
    audio_file = request.args.get('audio') + '.wav'
    cmd = "aplay -D {} static/{}".format(hw.SPEAKER_DEV, audio_file)
    subprocess.check_output(cmd, shell=True)
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
