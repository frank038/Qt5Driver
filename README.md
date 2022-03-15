# Qt5Driver

V. 0.5 - Testing

A program that makes things when a device has been plugged/unplugged or a window starts/closes.

Requires:
- python3
- pyqt5
- pyudev
- python3-xlib
- pyinotify
- notify-send (for notification; optional)

The application Qt5Driver.py is the graphical configuration program. The attach or detach of usb devices or the opening or closing of graphical applications can be notified, or a program or script can executed, or both. Qt5DriverDaemon.py is the daemon that makes such things. Killqt5driverdaemon.sh is just a script to kill/terminate the daemon. In the case of applications, an argument can also be specified optionally, such as a file name.

![My image](https://github.com/frank038/Qt5Driver/blob/main/image1.png)

![My image](https://github.com/frank038/Qt5Driver/blob/main/image2.png)
