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

import os
import argparse
import logging
import sched
import signal
import time
import sys
from PIL import Image, ImageDraw, ImageFont
from inky import InkyPHAT
from influxdb import InfluxDBClient

# Configure logging
logging.basicConfig(level=logging.INFO ,format="%(asctime)-15s %(levelname)-8s - %(message)s")

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--colour', '-c', type=str, required=True, choices=["red", "black", "yellow"], help="ePaper display colour")
args = parser.parse_args()

colour = args.colour

logging.info("Connect to InfluxDB")
influx = InfluxDBClient()
influx.switch_database("cellarsense")
logging.info("Connect to InfluxDB - Done")

def readLastValue():

    # lastMonthResult = influx.query("select * from sht31d where time > now() - 31d")
    # print(lastMonth)
    lastDataResult = influx.query("select * from sht31d order by time desc limit 1")

    lastData = {"temperature": 0.0, "humidity": 0.0}

    for point in lastDataResult.get_points():
        lastData = point
    
    return lastData

def readAvgFromDays(days):

    query = "select * from sht31d where time > now() - {:d}d".format(days)
    result = influx.query(query)

    tempSum = 0
    humSum = 0
    count = 0

    for point in result.get_points():
        tempSum += point["temperature"]
        humSum += point["humidity"]
        count += 1

    avgTemp = tempSum / count if count != 0 else 0.0
    avgHum = humSum / count if count != 0 else 0.0

    avg = {"temperature": avgTemp, "humidity": avgHum}
    
    return avg

def refreshDisplay(intervall, priority, scheduler):

    logging.info("Refresh Display - start")

    lastValue = readLastValue()
    avgMonth = readAvgFromDays(31)
    avgYear = readAvgFromDays(365)

    inkyDisplay = InkyPHAT(colour)
    inkyDisplay.set_border(inkyDisplay.BLACK)

    # Load our background image
    img = Image.open("/var/local/cellarsense/cellarsense-background.png")
    draw = ImageDraw.Draw(img)

    mainHeaderFont = ImageFont.truetype("FreeMonoBold.ttf", 20)
    mainFont = ImageFont.truetype("FreeMono.ttf", 20)
    medianFont = ImageFont.truetype("FreeMono.ttf", 15)

    lastValuePrint = "{:4.1f}°C {:4.1f}%".format(lastValue["temperature"], lastValue["humidity"])
    avgMonthPrint = "øm {:4.1f}°C {:4.1f}%".format(avgMonth["temperature"], avgMonth["humidity"])
    avgYearPrint = "øa {:4.1f}°C {:4.1f}%".format(avgYear["temperature"], avgYear["humidity"])

    logging.debug("Refresh Display - %s", lastValuePrint)
    logging.debug("Refresh Display - %s", avgMonthPrint)
    logging.debug("Refresh Display - %s", avgYearPrint)

    draw.text((5, 5), "CellarSense", fill=inkyDisplay.BLACK, font=mainHeaderFont)
    draw.text((20, 35), lastValuePrint, fill=inkyDisplay.BLACK, font=mainFont)
    draw.text((10, 70), avgMonthPrint, fill=inkyDisplay.BLACK, font=medianFont)
    draw.text((10, 85), avgYearPrint, fill=inkyDisplay.BLACK, font=medianFont)

    inkyDisplay.set_image(img)
    inkyDisplay.show()

    logging.info("Refresh Display - done")

    # reschedule
    scheduler.enter(intervall, priority, refreshDisplay,
                    (intervall, priority, scheduler))

def shutdown(signum, frame):

    logging.warn("Shutdown!")
    influx.close()
    logging.warn("Shutdown: disconnect influx")
    sys.exit(0)

# Gracefully shutdown on signal
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

# Initialise scheduler
s = sched.scheduler(time.time, time.sleep)

# refreshDisplay
refreshDisplay(3600, 1, s)

# Run scheduler
logging.info("Start scheduler")
s.run()
