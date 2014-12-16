delcom904x
==========
delcom904x is a python class to control the [Delcom Products 904x series multi-color
visual signal indicators](http://www.delcomproducts.com/products_USBLMP.asp). These are
USB HID devices that are easily programmable on most platforms.

It has been tested with the [904005-SB](http://www.delcomproducts.com/productdetails.asp?productnum=904005-SB)
but should work with any of the other models without any issues.

Requirements
============

[cython-hidapi](https://github.com/trezor/cython-hidapi) - Cross platform library to control USB HID devices.

[hidapi](https://github.com/signal11/hidapi) - Python wrapper for the hidapi

Installation
============

1. Install the delcom904x module

        $ [sudo] python setup.py install

2. Plug in your Delcom USBLMP
3. Test it out!

        $ ./control_delcom904x.py --green --red --flash --cycle


Example Usage
=============

```python
import delcom904x
light = delcom904x.DelcomMultiColorIndicator()
light.set_color(delcom904x.red, flashing = true)
```