#!/usr/bin/env python3
# V. 0.5
#####################
# whether to monitor the usb devices
USE_USB_DEVICES = 1
# whether to monitor the window manager
USE_XLIB = 1
#####################

if USE_USB_DEVICES:
    import pyudev
import signal
import sys
import os, shutil
import subprocess
import threading
import pyinotify



NOTIFYSEND = "notify-send"

######################################
##### usb devices
class usbDevices():
    DEVICE=""
    VENDOR=""
    DEVNAME=""
    SCRIPT=""
    ACTION=""
    NOTIFICATION=""

list_usb_devices = []
real_usb_dev_path = os.path.realpath("Qt5Usb.db")
def pop_usb_dev():
    tlines = []
    if os.path.exists("Qt5Usb.db"):
        with open("Qt5Usb.db", "r") as ff:
            tlines = ff.readlines()
    usb_dev = None
    for tline in tlines:
        if tline == "[USB DEVICE]\n":
            usb_dev = usbDevices()
        elif tline[0:7] == "DEVICE=":
            usb_dev.DEVICE=tline[7:].rstrip("\n")
        elif tline[0:7] == "VENDOR=":
            usb_dev.VENDOR=tline[7:].rstrip("\n")
        elif tline[0:8] == "DEVNAME=":
            usb_dev.DEVNAME=tline[8:].rstrip("\n")
        elif tline[0:7] == "SCRIPT=":
            usb_dev.SCRIPT=tline[7:].rstrip("\n")
        elif tline[0:7] == "ACTION=":
            usb_dev.ACTION=tline[7:].rstrip("\n")
        elif tline[0:13] == "NOTIFICATION=":
            usb_dev.NOTIFICATION=tline[13:].rstrip("\n")
            list_usb_devices.append(usb_dev)
            usb_dev = None
pop_usb_dev()

### windows
class winList():
    WINDOW=""
    TYPE=""
    NOTIFICATION=""
    SCRIPT=""
    ARGUMENT=""
    
win_list = []
real_win_path = os.path.realpath("Qt5Win.db")
def pop_win():
    tlines = []
    if os.path.exists("Qt5Win.db"):
        with open("Qt5Win.db", "r") as ff:
            tlines = ff.readlines()
    # 
    win_dev = None
    for tline in tlines:
        if tline == "[WINDOW]\n":
            win_dev = winList()
        elif tline[0:7] == "WINDOW=":
            win_dev.WINDOW=tline[7:].rstrip("\n")
        elif tline[0:5] == "TYPE=":
            win_dev.TYPE=tline[5:].rstrip("\n")
        elif tline[0:13] == "NOTIFICATION=":
            win_dev.NOTIFICATION=tline[13:].rstrip("\n")
        elif tline[0:7] == "SCRIPT=":
            win_dev.SCRIPT=tline[7:].rstrip("\n")
        elif tline[0:9] == "ARGUMENT=":
            win_dev.ARGUMENT=tline[9:].rstrip("\n")
            win_list.append(win_dev)
            win_dev = None
pop_win()

################################

signal.signal(signal.SIGINT, signal.SIG_DFL)

####################

if USE_XLIB:
    from Xlib.display import Display
    from Xlib import X, Xatom, Xutil, error, threaded
    display = Display()

class cThread(threading.Thread):
    def __init__(self, win_list, display):
        super(cThread, self).__init__()
        self.win_list = win_list
        self.display = display
        self.root = self.display.screen().root
        self.root.change_attributes(event_mask=X.PropertyChangeMask)
        #
        self.window_list_init = []
        xlist = self.root.get_full_property(self.display.intern_atom('_NET_CLIENT_LIST'), Xatom.WINDOW)
        if xlist:
            self.window_list_init = xlist.value.tolist()
        # window id
        self.window_list_added = []
        # window id - name
        self.window_list_added_2 = []
        
    def op(self, ul, win, action):
        if int(ul.NOTIFICATION) > 0:
            if shutil.which("notify-send"):
                iicon_type = "icons/xwindow.svg"
                icon_path = os.path.join(os.getcwd(), iicon_type)
                # 
                command = ["notify-send", "-i", icon_path, "-t", "3000", "-u", "normal", win, action]
                try:
                    subprocess.Popen(command)
                except:
                    pass
        if ul.SCRIPT:
            command = [ul.SCRIPT]
            try:
                subprocess.Popen(command, shell=True)
            except:
                pass
    
    def net_list(self):
        window_list = []
        xlist = self.root.get_full_property(self.display.intern_atom('_NET_CLIENT_LIST'), Xatom.WINDOW)
        if xlist:
            window_list = xlist.value.tolist()
            #
            window_added = [x for x in window_list if x not in self.window_list_init if x not in self.window_list_added]
            # 
            for ii in window_added:
                try:
                    window = self.display.create_resource_object('window', ii)
                    prop = window.get_full_property(self.display.intern_atom('_NET_WM_WINDOW_TYPE'), X.AnyPropertyType)
                except:
                    prop = None
                if prop:
                    if self.display.intern_atom('_NET_WM_WINDOW_TYPE_DOCK') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DESKTOP') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DIALOG') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_UTILITY') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_TOOLBAR') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_MENU') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_SPLASH') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DND') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_NOTIFICATION') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_DROPDOWN_MENU') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_COMBO') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_POPUP_MENU') in prop.value.tolist():
                        continue
                    elif self.display.intern_atom('_NET_WM_WINDOW_TYPE_NORMAL') in prop.value.tolist():
                        # 
                        win_name_t = None
                        try:
                            win_name_t = window.get_wm_class()
                        except:
                            win_name_t = None
                        win_exec = "Unknown"
                        if win_name_t is not None:
                            win_exec = str(win_name_t[0])
                        #
                        if win_exec:
                            if ii not in self.window_list_added:
                                self.window_list_added.append(ii)
                                self.window_list_added_2.append([ii, win_exec])
                                # 
                                cmd = "ps -e -o command | grep {} | grep -v grep".format(win_exec)
                                parg_temp = subprocess.check_output(cmd, shell=True)
                                parg = parg_temp.decode()
                                parg_list_temp = parg.split(win_exec)
                                del parg_list_temp[0]
                                parg_list = " ".join(parg_list_temp).lstrip(" ").rstrip("\n")
                                # find a program started with the previous argument
                                for ul in self.win_list:
                                    if ul.WINDOW == win_exec:
                                        if int(ul.TYPE) == 0:
                                            if ul.ARGUMENT == parg_list or ul.ARGUMENT == os.path.basename(parg_list):
                                                self.op(ul, ul.WINDOW, "Started: {}".format(ul.ARGUMENT))
                                                return
                                #
                                # find the window to notify
                                for ul in self.win_list:
                                    if ul.WINDOW == win_exec:
                                        if int(ul.TYPE) == 0:
                                            if not ul.ARGUMENT:
                                                self.op(ul, ul.WINDOW, "Started")
                                                return
            #
            window_removed = [x for x in self.window_list_added if x not in window_list]
            for ii in window_removed:
                if ii in self.window_list_added[:]:
                    self.window_list_added.remove(ii)
                    for el in self.window_list_added_2[:]:
                        if el[0] == ii:
                            self.window_list_added_2.remove(el)
                            win_name = el[1]
                            #
                            for ul in self.win_list:
                                if int(ul.TYPE) == 1:
                                    win_exec = ul.WINDOW
                                    if win_name == win_exec:
                                        self.op(ul, win_exec, "Closed")
                                        return
                
    def run(self):
        while True:
            xevent = self.display.next_event()
            if (xevent.type == X.PropertyNotify):
                if xevent.atom == self.display.intern_atom('_NET_CLIENT_LIST'):
                    self.net_list()
            if thread_stop:
                break
        if thread_stop:
            return


if USE_XLIB:
    threadc = cThread(win_list, display)
    threadc.start()
    thread_stop = False

###########################

# Watch Manager
wm = pyinotify.WatchManager()
# watched events
flags = pyinotify.IN_MODIFY

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self):
        pass
    
    def process_IN_MODIFY(self, event):
        if event.pathname == real_usb_dev_path:
            global list_usb_devices
            list_usb_devices = []
            pop_usb_dev()
        if event.pathname == real_win_path:
            global win_list
            win_list = []
            pop_win()
            #
            global thread_stop
            thread_stop = True
            global threadc
            threadc.join()
            threadc = cThread(win_list, display)
            threadc.start()
            thread_stop = False

handler = EventHandler()
notifier = pyinotify.ThreadedNotifier(wm, handler)
wdd = wm.add_watch(".", flags, rec=True)
notifier.start()

################################

if USE_USB_DEVICES:
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')
    monitor.start()

    for device in iter(monitor.poll, None):
        if device.action == "add":
            if 'DEVTYPE' in device and device.get('DEVTYPE') == "usb_device":
                vendor = device.get('ID_VENDOR_ID')
                product = device.get('ID_MODEL_ID')
                #
                hw_model = ""
                for ul in list_usb_devices:
                    if int(ul.ACTION) == 0:
                        if ul.VENDOR == "{}:{}".format(vendor, product):
                            hw_model = ul.DEVICE
                            #
                            if int(ul.NOTIFICATION) > 0:
                                if shutil.which("notify-send"):
                                    iicon_type = "icons/hardware.jpg"
                                    icon_path = os.path.join(os.getcwd(), iicon_type)
                                    # 
                                    command = ["notify-send", "-i", icon_path, "-t", "3000", "-u", "normal", hw_model, "Inserted"]
                                    try:
                                        subprocess.Popen(command)
                                    except:
                                        pass
                            if ul.SCRIPT:
                                command = [ul.SCRIPT]
                                try:
                                    subprocess.Popen(command, shell=True)
                                except:
                                    pass
        #
        elif device.action == "remove":
            if 'DEVTYPE' in device and device.get('DEVTYPE') == "usb_device":
                dvendor, dproduct, _ = device.get('PRODUCT').split("/")
                hw_model = ""
                for ul in list_usb_devices:
                    if int(ul.ACTION) == 1:
                        uvendor, uproduct = ul.VENDOR.split(":")
                        if dvendor in uvendor and dproduct in uproduct:
                            hw_model = ul.DEVICE
                            #
                            if int(ul.NOTIFICATION) > 0:
                                if shutil.which("notify-send"):
                                    iicon_type = "icons/hardware.jpg"
                                    icon_path = os.path.join(os.getcwd(), iicon_type)
                                    # 
                                    command = ["notify-send", "-i", icon_path, "-t", "3000", "-u", "normal", hw_model, "Removed"]
                                    try:
                                        subprocess.Popen(command)
                                    except:
                                        pass
                            if ul.SCRIPT:
                                command = [ul.SCRIPT]
                                try:
                                    subprocess.Popen(command, shell=True)
                                except:
                                    pass
