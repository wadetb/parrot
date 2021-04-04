import asyncio
import atexit
import random
import threading
import time
from concurrent.futures import CancelledError

import hw


sm_thread = None
sm_task = None

ALL_BUTTONS = [hw.b1, hw.b2]


def any_button_pressed():
    for btn in ALL_BUTTONS:
        if btn.pressed():
            return btn
    return None


async def flash_button(btn, count):
    for _ in range(count):
        btn.led_dio.value = True
        await asyncio.sleep(0.06)
        btn.led_dio.value = False
        await asyncio.sleep(0.06)


async def target_flash_loop(btn):
    while True:
        await flash_button(btn, 12)
        await asyncio.sleep(1)


async def play_game(btn):
    round = 1

    while True:
        if round == 1:
            print('Hi! Looks like you want to play the game! Drop down and get ready.')
        else:
            print('Drop down and get ready for the next one.')

        await flash_button(btn, 48)
        await asyncio.sleep(5)

        print('Which one will I choose first?')
        for n in range(len(ALL_BUTTONS) * 3):
            await flash_button(ALL_BUTTONS[n % len(ALL_BUTTONS)], 8)
        
        n = random.randrange(len(ALL_BUTTONS))
        btn = ALL_BUTTONS[n]
        print('This one! Go get it!')

        flash_task = asyncio.create_task(target_flash_loop(btn))

        start_time = time.time()
        time_limit = 30
        win = False

        while True:
            if btn.pressed():
                win = True
                break
            if time.time() - start_time > time_limit:
                break
            await asyncio.sleep(0.1)

        flash_task.cancel()
        while btn.pressed():
            await asyncio.sleep(1)
        btn.led_dio.value = False

        if win:
            s = int(time.time() - start_time)
            print(f'Nice job, your time was {s} seconds.')
        else:
            print('Try again soon!')
            return
        
        round += 1


async def task_loop():
    while True:
        while True:
            await asyncio.sleep(0.1)
            btn = any_button_pressed()
            if btn is not None:
                break

        await play_game(btn)


async def main():
    global sm_task
    sm_task = asyncio.create_task(task_loop())
    await sm_task


def thread_entry():
    try:
        asyncio.run(main())
    except CancelledError:
        pass


def start():
    stop()

    global sm_thread
    sm_thread = threading.Thread(target=thread_entry, daemon=True)
    sm_thread.start()


def stop():
    global sm_task
    if sm_task is not None:
        sm_task.cancel()
        sm_task = None

    global sm_thread
    if sm_thread is not None:
        sm_thread.join()
        sm_thread = None


atexit.register(stop)
