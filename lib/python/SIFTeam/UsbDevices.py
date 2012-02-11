from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists
from Tools.LoadPixmap import LoadPixmap
from Components.Button import Button

from Extra.SAPCL import SAPCL
from Extra.ExtraActionBox import ExtraActionBox
from Extra.ExtraMessageBox import ExtraMessageBox

from SoftwareManager.Stack import SMStack, smstack

from select import POLLIN, POLLPRI
import os
import re
import string
import socket
import pickle

# 3277 147 - terratec cinergy t
class UsbDevicesCache:
	def __init__(self):
		self.confdir = eEnv.resolve("${datadir}/enigma2/usbcache/")
		if not os.path.exists(self.confdir):
			os.mkdir(self.confdir)
		
	def load(self, idVendor, idProduct, nocache = False):
		filename = "%s/%d:%d.cache" % (self.confdir, idVendor, idProduct)
		ret = {}
		if fileExists(filename) and not nocache:
			cachefile = open(filename, 'rb')
			ret = pickle.load(cachefile)
			cachefile.close()
			ret["cached"] = True
		else:
			api = SAPCL()
			ret = api.getUsbDevice(idVendor, idProduct)
			if len(ret["devices"]) > 0:
				ret["devices"][0]["status"] = 0
			cachefile = open(filename, 'wb')
			pickle.dump(ret, cachefile)
			cachefile.close()
			ret["cached"] = False
			
		return ret
		
	# status: 0 -> not processed, 1 -> choose to ask to install next time
	# 2 -> never ask for installation again, 3 -> installed
	def setStatus(self, idVendor, idProduct, status):
		filename = "%s/%d:%d.cache" % (self.confdir, idVendor, idProduct)
		if not fileExists(filename):
			# ?!?! no cache?
			return
			
		cachefile = open(filename, 'rb')
		data = pickle.load(cachefile)
		cachefile.close()
		
		data["devices"][0]["status"] = status
		
		cachefile = open(filename, 'wb')
		pickle.dump(data, cachefile)
		cachefile.close()
		
class UsbDevice:
	def __init__(self, idVendor, idProduct, description = ""):
		self.idVendor = idVendor
		self.idProduct = idProduct
		self.description = description
		self.data = None
		usbcache = UsbDevicesCache()
		device = usbcache.load(idVendor, idProduct)
		if len(device["devices"]) == 0 and device["cached"]:
			# maybe we are lucky and there's an update on the repo :)
			device = usbcache.load(idVendor, idProduct, True)
			
		if len(device["devices"]) == 0:
			# unknow device.. nothing to do
			return
			
		self.data = device["devices"][0]		# more than one device? if this happen we can only take the first and hope
		
	def getDescription(self):
		if self.description != "":
			return self.description
			
		if self.data is None:
			return ""
			
		return self.data["descProduct"]
		
	def getPackage(self):
		if self.data is None:
			return ""
			
		return self.data["package"]
		
	def setStatus(self, status):
		usbcache = UsbDevicesCache()
		usbcache.setStatus(self.idVendor, self.idProduct, status)
		
	def needAutoInstall(self):
		if self.data is None:
			return False
			
		if len(self.data["package"]) == 0:
			# no package??
			return False
			
		if self.data["status"] > 1:
			return False
			
		if fileExists("/usr/lib/opkg/info/%s.control" % self.data["package"]):
			# already installed
			return False
			
		return True
		
class UsbDeviceAutoInstall:
	def __init__(self, session, device):
		self.session = session
		self.device = device
		self.callback = None
		
	def installCb(self, callback):
		self.callback = callback
		
	def msgboxCb(self, result):
		if result == 0:
			self.device.setStatus(3)	# mark as installed
			if not fileExists("/usr/lib/opkg/info/v4l-dvb-firmware.control"):
				smstack.add(SMStack.INSTALL, "v4l-dvb-firmware")
			smstack.add(SMStack.INSTALL_WITH_REBOOT, self.device.getPackage())
			
			# if necessary open usbdevices view
			found = False
			for dialog in self.session.dialog_stack:
				if isinstance(dialog, UsbDevices):
					found = True
					break
			if not found:
				self.session.open(UsbDevices)
		elif result == 1:
			self.device.setStatus(1)	# mark as "ask again"
		elif result == 2:
			self.device.setStatus(2)	# mark as "never ask again"
		
		if self.callback:
			self.callback(self)
		
	def install(self):
		if not self.device.needAutoInstall():
			return
			
		self.session.openWithCallback(
			self.msgboxCb,
			ExtraMessageBox,
			"Do you want install the driver for '%s'?\n(the installation will be performed in background)" % self.device.getDescription(),
			"New device found!",
			[
				[ "Yes", "ok.png" ],
				[ "No (ask me again next time)", "cancel.png" ],
				[ "No (never ask me again)", "cancel.png" ]
			]
		)
		
class UsbDevicesNotifier:
	def __init__(self, session):
		self.session = session
		self.installstack = []
		
		self.netlink = socket.socket(socket.AF_NETLINK, socket.SOCK_DGRAM, 15)
		self.netlink.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
		self.netlink.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
		self.netlink.bind((0, 1))
		self.sn = eSocketNotifier(self.netlink.fileno(), POLLIN|POLLPRI)
		self.sn.callback.append(self.dataAvail)

	def installComplete(self, devinst):
		self.installstack.remove(devinst)
		
	def dataAvail(self, what):
		received = self.netlink.recvfrom(16384)

		data = received[0].split('\0')[:-1]
		v = {}

		for x in data:
			i = x.find('=')
			var, val = x[:i], x[i+1:]
			v[var] = val

		if v['SUBSYSTEM'] == 'usb_device' and v['ACTION'] == "add":
			try:
				idVendor = int(open("/sys" + v['DEVPATH'] + "/device/idVendor").read().strip(), 16)
				idProduct = int(open("/sys" + v['DEVPATH'] + "/device/idProduct").read().strip(), 16)
				product = ""
				if fileExists("/sys" + v['DEVPATH'] + "/device/product"):
					product = open("/sys" + v['DEVPATH'] + "/device/product").read().strip()
				device = UsbDevice(idVendor, idProduct, product)
				devinst = UsbDeviceAutoInstall(self.session, device)
				self.installstack.append(devinst)
				devinst.installCb(self.installComplete)
				devinst.install()
			except Exception, e:
				print e
				
class UsbDevicesProbe:
	blacklist = [
		[7531, 1], # Broadcom STB EHCI
		[7531, 2], # Broadcom STB OHCI
		[6720, 257], # USB 2.0 Hub
		[57005, 48879], # BRCM OHCI USB2.0
	]
	
	def __init__(self, session, auto = False):
		self.session = session
		self.auto = auto
		self.installstack = []
		self.devices = []
		if self.auto:
			self.timer = eTimer()
			self.timer.callback.append(self.probe)
			self.timer.start(10000, 1) # delay of 10 seconds
		
	def installComplete(self, devinst):
		self.installstack.remove(devinst)
	
	def isBlacklisted(self, idVendor, idProduct):
		for entry in self.blacklist:
			if entry[0] == idVendor and entry[1] == idProduct:
				return True
				
	def probe(self):
		if len(self.session.dialog_stack) > 0 and self.auto:
			# osd busy.. delay of 10 seconds
			self.timer.start(10000, 1) # delay of 20 seconds
			return
			
		devdirs = os.listdir("/sys/bus/usb/devices/")
		for devdir in devdirs:
			try:
				idVendor = int(open("/sys/bus/usb/devices/" + devdir + "/idVendor").read().strip(), 16)
				idProduct = int(open("/sys/bus/usb/devices/" + devdir + "/idProduct").read().strip(), 16)
				product = ""
				if fileExists("/sys/bus/usb/devices/" + devdir + "/product"):
					product = open("/sys/bus/usb/devices/" + devdir + "/product").read().strip()
					
				if self.isBlacklisted(idVendor, idProduct):
					continue
					
				device = UsbDevice(idVendor, idProduct, product)
				if self.auto:
					devinst = UsbDeviceAutoInstall(self.session, device)
					self.installstack.append(devinst)
					devinst.installCb(self.installComplete)
					devinst.install()
				else:
					self.devices.append(device)
					
			except Exception, e:
				pass
				
		if self.auto:
			global deviceprobe
			deviceprobe = None
				
devicenotifier = None
deviceprobe = None
def initUsbNotifier(session):
	global devicenotifier, deviceprobe
	devicenotifier = UsbDevicesNotifier(session)
	deviceprobe = UsbDevicesProbe(session, True)
	
def TunerEntry(name, module, installed):
	if installed:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"));
	else:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_off.png"));
		
	return (name, module, picture)

class UsbDevices(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.index = 0
		
		self["menu"] = List(list())
		self["menu"].onSelectionChanged.append(self.selectionChanged)
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
				
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
				{
					"red": self.install,
					"cancel": self.quit
				}, -2)
	
		devprobe = UsbDevicesProbe(session)
		devprobe.probe()
		self.devices = devprobe.devices

		self.drawList()
		self.selectionChanged()
		
		smstack.callbacks.append(self.drawList)
		
	def install(self):
		if len(self.devices) == 0:
			return
			
		index = self["menu"].getIndex()
		if index == None:
			index = 0
		
		if len(self.devices[index].getPackage()) == 0 or smstack.checkIfPending(self.devices[index].getPackage()):
			return
			
		if fileExists("/usr/lib/opkg/info/%s.control" % self.devices[index].getPackage()):
			smstack.add(SMStack.REMOVE, self.devices[index].getPackage())
			self.devices[index].setStatus(2)
		else:
			if not fileExists("/usr/lib/opkg/info/v4l-dvb-firmware.control"):
				smstack.add(SMStack.INSTALL, "v4l-dvb-firmware")
			smstack.add(SMStack.INSTALL_WITH_REBOOT, self.devices[index].getPackage())
			self.devices[index].setStatus(3)
			
		self.drawList()
		
	def selectionChanged(self):
		if len(self.devices) == 0:
			return
			
		index = self["menu"].getIndex()
		if index == None:
			index = 0
		
		self.index = index
		
		if len(self.devices[index].getPackage()) == 0 or smstack.checkIfPending(self.devices[index].getPackage()):
			self["key_red"].setText("")
		elif fileExists("/usr/lib/opkg/info/%s.control" % self.devices[index].getPackage()):
			self["key_red"].setText(_("Remove"))
		else:
			self["key_red"].setText(_("Install"))
			
	def drawList(self):
		list = []
		count = 0
		for device in self.devices:
			if len(device.getPackage()) > 0:
				inprogress = smstack.checkIfPending(device.getPackage())
				if inprogress:
					list.append(TunerEntry(device.getDescription(), smstack.getMessage(device.getPackage()), False))
				else:
					installed = fileExists("/usr/lib/opkg/info/%s.control" % device.getPackage())
					if installed:
						info = device.getPackage() + " - installed"
					else:
						info = device.getPackage() + " - not installed"
					list.append(TunerEntry(device.getDescription(), info, installed))
			else:
				list.append(TunerEntry(device.getDescription(), "Driver not found", False))
				
			count += 1
			
		self["menu"].setList(list)
		self["menu"].setIndex(self.index)
		
	def quit(self):
		smstack.callbacks.remove(self.drawList)
		self.close()