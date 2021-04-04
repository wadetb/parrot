import atexit

import board
import digitalio
from adafruit_motorkit import MotorKit
from adafruit_debouncer import Debouncer

mk = MotorKit()


class LEDButton:
    def __init__(self, btn_pin, led_pin):
        self.dio = digitalio.DigitalInOut(btn_pin)
        self.dio.direction = digitalio.Direction.INPUT
        self.dio.pull = digitalio.Pull.UP

        self.led_dio = digitalio.DigitalInOut(led_pin)
        self.led_dio.direction = digitalio.Direction.OUTPUT

    def pressed(self):
        return not self.dio.value

class LED:
    def __init__(self, pin):
        self.dio = digitalio.DigitalInOut(pin)
        self.dio.direction = digitalio.Direction.OUTPUT


b1 = LEDButton(board.D13, board.D12)
b2 = LEDButton(board.D25, board.D24)
leye = LED(board.D20)
reye = LED(board.D21)

# SPEAKER_DEV = "bluealsa:HCI=hci0,DEV=90:C6:82:02:78:19,PROFILE=a2dp" # Stormtrooper
SPEAKER_DEV = "sysdefault"


def off():
    mk.motor1.throttle = None
    mk.motor2.throttle = None
    mk.motor3.throttle = None
    mk.motor4.throttle = None
    b1.led_dio.value = False
    b2.led_dio.value = False
    leye.dio.value = False
    reye.dio.value = False


atexit.register(off)
