# Parrot

This is an animatronic that sits on top of my kids' climbing wall and tells pirate jokes when they hit the buttons at the top. Originally conceived to be some kind of elaborate climbing whack a mole.

## Setup

1. Enable i2c via raspi-config.

2. Install packages:

```
sudo apt update
sudo apt upgrade -y
sudo apt install -y git vim python3-numpy python3-pip espeak sox
sudo pip3 install flask adafruit-blinka adafruit-circuitpython-motorkit adafruit-circuitpython-debouncer
sudo ln parrot.service /etc/systemd/system/
```
