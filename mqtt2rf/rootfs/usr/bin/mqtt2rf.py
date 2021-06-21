#!/usr/bin/env python3
# https://pypi.org/project/paho-mqtt/
# https://github.com/milaq/rpi-rf/blob/master/scripts/rpi-rf_send
# https://github.com/home-assistant/core/blob/dev/homeassistant/components/rpi_rf/switch.py
import argparse
import signal
import sys
import time
import logging
import io, os, shutil
import paho.mqtt.client as mqtt
import json
from datetime import datetime
from rpi_rf import RFDevice

MQTT_KEEPALIVE_S = 120
rfdevice = None

# pylint: disable=unused-argument
def exithandler(signal, frame):
    rfdevice.cleanup()
    sys.exit(0)


levels = {
    "trace": logging.DEBUG,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "notice": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "fatal": logging.CRITICAL,
}

parser = argparse.ArgumentParser(description="Receives a decimal code via a 433/315MHz GPIO device")
parser.add_argument("--log-level", choices=list(levels.keys()), help="Provide logging level", default="info")
parser.add_argument("-g", dest="gpio", type=int, default=27, help="GPIO pin (Default: 27)")
parser.add_argument("--mqtt-host", required=True)
parser.add_argument("--mqtt-port", required=True)
parser.add_argument("--mqtt-user", required=True)
parser.add_argument("--mqtt-password", required=True)
parser.add_argument("--mqtt-test", default=None)
args = parser.parse_args()

logging.basicConfig(
    level=levels.get(args.log_level),
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)-15s] %(levelname)s %(module)s: %(message)s",
)

signal.signal(signal.SIGINT, exithandler)
rfdevice = RFDevice(args.gpio)
rfdevice.enable_tx()


def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected with result code {rc}")
    if args.mqtt_test:
        logging.info("Sending MQTT test messsage to 'test/topic'")
        client.publish("test/topic", "hello from mqtt2rf")
    logging.info("Subscribing to 'switches/rf'")
    client.subscribe("switches/rf/#")


def on_message(client, userdata, message):
    logging.debug(f"message: userdata '{userdata}' message payload '{str(message.payload)}' topic '{message.topic}'")
    try:
        data = json.loads(message.payload)
        code = data["code"]
        pulselength = data["pulselength"]
        protocol = data["protocol"]
        repeat = data["repeat"]
        logging.info(f"rf send '{code}' [pulselength {pulselength}, protocol {protocol}, repeat {repeat}]")
        rfdevice.tx_repeat = repeat
        rfdevice.tx_code(code, protocol, pulselength)
    except Exception as e:
        logging.error(f"exception: '{repr(e)}'")


def on_log(client, obj, level, buf):
    logging.debug(f"log: level {level} message '{str(buf)}' userdata '{str(obj)}'")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log
client.username_pw_set(args.mqtt_user, args.mqtt_password)
client.connect(args.mqtt_host, int(args.mqtt_port), MQTT_KEEPALIVE_S)
client.loop_forever(retry_first_connection=True)
