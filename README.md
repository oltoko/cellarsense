# cellarsense

Measure Temperature and Humidity and show it on a eInk Display by using:
* a [Raspberry Pi Zero W](https://web.archive.org/web/20200115212613/https://www.raspberrypi.org/products/raspberry-pi-zero-w/)
* a [Adafruit Sensirion SHT31-D](https://web.archive.org/web/20200115212748/https://www.adafruit.com/product/2857)
* a [Pimoroni Inky pHAT red](https://web.archive.org/web/20200115212955/https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-inky-phat)

# Setup

## Hardware

To get startet you should first [setup your Pi](https://web.archive.org/web/20200115215635/https://www.raspberrypi.org/documentation/setup/). Vanilla installation of Raspbian should be enough for the beginning.

After that connect your Sensor and the Display.

The SHT31-D is connected using [I2C](https://web.archive.org/web/20190517064722/https://pinout.xyz/pinout/i2c). I've used the Pins 3, 4, 5 and 6.

Connecting the [pHat](https://web.archive.org/web/20190606174347/https://pinout.xyz/pinout/inky_phat) is obviously very easy, but you need to consider that you need to connect your SHT31-D in parallel with the pHat. If you don't want to solder it somehow at the bottom of your Pi you maybe want to use a GPIO extender like [Pico HAT Hacker](https://web.archive.org/web/20200115214420/https://shop.pimoroni.de/products/pico-hat-hacker).

## Software

Setting up the Software should work by just executing the Ansible playbook.

Clone this Repository to your local machine. If not done before, you need to [setup Ansible](https://web.archive.org/web/20200115214629/https://docs.ansible.com/ansible/latest/installation_guide/index.html). I've used version 2.9.2.

After that, you need to setup the [inventory](https://web.archive.org/web/20200115213927/https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html). I've just added a [SSH config](https://web.archive.org/web/20200115215831/https://linux.die.net/man/5/ssh_config) with the name `cellarnode`.

Now you just need to go to the `ansible` directory and execute the following command:
```
ansible-playbook playbook.yml -i inventory
```
Could take some time 😴

After the next restart, everything should be running and your display should show the first value.

![Final result](https://archive.org/download/cellarsense/cellarsense.png)

Time to enjoy a good glas of wine 🍷
