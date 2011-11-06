from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.SystemInfo import SystemInfo
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigBoolean, ConfigYesNo
from Components.ActionMap import ActionMap
from Components.Button import Button

import os

import re
import string

class KernelModules(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.ntfs = 1
		self.cifs = 1
		self.autofs4 = 1
		self.sci_ng = 1
		self.pl2303 = 0
		self.zd1211b = 0
		
		self.load()
		
		self.list = []
		self.list.append(getConfigListEntry(_("Module ntfs.ko:"), ConfigYesNo(default=self.ntfs)))
		self.list.append(getConfigListEntry(_("Module cifs.ko:"), ConfigYesNo(default=self.cifs)))
		self.list.append(getConfigListEntry(_("Module zd1211b.ko:"), ConfigYesNo(default=self.zd1211b)))
		
		ConfigListScreen.__init__(self, self.list, session = session)
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
				{
					"red": self.ok,
					#"green": self.green,
					"blue": self.keyCancel,
					"cancel": self.keyCancel,
				}, -2)
				
		self["key_green"] = Button("")
		self["key_red"] = Button(_("Ok"))
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
	
	def load(self):
		try:
			f = open("/etc/settings.modules", "r")
		except Exception, e:
			return
			
		import re
		commentRe = re.compile(r"#(.*)")
		entryRe = re.compile(r"(.*)=(.*)")
		
		for line in f.readlines(): 
			comment = re.findall(commentRe, line)
			if not comment:
				entry = re.findall(entryRe, line)
				if entry:
					key = entry[0][0].strip()
					value = entry[0][1].strip()
					if key == "ntfs":
						self.ntfs = int(value)
					elif key == "cifs":
						self.cifs = int(value)
					elif key == "autofs4":
						self.autofs4 = int(value)
					elif key == "sci_ng":
						self.sci_ng = int(value)
					elif key == "pl2303":
						self.pl2303 = int(value)
					elif key == "zd1211b":
						self.zd1211b = int(value)
						
		f.close()
		
	def save(self):
		try:
			f = open("/etc/settings.modules", "w")
		except Exception, e:
			return
			
		f.write("ntfs=%d\n" % (self.ntfs))
		f.write("cifs=%d\n" % (self.cifs))
		f.write("zd1211b=%d\n" % (self.zd1211b))
		
		f.close()
		
	def ok(self):
		self.ntfs = self.list[0][1].getValue()
		self.cifs = self.list[1][1].getValue()
		self.zd1211b = self.list[2][1].getValue()
		self.save()
		self.close()