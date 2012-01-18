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
			smstack.add(SMStack.INSTALL_WITH_REBOOT, self.device.getPackage())
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

devicenotifier = None
def initUsbNotifier(session):
	global devicenotifier
	devicenotifier = UsbDevicesNotifier(session)
	
def TunerEntry(name, module, started):
	if started:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"));
	else:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_off.png"));
		
	return (name, module, picture)

class UsbDevices(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["menu"] = List(list())
		self["menu"].onSelectionChanged.append(self.selectionChanged)
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
				
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
				{
					"red": self.ok,
					#"green": self.green,
					"blue": self.close,
					"cancel": self.close,
				}, -2)
	
		#lsusb = os.popen("/sbin/lsusb")
		#buff = lsusb.read()
		#lsusb.close()
		#buff = buff.split("\n")
		buff = []
		i = 0
		self.usblist = []
		while i < len(buff):
			if len(buff[i]) > 0:
				offset = buff[i].find(": ID ") + 5
				entry = buff[i][offset:]
				if entry[:9] != "0000:0000":
					self.usblist.append([entry[0:4], entry[5:9], entry[10:].strip()])
			i += 1
			
		#dict = open("/usr/share/usbloader/dictionary.csv", "r")
		self.usbdict = []
		#for line in dict:
		#	buff = line.strip().split(";")
		#	
		#	buff[0] = buff[0][2:]
		#	if len(buff[0]) == 1:
		#		buff[0] = "000" + buff[0]
		#	elif len(buff[0]) == 2:
		#		buff[0] = "00" + buff[0]
		#	elif len(buff[0]) == 3:
		#		buff[0] = "0" + buff[0]
		#		
		#	buff[1] = buff[1][2:]
		#	if len(buff[1]) == 1:
		#		buff[1] = "000" + buff[1]
		#	elif len(buff[1]) == 2:
		#		buff[1] = "00" + buff[1]
		#	elif len(buff[1]) == 3:
		#		buff[1] = "0" + buff[1]
		#	
		#	self.usbdict.append(buff)
		#dict.close()

		modules = open("/proc/modules", "r")
		self.moduleslist = []
		for line in modules:
			buff = line.strip().split(" ")
			buff = buff[0].strip()
			self.moduleslist.append(buff)
		modules.close()
		
		self.drawList()
		
	def ok(self):
		#global devicenotifier
		#devicenotifier.newDevice(3277, 147)
		pass
		
	def selectionChanged(self):
		pass

	def searchDevice(self, vid, pid):
		for entry in self.usbdict:
			if entry[0] == vid and entry[1] == pid:
				return entry
				
		return None
		
	def isInModules(self, name):
		for entry in self.moduleslist:
			if entry == name:
				return True
			elif entry == name.replace("-", "_"):
				return True
			
		return False
	
	def drawList(self):
		llist = []
		for entry in self.usblist:
			dentry = self.searchDevice(entry[0], entry[1])
			if (dentry == None):
				llist.append(TunerEntry(entry[0] + ":" + entry[1] + " - " + entry[2], "Device not in dictionary", False))
			else:
				llist.append(TunerEntry(entry[0] + ":" + entry[1] + " - " + entry[2], dentry[2] + ": " + dentry[3] + " (driver: " + dentry[4] + ")", self.isInModules(dentry[4])))

		self["menu"].setList(llist)
