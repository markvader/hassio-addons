#!/usr/bin/env python3

import argparse
import signal
import sys
import time
import logging
import io, os, shutil
from datetime import datetime

mosquitto_address = "192.168.178.100"
mosquitto_port = "1883"
mosquitto_user = "mqtt_user"
mosquitto_password = "mqtt_password"

from rpi_rf import RFDevice

rfdevice = None
valid_codes = ["329041", "329044", "332113", "332116", "332881", "332884", "333073", "333076"]

# pylint: disable=unused-argument
def exithandler(signal, frame):
    rfdevice.cleanup()
    sys.exit(0)

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s', )

parser = argparse.ArgumentParser(description='Receives a decimal code via a 433/315MHz GPIO device')
parser.add_argument('-g', dest='gpio', type=int, default=27,
                    help="GPIO pin (Default: 27)")
args = parser.parse_args()

signal.signal(signal.SIGINT, exithandler)
rfdevice = RFDevice(args.gpio)
rfdevice.enable_rx()
timestamp = None
last_sent = datetime.now()
logging.info("Listening for codes on GPIO " + str(args.gpio))
while True:
    seconds_since_last_mqtt_message_sent = (datetime.now() - last_sent).total_seconds()
    if rfdevice.rx_code_timestamp != timestamp and str(rfdevice.rx_code) in valid_codes and seconds_since_last_mqtt_message_sent > 3:
        timestamp = rfdevice.rx_code_timestamp
        logging.info(str(rfdevice.rx_code) +
                     " [pulselength " + str(rfdevice.rx_pulselength) +
                     ", protocol " + str(rfdevice.rx_proto) + "]")
        os.system("mosquitto_pub -V mqttv311 -h " + mosquitto_address + " -p " + mosquitto_port + " -t 'sensors/rf/receiver' -u " + mosquitto_user + " -P " + mosquitto_password + " -m " + str(rfdevice.rx_code))
        last_sent = datetime.now()
    time.sleep(0.01)
rfdevice.cleanup() 

