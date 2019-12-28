# home-assistant_config [![Build Status](https://travis-ci.org/tomhoover/home-assistant_config.svg?branch=master)](https://travis-ci.org/tomhoover/home-assistant_config)

## Misc configuration items
Create `/etc/udev/rules.d/99-usb-serial.rules`:
```
SUBSYSTEM=="tty", ATTRS{idVendor}=="0658", ATTRS{idProduct}=="0200", SYMLINK+="zwave"
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="e024", SYMLINK+="wyzesense"
```
