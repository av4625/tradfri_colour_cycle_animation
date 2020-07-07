#!/usr/bin/env python3

from collections import namedtuple
from itertools import cycle
import paho.mqtt.client as mqtt
from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import PytradfriError, RequestTimeout
from pytradfri.util import load_json, save_json
import threading
from threading import Thread
import time
import uuid

# Update with your mqtt details
mqtt_username = ''
mqtt_password = ''
mqtt_server = 'localhost'

client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)

# Location of your config file in the following format:
# {
#     'security_code': '',
#     'identity': '',
#     'key': ''
# }
config_file = ''

# IP address of your Tradfri gateway
gateway_ip = ''

colour = namedtuple('colour', ['x', 'y'])

# Set your prefered colours to cycle over
rainbow_colours = [
    colour(28790, 14385),
    colour(17145, 7969),
    colour(9900, 3976),
    colour(19659, 39108),
    colour(26623, 33577),
    colour(36075, 26071),
    colour(41528, 21404)
]

colours = [
    colour(28790, 14385),
    colour(17145, 7969),
    colour(9900, 3976),
    colour(17145, 7969),
    colour(28790, 14385),
    colour(41528, 21404)
]

# Update with the light name from the tradfri app
lamp_name = 'Dining Room Lamp'

threads = {}

def on_connect(client, user_data, flags, rc):
    print('Connected to MQTT broker with result code: ' + str(rc))
    client.subscribe('colour_cycle')
    client.subscribe('colour_cycle_slow')
    client.subscribe('rainbow_cycle')

def on_message(client, user_data, message):
    payload = message.payload.decode("UTF-8")

    if (payload == 'on'):
        start_colours(message.topic)
    else:
        stop_colours(message.topic)


def cycle_colours(api, light, colours, transition_time):
    try:
        api(light.light_control.set_xy_color(colours[-1].x, colours[-1].y))
        colour_wheel = cycle(colours)

        for colour in colour_wheel:
            t = threading.currentThread()
            if (getattr(t, 'stop', True)):
                break

            api(light.light_control.set_xy_color(
                colour.x, colour.y, transition_time=transition_time * 10))

            time.sleep(transition_time)

    except RequestTimeout:
        # If we get a slow request, possibly because someone else is controlling
        # the light we will start again
        cycle_colours(api, light, colours, transition_time)

def setup_api(gateway_ip, config_file):
    config = load_json(config_file)

    try:
        identity = config[gateway_ip]['identity']
        psk = config[gateway_ip]['key']
        api_factory = APIFactory(host=gateway_ip, psk_id=identity, psk=psk)
    except KeyError:
        identity = uuid.uuid4().hex
        api_factory = APIFactory(host=gateway_ip, psk_id=identity)

        psk = api_factory.generate_psk(config[gateway_ip].get('security_code'))
        print('Generated PSK: ', psk)

        config[gateway_ip] = {
            'security_code': config[gateway_ip].get('security_code'),
            'identity': identity,
            'key': psk
        }

        save_json(config_file, config)

    return api_factory.request

def get_dining_room_lamp(api):
    gateway = Gateway()
    devices_command = gateway.get_devices()
    devices_commands = api(devices_command)
    devices = api(devices_commands)

    lights = [dev for dev in devices if dev.has_light_control and dev.light_control.can_set_xy]

    for light in lights:
        if light.name == lamp_name:
            return light

def start_colours(cycle_mode):
    api = setup_api(gateway_ip, config_file)
    dining_room_lamp = get_dining_room_lamp(api)

    stop_all_colours()

    colours_to_show = colours

    if (cycle_mode == 'rainbow_cycle'):
        colours_to_show = rainbow_colours

    transition_time = 5

    if ('slow' in cycle_mode):
        transition_time = 30

    threads[cycle_mode] = Thread(
        target=cycle_colours, args=[
            api, dining_room_lamp, colours_to_show, transition_time])
    threads[cycle_mode].stop = False
    threads[cycle_mode].start()


def stop_colours(cycle_mode):
    if (cycle_mode in threads):
        print('stopping')
        threads[cycle_mode].stop = True
        threads[cycle_mode].join()
        del threads[cycle_mode]

def stop_all_colours():
    for cycle_mode in threads:
        threads[cycle_mode].stop = True
        threads[cycle_mode].join()
        del threads[cycle_mode]

if __name__ == "__main__":
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(mqtt_server, 1883)

    client.loop_forever()
    client.disconnect()
