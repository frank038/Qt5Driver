#!/usr/bin/env python3
# V. 0.5.1

from PyQt5.QtCore import (Qt,QMargins)
from PyQt5.QtWidgets import (QDesktopWidget,QLineEdit,QListWidget,QListWidgetItem,QFileDialog,QSizePolicy,qApp,QBoxLayout,QLabel,QPushButton,QApplication,QDialog,QGridLayout,QMessageBox,QTabWidget,QWidget,QComboBox,QCheckBox)
from PyQt5.QtGui import QIcon
import os
import sys
import pyudev
import subprocess
import Xlib.display, Xlib.X

WINW = 800
WINH = 100
DIALOGWIDTH = 600
PROGRAM_NAME = "Qt5Driver"


############################
class firstMessage(QWidget):
    def __init__(self, *args):
        super().__init__()
        title = args[0]
        message = args[1]
        self.setWindowTitle(title)
        # self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        box = QBoxLayout(QBoxLayout.TopToBottom)
        box.setContentsMargins(5,5,5,5)
        self.setLayout(box)
        label = QLabel(message)
        box.addWidget(label)
        button = QPushButton("Close")
        box.addWidget(button)
        button.clicked.connect(self.close)
        self.show()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

###################
WINM = "False"
if not os.path.exists("qt5prog.cfg"):
    try:
        with open("qt5prog.cfg", "w") as ifile:
            ifile.write("{};{};False".format(WINW, WINH))
    except:
        app = QApplication(sys.argv)
        fm = firstMessage("Error", "The file qt5prog.cfg cannot be created.")
        sys.exit(app.exec_())

if not os.access("qt5prog.cfg", os.R_OK):
    app = QApplication(sys.argv)
    fm = firstMessage("Error", "The file qt5prog.cfg cannot be read.")
    sys.exit(app.exec_())

try:
    with open("qt5prog.cfg", "r") as ifile:
        fcontent = ifile.readline()
    aw, ah, am = fcontent.split(";")
    WINW = aw
    WINH = ah
    WINM = am.strip()
except:
    app = QApplication(sys.argv)
    fm = firstMessage("Error", "The file qt5prog.cfg cannot be read.\nRebuilded.")
    try:
        with open("qt5prog.cfg", "w") as ifile:
            ifile.write("{};{};False".format(WINW, WINH))
    except:
        pass
    sys.exit(app.exec_())
#######################

##### usb devices
class usbDevices():
    DEVICE=""
    VENDOR=""
    DEVNAME=""
    SCRIPT=""
    ACTION=""
    NOTIFICATION=""

list_usb_devices = []
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

### windows
class winList():
    WINDOW=""
    TYPE=""
    NOTIFICATION=""
    SCRIPT=""
    ARGUMENT=""
    
win_list = []
tlines = []
if os.path.exists("Qt5Win.db"):
    with open("Qt5Win.db", "r") as ff:
        tlines = ff.readlines()

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

disp = Xlib.display.Display()
root = disp.screen().root
NET_CLIENT_LIST = disp.intern_atom('_NET_CLIENT_LIST')


class MainWin(QWidget):
    
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        #
        self.setWindowIcon(QIcon("icons/program.svg"))
        self.resize(int(WINW), int(WINH))
        self.setWindowTitle(PROGRAM_NAME)
        #
        ###### main box
        self.vbox = QBoxLayout(QBoxLayout.TopToBottom)
        self.vbox.setContentsMargins(QMargins(2,2,2,2))
        self.setLayout(self.vbox)
        ### button box
        self.obox1 = QBoxLayout(QBoxLayout.LeftToRight)
        self.obox1.setContentsMargins(QMargins(0,0,0,0))
        self.vbox.addLayout(self.obox1)
        #
        button_add = QPushButton("Add")
        button_add.clicked.connect(self.on_add)
        self.obox1.addWidget(button_add)
        #
        button_remove = QPushButton("remove")
        button_remove.clicked.connect(self.on_remove)
        self.obox1.addWidget(button_remove)
        #
        button_close = QPushButton("Close")
        button_close.clicked.connect(self.close)
        self.obox1.addWidget(button_close)
        #
        self.mtab = QTabWidget()
        self.mtab.setContentsMargins(QMargins(0,0,0,0))
        self.mtab.setMovable(False)
        self.mtab.setTabsClosable(False)
        self.vbox.addWidget(self.mtab)
        ### TAB USB DEVICES
        page1 = QWidget()
        self.mtab.addTab(page1, "Usb Devices")
        self.grid1 = QGridLayout()
        self.grid1.setColumnStretch(1,3)
        page1.setLayout(self.grid1)
        #
        self.usb_dev_list = QListWidget()
        self.usb_dev_list.itemClicked.connect(self.on_item_clicked)
        self.grid1.addWidget(self.usb_dev_list, 0, 0, 2, 5)
        #
        label_combo1 = QLabel("Action type:")
        self.grid1.addWidget(label_combo1, 2, 0, 1, 1, Qt.AlignLeft)
        self.combo1 = QComboBox()
        self.combo1.addItems(["inserted", "removed"])
        self.combo1.currentIndexChanged.connect(self.on_combo1)
        self.grid1.addWidget(self.combo1, 2, 1, 1, 1, Qt.AlignLeft)
        #
        label_vendor1 = QLabel("Vendor")
        self.grid1.addWidget(label_vendor1, 3, 0, 1, 1, Qt.AlignLeft)
        self.label_vendor = QLabel("")
        self.grid1.addWidget(self.label_vendor, 3, 1, 1, 1, Qt.AlignLeft)
        label_product1 = QLabel("Product")
        self.grid1.addWidget(label_product1, 4, 0, 1, 1, Qt.AlignLeft)
        self.label_product = QLabel("")
        self.grid1.addWidget(self.label_product, 4, 1, 1, 1, Qt.AlignLeft)
        # desktop notification
        self.ckb1 = QCheckBox("Desktop notification")
        self.ckb1.stateChanged.connect(self.on_ckb1)
        self.grid1.addWidget(self.ckb1, 5, 0, 1, 5, Qt.AlignLeft)
        # script
        button_script = QPushButton("Script")
        button_script.clicked.connect(self.on_get_file)
        self.grid1.addWidget(button_script, 6, 0, 1, 1)
        self.label_script = QLineEdit()
        self.label_script.setClearButtonEnabled(True)
        self.label_script.textChanged.connect(self.on_label_script)
        self.grid1.addWidget(self.label_script, 6, 1, 1, 5)
        # save
        button_save = QPushButton("Save")
        button_save.clicked.connect(self.on_save)
        self.grid1.addWidget(button_save, 7, 0, 1, 1, Qt.AlignLeft)
        # load the file 
        for ul in list_usb_devices:
            item = QListWidgetItem(ul.DEVICE)
            self.usb_dev_list.addItem(item)
            # vendor - product
            item.data1 = ul.VENDOR
            # devname
            item.data2 = ul.DEVNAME
            # script
            item.data3 = ul.SCRIPT
            # action type: 0 inserted - 1 removed
            item.data4 = int(ul.ACTION)
            # notification desktop
            item.data5 = int(ul.NOTIFICATION)
        ## TAB WINDOWS
        page3 = QWidget()
        self.mtab.addTab(page3, "Windows")
        self.grid3 = QGridLayout()
        self.grid3.setColumnStretch(1,3)
        page3.setLayout(self.grid3)
        #
        #
        self.window_list = QListWidget()
        self.window_list.itemClicked.connect(self.on_item_clicked_win)
        self.grid3.addWidget(self.window_list, 0, 0, 2, 5)
        # combo inserted/removed
        label_combo1 = QLabel("Action type:")
        self.grid3.addWidget(label_combo1, 2, 0, 1, 1, Qt.AlignLeft)
        self.combo3 = QComboBox()
        self.combo3.addItems(["started", "closed"])
        self.combo3.currentIndexChanged.connect(self.on_combo3)
        self.grid3.addWidget(self.combo3, 2, 1, 1, 1, Qt.AlignLeft)
        # window argument 
        label_arg = QLabel("Argument:")
        self.grid3.addWidget(label_arg, 3, 0, 1, 1, Qt.AlignLeft)
        self.line_edit3 = QLineEdit()
        self.line_edit3.setClearButtonEnabled(True)
        self.line_edit3.textChanged.connect(self.on_line_edit3)
        self.grid3.addWidget(self.line_edit3, 3, 1, 1, 4)
        # desktop notification
        self.ckb3 = QCheckBox("Desktop notification")
        self.ckb3.stateChanged.connect(self.on_ckb3)
        self.grid3.addWidget(self.ckb3, 5, 0, 1, 5, Qt.AlignLeft)
        # script
        button_script_win = QPushButton("Script")
        button_script_win.clicked.connect(self.on_get_file_win)
        self.grid3.addWidget(button_script_win, 6, 0, 1, 1)
        self.label_script_win = QLineEdit()
        self.label_script_win.setClearButtonEnabled(True)
        self.label_script_win.textChanged.connect(self.on_label_scrip_win)
        self.grid3.addWidget(self.label_script_win, 6, 1, 1, 4)
        #
        # save
        button_save_win = QPushButton("Save")
        button_save_win.clicked.connect(self.on_save_win)
        self.grid3.addWidget(button_save_win, 7, 0, 1, 1, Qt.AlignLeft)
        # load the file 
        for ul in win_list:
            item = QListWidgetItem(ul.WINDOW)
            self.window_list.addItem(item)
            # script - string
            item.data1 = ul.SCRIPT
            # type - int
            item.data2 = int(ul.TYPE)
            # notification - int
            item.data3 = int(ul.NOTIFICATION)
            # argument - string
            item.data4 = ul.ARGUMENT

    def closeEvent(self, event):
        self.on_close()
    
    def on_close(self):
        new_w = self.size().width()
        new_h = self.size().height()
        if new_w != int(WINW) or new_h != int(WINH):
            # WINW = width
            # WINH = height
            # WINM = maximized
            isMaximized = self.isMaximized()
            # close without update the file
            if isMaximized == True:
                qApp.quit()
                return
            #
            try:
                ifile = open("qt5prog.cfg", "w")
                ifile.write("{};{};False".format(new_w, new_h))
                ifile.close()
            except Exception as E:
                MyDialog("Error", str(E), self)
        qApp.quit()
    
############ WINDOWS ############
    # script
    def on_label_scrip_win(self, stext):
        curr_item = self.window_list.currentItem()
        if curr_item:
            curr_item.data1 = stext
    
    # type
    def on_combo3(self, idx):
        curr_item = self.window_list.currentItem()
        if curr_item:
            curr_item.data2 = idx
    
    # notification
    def on_ckb3(self, cstate):
        curr_item = self.window_list.currentItem()
        if curr_item:
            curr_item.data3 = cstate
        
    # argument
    def on_line_edit3(self, stext):
        curr_item = self.window_list.currentItem()
        if curr_item:
            curr_item.data4 = stext
    
    def on_add_window(self):
        ret = retDialogBox("Info", "Close the window and press Yes.\nThen, restart it and press 'Check'.", self)
        if ret.getValue() == 0:
            return
        ret = chooseDialogWin(self)
        if ret.getValue() == 0:
            return
        else:
            win_name = ret.getValue()
            item = QListWidgetItem(win_name)
            item.data1 = ""
            item.data2 = self.combo3.currentIndex()
            item.data3 = int(self.ckb3.isChecked())
            item.data4 = ""
            self.window_list.addItem(item)
            self.window_list.setCurrentItem(item)
    
    def on_remove_win(self):
        if self.window_list.currentItem() == None:
            return
        #
        ret = retDialogBox("Question", "Remove?", self)
        if ret.getValue() == 0:
            return
        #
        self.window_list.takeItem(self.window_list.currentRow())
        self.window_list.selectionModel().clear() 
        self.label_script_win.clear()
        self.line_edit3.clear()
        self.combo3.setCurrentIndex(0)
        self.ckb3.setChecked(False)
    
    def on_save_win(self):
        ret = retDialogBox("Question", "Save?", self)
        if ret.getValue() == 0:
            return
        #
        ff = open("Qt5Win.db", "w")
        for ii in range(self.window_list.count()):
            curr_item = self.window_list.item(ii)
            WINDOW = curr_item.text()
            SCRIPT = curr_item.data1
            TYPE = curr_item.data2
            NOTIFICATION = curr_item.data3
            ARGUMENT = curr_item.data4
            #
            text_line = "[WINDOW]"+"\n"+"WINDOW="+WINDOW+"\n"+"TYPE="+str(TYPE)+"\n"+"SCRIPT="+SCRIPT+"\n"+"NOTIFICATION="+str(NOTIFICATION)+"\n"+"ARGUMENT="+ARGUMENT+"\n"
            ff.write(text_line)
        ff.close()
        MyDialog("Info", "Saved.", self)
        
    def on_item_clicked_win(self, item):
        SCRIPT = item.data1
        TYPE = item.data2
        NOTIFICATION = item.data3
        ARGUMENT = item.data4
        #
        self.combo3.setCurrentIndex(int(TYPE))
        self.line_edit3.clear()
        self.line_edit3.setText(ARGUMENT)
        self.ckb3.setChecked(bool(NOTIFICATION))
        self.label_script_win.setText(SCRIPT)
    
    def on_get_file_win(self):
        if self.window_list.currentItem() == None:
            return
        fileName, fileType = QFileDialog.getOpenFileName(self,"Select the file", os.path.expanduser('~'),"All Files (*)")
        if fileName:
            self.label_script_win.setText(fileName)

############ WINDOWS END ############

############ USB DEVICES ############
    
    # script
    def on_label_script(self, stext):
        curr_item = self.usb_dev_list.currentItem()
        if curr_item:
            curr_item.data3 = stext
        
    # action
    def on_combo1(self, idx):
        curr_item = self.usb_dev_list.currentItem()
        if curr_item:
            curr_item.data4 = idx
        
    # notification
    def on_ckb1(self, cstate):
        curr_item = self.usb_dev_list.currentItem()
        if curr_item:
            curr_item.data5 = cstate
    
    def on_save(self):
        ret = retDialogBox("Question", "Save?", self)
        if ret.getValue() == 0:
            return
        #
        ff = open("Qt5Usb.db", "w")
        for ii in range(self.usb_dev_list.count()):
            curr_item = self.usb_dev_list.item(ii)
            device_name = curr_item.text()
            vendor_product = curr_item.data1
            devname = curr_item.data2
            dscript = curr_item.data3
            action = curr_item.data4
            desktop_not = curr_item.data5
            #
            text_line = "[USB DEVICE]"+"\n"+"DEVICE="+device_name+"\n"+"VENDOR="+vendor_product+"\n"+"DEVNAME="+devname+"\n"+"ACTION="+str(action)+"\n"+"SCRIPT="+dscript+"\n"+"NOTIFICATION="+str(desktop_not)+"\n"
            ff.write(text_line)
        ff.close()
        MyDialog("Info", "Saved.", self)
        
    def on_add(self, mtab):
        if self.mtab.currentIndex() == 0:
            self.on_add_usb_device()
        elif self.mtab.currentIndex() == 1:
            self.on_add_window()
    
    def on_add_usb_device(self):
        ret = retDialogBox("Info", "Detach the usb device and press Yes.\nThen, connect the usb device to a usb port.", self)
        if ret.getValue() == 0:
            return
        ret = chooseDialog(self)
        if ret.getValue() == 0:
            return
        else:
            data_get = ret.getValue()
            item = QListWidgetItem(data_get[0])
            self.usb_dev_list.addItem(item)
            # vendor - product
            item.data1 = data_get[1]+":"+data_get[2]
            # devname
            item.data2 = data_get[3]
            # script
            item.data3 = ""
            # action type: 0 inserted - 1 removed
            item.data4 = 0
            # notification desktop
            item.data5 = 0
            self.label_vendor.setText(data_get[1])
            self.label_product.setText(data_get[2])
            #
            self.usb_dev_list.setCurrentItem(item)
            
    def on_remove(self):
        if self.mtab.currentIndex() == 0:
            self.on_remove_usb()
        elif self.mtab.currentIndex() == 1:
            self.on_remove_win()
    
    def on_remove_usb(self):
        item = self.usb_dev_list.currentItem()
        if item == None:
            return
        #
        ret = retDialogBox("Question", "Remove?", self)
        if ret.getValue() == 0:
            return
        #
        self.usb_dev_list.takeItem(self.usb_dev_list.currentRow())
        self.usb_dev_list.selectionModel().clear() 
        self.label_vendor.setText("")
        self.label_product.setText("")
        self.label_script.clear()
        self.combo1.setCurrentIndex(0)
        self.ckb1.setChecked(False)
        
    def on_item_clicked(self, item):
        vendor, product = item.data1.split(":")
        dscript = item.data3
        action_type = item.data4
        desktop_not = item.data5
        self.combo1.setCurrentIndex(action_type)
        self.label_vendor.setText(vendor)
        self.label_product.setText(product)
        self.label_script.setText(dscript)
        self.ckb1.setChecked(bool(desktop_not))
    
    def on_get_file(self):
        if self.usb_dev_list.currentItem() == None:
            return
        fileName, fileType = QFileDialog.getOpenFileName(self,"Select the file", os.path.expanduser('~'),"All Files (*)")
        if fileName:
            self.label_script.setText(fileName)
        
############ USB DEVICES END ############


# simple dialog message
# type - message - parent
class MyDialog(QMessageBox):
    def __init__(self, *args):
        super(MyDialog, self).__init__(args[-1])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Information)
            self.setStandardButtons(QMessageBox.Ok)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Critical)
            self.setStandardButtons(QMessageBox.Ok)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Question)
            self.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        self.setWindowIcon(QIcon("icons/program.svg"))
        self.setWindowTitle(args[0])
        self.resize(DIALOGWIDTH,300)
        self.setText(args[1])
        retval = self.exec_()
    
    # def event(self, e):
        # result = QMessageBox.event(self, e)
        # #
        # self.setMinimumHeight(0)
        # self.setMaximumHeight(16777215)
        # self.setMinimumWidth(0)
        # self.setMaximumWidth(16777215)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # # 
        # return result

class chooseDialogWin(QDialog):
    def __init__(self, parent):
        super(chooseDialogWin, self).__init__(parent)
        self.setWindowIcon(QIcon("icons/program.svg"))
        self.setWindowTitle("Window...")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(DIALOGWIDTH, 300)
        #
        vbox = QBoxLayout(QBoxLayout.TopToBottom)
        vbox.setContentsMargins(5,5,5,5)
        self.setLayout(vbox)
        #
        self.win_list = QListWidget()
        vbox.addWidget(self.win_list)
        ### button box
        hbox = QBoxLayout(QBoxLayout.LeftToRight)
        vbox.addLayout(hbox)
        #
        button2 = QPushButton("Check")
        button2.clicked.connect(self.on_check)
        hbox.addWidget(button2)
        #
        button4 = QPushButton("Accept")
        button4.clicked.connect(self.on_accept)
        hbox.addWidget(button4)
        #
        button3 = QPushButton("Close")
        button3.clicked.connect(self.close)
        hbox.addWidget(button3)
        #
        self.Value = 0
        #
        self.win_before = []
        self.win_after = []
        self.pop_win_before()
        #
        self.exec_()
    
    def pop_win_before(self):
        window_list = root.get_full_property(NET_CLIENT_LIST, Xlib.X.AnyPropertyType).value
        self.win_before = window_list.tolist()
        
    def on_check(self):
        window_list = root.get_full_property(NET_CLIENT_LIST, Xlib.X.AnyPropertyType).value
        self.win_after = window_list.tolist()
        #
        diff_list = [i for i in self.win_after if i not in self.win_before]
        # 
        for w in diff_list:
            window = disp.create_resource_object('window', w)
            win_name_t = window.get_wm_class()
            # 
            if win_name_t is not None:
                if str(win_name_t[0]) != "Qt5Driver.py":
                    win_name = str(win_name_t[0])
                    self.win_list.addItem(win_name)
        #
        if self.win_list.count():
            self.win_list.setCurrentItem(self.win_list.item(0))
    
    def on_accept(self):
        if self.win_list.currentItem():
            data_get = self.win_list.currentItem().text()
            self.Value = data_get
        self.close()
    
    def getValue(self):
        return self.Value

# 
class chooseDialog(QDialog):
    def __init__(self, parent):
        super(chooseDialog, self).__init__(parent)
        self.setWindowIcon(QIcon("icons/program.svg"))
        self.setWindowTitle("Device...")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(DIALOGWIDTH, 300)
        #
        vbox = QBoxLayout(QBoxLayout.TopToBottom)
        vbox.setContentsMargins(5,5,5,5)
        self.setLayout(vbox)
        #
        self.usb_list = QListWidget()
        vbox.addWidget(self.usb_list)
        ### button box
        hbox = QBoxLayout(QBoxLayout.LeftToRight)
        vbox.addLayout(hbox)
        #
        button4 = QPushButton("Accept")
        button4.clicked.connect(self.on_accept)
        hbox.addWidget(button4)
        #
        button3 = QPushButton("Close")
        button3.clicked.connect(self.close)
        hbox.addWidget(button3)
        #
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb')
        self.observer = pyudev.MonitorObserver(monitor, self.udev_event)
        self.observer.start()
        #
        self.Value = 0
        #
        self.exec_()
    
    def udev_event(self, action, device):
        if action == "add":
            if device.get('DEVTYPE') == "usb_device":
                device_name = ""
                if device.get('ID_MODEL_FROM_DATABASE'):
                    device_name = device.get('ID_MODEL_FROM_DATABASE')
                else:
                    device_name = device.get('ID_MODEL_ID')
                self.usb_list.addItem(device_name+" - "+device.get('ID_VENDOR_ID')+":"+device.get('ID_MODEL_ID'))
                self.Value = [device_name,device.get('ID_VENDOR_ID'),device.get('ID_MODEL_ID'), device.get('DEVNAME')]
    
    def on_accept(self):
        self.close()
    
    def getValue(self):
        return self.Value
        

# dialog - return of the choise yes or no
class retDialogBox(QMessageBox):
    def __init__(self, *args):
        super(retDialogBox, self).__init__(args[-1])
        self.setWindowIcon(QIcon("icons/progam.png"))
        self.setWindowTitle(args[0])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Information)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Critical)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Question)
        self.resize(DIALOGWIDTH, 100)
        self.setText(args[1])
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        #
        self.Value = None
        retval = self.exec_()
        #
        if retval == QMessageBox.Yes:
            self.Value = 1
        elif retval == QMessageBox.Cancel:
            self.Value = 0
    
    def getValue(self):
        return self.Value
    
    # def event(self, e):
        # result = QMessageBox.event(self, e)
        # #
        # self.setMinimumHeight(0)
        # self.setMaximumHeight(16777215)
        # self.setMinimumWidth(0)
        # self.setMaximumWidth(16777215)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # #
        # textEdit = self.findChild(QTextEdit)
        # if textEdit != None :
            # textEdit.setMinimumHeight(0)
            # textEdit.setMaximumHeight(16777215)
            # textEdit.setMinimumWidth(0)
            # textEdit.setMaximumWidth(16777215)
            # textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # #
        # return result

###################

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWin()
    window.show()
    ret = app.exec_()
    sys.exit(ret)

####################
