# Tradfri Colour Cycle Animation
This provides a way for you to have a colour cycle animation with RGB Tradfri
bulbs without having to use Philips Hue apps/hubs.

I use a Wemos D1 Mini that acts as a smart switch on Alexa. You can set up to
ten switches with one Wemos. I have one for fast colours, slow colours and
rainbow colours. When the smart switch has been turned on I send a `MQTT`
request from the Wemos. The Raspberry Pi is subscribing to these events,
when it gets an 'on' request for the specific cycle mode it will turn the colour
cycle on. When it gets an 'off' it will turn the cycle off.

This seems like a round about way of doing things as all could be done with
either a Wemos or A Raspberry Pi but the `CoAP` requests aren't as easy to do with
`Arduino` as it is with `pytradfri` and there is a handy library for Arduino to
simulate a smart switch on Alexa. I also already had a MQTT subscriber setup on
a Raspberry Pi.

## Prerequisites
* Have a Wemos D1 Mini (ESP8266) or similar
* Have a Raspberry Pi or something that is running a `MQTT` (mosquito)
server/subscriber
* Have Alexa (Works without alexa if you want to just run it from Linux)
* Have `python3` on your Raspberry Pi with `pytradfri` and `mqtt` packages installed
* Have `MQTT` running on your Raspberry Pi. [Sample Instructions](https://appcodelabs.com/introduction-to-iot-build-an-mqtt-server-using-raspberry-pi)
* Have `Arduino` installed
* Install `PubSubClient` for `Arduino`
* Install the [smart switch simulator](https://github.com/kakopappa/arduino-esp8266-alexa-multiple-wemo-switch) for `Arduino`.
I have forked this library and restructured it so that it can be used as a
library within `Arduino`. You will need my forked verison to make the example
code work. [Forked Version](https://github.com/av4625/arduino-esp8266-alexa-multiple-wemo-switch)

## Get it running
1. Start the `MQTT` subscriber, manually or by a service
2. Build the `ino` file and put it on your wemos and plug it in
3. Open the Alexa app and go to "Devices"
4. Add a device
5. Select "Other"
6. The devices will show, set them up by adding them to groups etc
7. Turn the animations on and off!

## Setting it up to run as a service
```bash
sudo cp colour_cycle.service /etc/systemd/system/colour_cycle.service
sudo systemctl enable colour_cycle.service
sudo systemctl start colour_cycle.service
```

## Gotchas
* The lamp must be on and at the brightness you want the colour cycle to be at
* You must turn off one cycle before starting the other (limitation in the smart
switch emulator code)
* You must turn off the cycle to be able to turn of the lamp (limitation with
way Ikea implemented the transition time)
* Reds, pinks, purples, blues and oranges works best. The rainbow colours aren't
great as the Ikea bulbs don't show a nice saturated green and it goes white

## TODO
- [ ] Work with more than one light
- [ ] Find a better why of stopping threads in python
- [ ] Make it turn on the light and start the animation if the lamp is off
- [ ] Let the user change brightness and turn off the lamp while the animation
is on
