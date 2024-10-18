import asyncio
import signal
from contextlib import suppress
import RPi.GPIO as GPIO
import time

loop = asyncio.get_event_loop()
LED_PIN = 26
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN, GPIO.OUT)
time.sleep(5)
print("LED off")
GPIO.output(LED_PIN, GPIO.LOW)

import pulsectl_asyncio

async def listen(pulse: pulsectl_asyncio.PulseAsync, source_name: str):
    ledIsOn = False
    async for level in pulse.subscribe_peak_sample(source_name, rate=5):
        if level>0.4 and ledIsOn==False:
            #print("LED on")
            GPIO.output(LED_PIN, GPIO.HIGH)
            ledIsOn = True
        
        if level<0.39 and ledIsOn==True:
            GPIO.output(LED_PIN, GPIO.LOW)
            ledIsOn = False

async def main():
    async with pulsectl_asyncio.PulseAsync('peak-listener') as pulse:
        # Get name of monitor_source of default sink
        server_info = await pulse.server_info()
        default_sink_info = await pulse.get_sink_by_name(server_info.default_sink_name)
        source_name = default_sink_info.monitor_source_name
        print('LED controller listening to', source_name)

        # Start listening/monitoring task
        listen_task = loop.create_task(listen(pulse, source_name))

        # register signal handlers to cancel listener when program is asked to terminate
        # Alternatively, the PulseAudio event subscription can be ended by breaking/returning from the `async for` loop
        for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
            loop.add_signal_handler(sig, listen_task.cancel)

        with suppress(asyncio.CancelledError):
            await listen_task
            print()


def vumeter():
    # Run event loop until main_task finishes
    tasks = asyncio.gather(main())
    try:
        loop.run_until_complete(tasks)
    except KeyboardInterrupt as e:
        print("Keyboard interrupt in VU meter loop")
        tasks.cancel()
        loop.run_forever()
        tasks.exception()
    finally:
        print("Close VU meter loop")
        loop.close()
