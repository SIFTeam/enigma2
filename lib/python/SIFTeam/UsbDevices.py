from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Components.Button import Button

from Extra.ExtraMessageBox import ExtraMessageBox

from Addons import Addons

import os

import re
import string

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
	
		lsusb = os.popen("/sbin/lsusb")
		buff = lsusb.read()
		lsusb.close()
		buff = buff.split("\n")
		i = 0
		self.usblist = []
		while i < len(buff):
			if len(buff[i]) > 0:
				offset = buff[i].find(": ID ") + 5
				entry = buff[i][offset:]
				if entry[:9] != "0000:0000":
					self.usblist.append([entry[0:4], entry[5:9], entry[10:].strip()])
			i += 1
			
		dict = open("/usr/share/usbloader/dictionary.csv", "r")
		self.usbdict = []
		for line in dict:
			buff = line.strip().split(";")
			
			buff[0] = buff[0][2:]
			if len(buff[0]) == 1:
				buff[0] = "000" + buff[0]
			elif len(buff[0]) == 2:
				buff[0] = "00" + buff[0]
			elif len(buff[0]) == 3:
				buff[0] = "0" + buff[0]
				
			buff[1] = buff[1][2:]
			if len(buff[1]) == 1:
				buff[1] = "000" + buff[1]
			elif len(buff[1]) == 2:
				buff[1] = "00" + buff[1]
			elif len(buff[1]) == 3:
				buff[1] = "0" + buff[1]
			
			self.usbdict.append(buff)
		dict.close()

		modules = open("/proc/modules", "r")
		self.moduleslist = []
		for line in modules:
			buff = line.strip().split(" ")
			buff = buff[0].strip()
			self.moduleslist.append(buff)
		modules.close()
		
		self.drawList()
		
	def ok(self):
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
