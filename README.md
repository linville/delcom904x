delcom904x
==========
delcom904x is a python class and command-line script to control the [Delcom Products 904x
series multi-color visual signal indicators](http://www.delcomproducts.com/products_USBLMP.asp).
These are USB HID devices that are easily controllable from most platforms.

It has been tested with the [904005-SB](http://www.delcomproducts.com/productdetails.asp?productnum=904005-SB)
but should work with any of the other models without any issues. The yellow in the green,
red and *yellow* indicators is wired the same as blue. There also doesn't appear to be a
method of detecting if the attached indicator supports blue or yellow, so blue and yellow
commands are synonyms.


Installation
------------

        $ pip install delcom904x
        $ control-delcom904x --green --red --flash --cycle


`control-delcom904x` usage
-----------------------------

        -h, --help        show this help message and exit
        --list            List all USB devices.
        --info            Returns info on the device.
        --red             Enable the red light.
        --green           Enable the green light.
        --blue            Enable the blue light.
        --yellow          Enable the yellow light (if equipped; synonym for blue).
        --flash           Turns on flashing.
        --cycle [100]     Turns on cycling.
        --intensity [80]  Sets brightness: 0-100.
        --buzzer          Buzzes three times.
        --reset           Resets the device.


Python Code Examples
-------------------


```python
import delcom904x

light = delcom904x.DelcomMultiColorIndicator()
light.set_color(delcom904x.red, flashing=True)
light.close()
```

```python
import delcom904x

with delcom904x.DelcomMultiColorIndicator() as light:
    light.info()
    color = delcom904x.green
    light.set_color(color, flashing=True)
    light.set_intensity(80, color)
```


udev Notes
----------

On Linux machines, the default udev rulesets may set the permissions on the device to only
be accessible to the root user. Add the following rule to `/etc/udev/rules.d/` and
re-plugin the indicator to allow all users to access the device (optionally, consider
changing `MODE="0666"` to `GROUP="dialout"` to allow only the dialout group access).

        SUBSYSTEMS=="usb", ATTRS{idVendor}=="0fc5", ATTRS{idProduct}=="b080", MODE="0666"

