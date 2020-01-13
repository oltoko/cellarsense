#!/usr/bin/env python3

#    Copyright 2019 Oliver Koch
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import time
import board
import busio
import adafruit_sht31d
import socket
from datetime import datetime
from datetime import timezone
import sched
import signal
import sys
import logging
import time
from influxdb import InfluxDBClient

# Configure logging
logging.basicConfig(level=logging.INFO ,format="%(asctime)-15s %(levelname)-8s - %(message)s")

# Establish connection to influxDB
logging.info("Connect to InfluxDB")
influx = InfluxDBClient()
influx.create_database("cellarsense")
influx.switch_database("cellarsense")
logging.info("Connect to InfluxDB - Done")

# Create library object using our Bus I2C port
logging.info("Initialise SHT31D")
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)
logging.info("Initialise SHT31D - Done")

def measure(intervall, priority, scheduler, sensor):

    sensor.serial_number

    measurement = [{
        "measurement": "sht31d",
        "tags": {
            "host": socket.gethostname(),
            "serial": sensor.serial_number
        },
        "time": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        "fields": {
            "humidity": sensor.relative_humidity,
            "temperature": sensor.temperature
        }
    }]

    influx.write_points(measurement)
    logging.debug(measurement)

    # reschedule measurement
    scheduler.enter(intervall, priority, measure,
                    (intervall, priority, scheduler, sensor))


def heater(intervall, priority, scheduler, sensor):

    sensor.heater = True
    logging.info("Enabled heater")
    time.sleep(1)
    sensor.heater = False
    logging.info("Disabled heater")
    time.sleep(5)

    # reschedule heater
    scheduler.enter(intervall, priority, heater,
                    (intervall, priority, scheduler, sensor))

def shutdown(signum, frame):

    logging.warn("Shutdown!")
    sensor.heater = False
    logging.warn("Shutdown: disabled heater")
    influx.close()
    logging.warn("Shutdown: disconnect influx")
    sys.exit(0)

# Gracefully shutdown on signal
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

# Initialise scheduler
s = sched.scheduler(time.time, time.sleep)

# Execute heating and measurement
heater(1801, 1, s, sensor)
measure(1800, 10, s, sensor)

# Run scheduler
logging.info("Start scheduler")
s.run()
