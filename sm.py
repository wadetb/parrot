import asyncio
import math
import os
import random
import subprocess
import threading
import time
from concurrent.futures import CancelledError
import wave

import numpy as np

import hw


sm_thread = None
sm_loop = asyncio.new_event_loop()

spawn = asyncio.create_task

ALL_BUTTONS = [hw.b1, hw.b2]

oob_queue = []


def any_button_pressed():
    for btn in ALL_BUTTONS:
        if btn.pressed():
            return btn
    return None


async def run(args):
    print('RUN', args)
    p = subprocess.Popen(
        args,
        # stdout=subprocess.DEVNULL,
        # stderr=subprocess.DEVNULL
    )
    while p.poll() is None:
        await asyncio.sleep(0.1)


def sample_wave(path):
    with wave.open(path, 'r') as w:
        print(w.getparams())
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        n = w.getnframes()
        f = int(w.getframerate() / 10)
        signal = np.frombuffer(w.readframes(n), dtype=np.int16)

    r = np.array([np.average(np.absolute(signal[i*f:(i+1)*f]))
                  for i in range(n // f)])
    r = r / np.max(r)
    return r


async def flap_wings():
    while True:
        await asyncio.sleep(0.5 + random.random() * 1)
        t = 0.25 + random.random() * 0.25
        hw.wings.throttle = 0.5
        await asyncio.sleep(t)
        hw.wings.throttle = -0.3
        await asyncio.sleep(t * 0.25)
        hw.wings.throttle = None


async def animate_speech(path):
    frames = sample_wave(path)
    print('FRAMES', frames)

    audio_task = spawn(run(['/usr/bin/aplay', path]))

    try:
        wings_task = spawn(flap_wings())
        for f in frames:
            hw.head.throttle = -0.6 if f > 0.05 else None
            hw.beak.throttle = math.pow(f, 0.9) - 0.3
            await asyncio.sleep(0.1)
    finally:
        wings_task.cancel()
        hw.wings.throttle = None
        hw.head.throttle = None
        hw.beak.throttle = None

    await audio_task


async def say(text):
    print('SAY', text)
    await run([
        '/usr/bin/espeak',
        '-v', 'en', '-s', '150', '-p', '125', '-g', '3',
        '-w', 'speech.wav',
        text])
    await animate_speech('speech.wav')


async def pause(secs):
    n = 0
    while n < secs:
        if len(oob_queue):
            cmd, args = oob_queue.pop()
            if cmd == 'say':
                await say(args[0])
            if cmd == 'say_file':
                await animate_speech(args[0])
        await asyncio.sleep(0.1)
        n += 0.1

async def flash_button(btn, count):
    print('FLASH', 10)
    audio_task = spawn(run([
        '/usr/bin/play', '-n',
        'synth', '0.05',
        'sin', str(btn.audio[0]),
        'sin', str(btn.audio[1]),
        'delay', '0.05',
        'repeat', str(count)]))

    for _ in range(count):
        btn.led_dio.value = True
        await asyncio.sleep(0.05)
        btn.led_dio.value = False
        await asyncio.sleep(0.05)

    await audio_task


async def target_flash_loop(btn):
    while True:
        await flash_button(btn, 12)
        await pause(1)


async def play_game(btn):
    round = 1

    while True:
        await flash_button(btn, 48)

        if round == 1:
            await say('Hi! Looks like you want to play the game! Drop down and get ready.')
        else:
            await say('Drop down and get ready for the next one.')

        await say('Which one will I choose first?')
        for n in range(len(ALL_BUTTONS) * 3):
            await flash_button(ALL_BUTTONS[n % len(ALL_BUTTONS)], 8)

        n = random.randrange(len(ALL_BUTTONS))
        btn = ALL_BUTTONS[n]
        await say('This one! Go get it!')

        flash_task = spawn(target_flash_loop(btn))

        start_time = time.time()
        time_limit = 30
        win = False

        while True:
            if btn.pressed():
                win = True
                break
            if time.time() - start_time > time_limit:
                break
            await pause(0.1)

        flash_task.cancel()

        while btn.pressed():
            await pause(0.1)
        btn.led_dio.value = False

        if win:
            s = int(time.time() - start_time)
            await say(f'Nice job, your time was {s} seconds.')
        else:
            break

        round += 1

    await say('Try again!')


async def play_joke():
    path = random.choice([
        'static/8_pirates.wav',
        'static/80th_bday.wav',
        'static/addictive.wav',
        'static/boxing.wav',
        'static/just_waved.wav',
    ])
    await animate_speech(path)


async def task_loop():
    await say('Parrot Operating System Online')

    while True:
        while True:
            btn = any_button_pressed()
            if btn is not None:
                break
            await pause(0.1)

        await flash_button(btn, 32)
        await play_joke()

        # await play_game(btn)


def thread_entry():
    try:
        sm_loop = asyncio.new_event_loop()
        # w = asyncio.FastChildWatcher()
        # w.attach_loop(sm_loop)
        sm_loop.run_until_complete(task_loop())
    except CancelledError:
        pass


def start():
    stop()

    global sm_thread
    sm_thread = threading.Thread(target=thread_entry, daemon=True)
    sm_thread.start()


def stop():
    global sm_loop
    if sm_loop is not None:
        sm_loop.stop()
        sm_loop = None

    global sm_thread
    if sm_thread is not None:
        sm_thread.join()
        sm_thread = None
