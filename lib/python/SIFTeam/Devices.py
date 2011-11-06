from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Tools.Directories import fileExists
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest

from Extra.ExtrasList import ExtrasList, SimpleEntry

from HddInfo import HddInfo
from HddSetup import HddSetup

class Devices(Screen):
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		
		list = []
		list.append(SimpleEntry(_("Hard Drive Informations"), "hdinfo.png"))
		list.append(SimpleEntry(_("Hard Drive Setup"), "hdsetup.png"))
		list.append(SimpleEntry("---", "div.png"))
		list.append(SimpleEntry(_("Usb Stick Setup"), "usbsetup.png"))
		
		self['menu'] = ExtrasList(list)
		self["actions"] = ActionMap(["SetupActions"],
		{
			"ok": self.ok,
			"cancel": self.quit,
		}, -2)
		
	def ok(self):
		index = self['menu'].getSelectedIndex()
		if (index == 0):
			self.session.open(HddInfo)
		elif (index == 1):
			self.session.open(HddSetup)
		#elif (index == 3):
		#	self.session.open(Swap)
		#elif (index == 4):
		#	self.session.open(DaemonsList)
			
	def quit(self):
		self.close()