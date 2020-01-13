# cellarsense

Measure Temperature and Humidity and show it on a eInk Display by using:
* a [Raspberry Pi Zero](https://shop.pimoroni.com/products/raspberry-pi-zero-wh-with-pre-soldered-header)
* a [Adafruit Sensirion SHT31-D](https://shop.pimoroni.com/products/adafruit-sensiron-sht31-d-temperature-humidity-sensor-breakout)
* a [Pimoroni Inky pHAT](https://shop.pimoroni.com/products/inky-phat?variant=12549254217811)

## Setup

Everything, besides connection the Hardware 😉, should work by just executing the Ansible playbook. Just go to the `ansible` directory and execute the following command:
```
ansible-playbook playbook.yml -i inventory
```
Could take some time 😴
