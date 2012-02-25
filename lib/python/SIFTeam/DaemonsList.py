from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import crawlDirectory, resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Components.Button import Button

from Extra.ExtraActionBox import ExtraActionBox
from SoftwareManager.Status import SMStatus
from SoftwareManager.Stack import SMStack, smstack

import os
import sys

def DaemonEntry(name, picture, description, started, installed):
	if started:
		pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"));
	else:
		pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_off.png"));
	if not installed:
		pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_error.png"));
		
	pixmap2 = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_daemons/" + picture));
	if not pixmap2:
		pixmap2 = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/empty.png"));
	
	return (pixmap2, name, description, pixmap)
	
class DaemonsList(Screen):
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		
		self.running = list()
		self.installed = list()
		self.daemons = list()
		
		self["menu"] = List(list())
		self["menu"].onSelectionChanged.append(self.selectionChanged)
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"yellow": self.yellow,
			"red": self.red,
			"green": self.green,
			"cancel": self.quit,
		}, -2)
		
		self.onFirstExecBegin.append(self.drawList)
	
	def selectionChanged(self):
		if len(self.daemons) > 0:
			index = self["menu"].getIndex()
			if self.installed[index]:
				if self.running[index]:
					self["key_red"].setText(_("Stop"))
				else:
					self["key_red"].setText(_("Start"))
				
				if self.daemons[index][6]:
					self["key_yellow"].setText(_("Configure"))
				else:
					self["key_yellow"].setText("")
				
				self["key_green"].setText("")
			else:
				self["key_red"].setText("")
				self["key_yellow"].setText("")
				if self.daemons[index][9]:
					self["key_green"].setText(_("Install"))
				else:
					self["key_green"].setText("")
		
	def drawList(self, ret = None):
		self.session.open(ExtraActionBox, "Checking daemons status...", "Daemons", self.actionDrawList)

	def actionDrawList(self):
		self.ishowed = True
		if len(self.daemons) == 0:
			self.loadList()
		self.checkInstalled()
		self.checkRunning()
	
		list = []
		i = 0
		for daemon in self.daemons:
			list.append(DaemonEntry(daemon[0], "%s" % daemon[2], daemon[1], self.running[i], self.installed[i]))
			i += 1
		
		self["menu"].setList(list)
	
	def checkRunning(self):
		self.running = list()
		for daemon in self.daemons:
			self.running.append(daemon[3]())
			
	def checkInstalled(self):
		self.installed = list()
		for daemon in self.daemons:
			self.installed.append(daemon[7]())
		
	def loadList(self):
		self.daemons = list()
		tdaemons = crawlDirectory("%s/Daemons/" % os.path.dirname(sys.modules[__name__].__file__), ".*\.ext$")
		tdaemons.sort()
		for daemon in tdaemons:
			if daemon[1][:1] != ".":
				src = open(os.path.join(daemon[0], daemon[1]))
				exec src.read()
				src.close()
				self.daemons.append((daemon_name, daemon_description, daemon_icon, daemon_fnc_status, daemon_fnc_start, daemon_fnc_stop, daemon_class_config, daemon_fnc_installed, daemon_fnc_boot, daemon_package))
	
	def yellow(self):
		index = self["menu"].getIndex()
		if self.installed[index]:
			if self.daemons[index][6]:
				self.session.open(self.daemons[index][6])

	def green(self):
		index = self["menu"].getIndex()
		if not self.installed[index]:
			if self.daemons[index][9]:
				smstack.add(SMStack.INSTALL, self.daemons[index][9])
				self.session.openWithCallback(self.drawList, SMStatus)
			
	def red(self):
		if len(self.daemons) > 0:
			index = self["menu"].getIndex()
			if self.running[index]:
				self.session.openWithCallback(self.drawList, ExtraActionBox, "Stopping %s..." % self.daemons[index][0], "Daemons", self.startstop)
			else:
				self.session.openWithCallback(self.drawList, ExtraActionBox, "Starting %s..." % self.daemons[index][0], "Daemons", self.startstop)
			
	def startstop(self):
		if len(self.daemons) > 0:
			index = self["menu"].getIndex()
			if self.installed[index]:
				if self.running[index]:
					self.daemons[index][5]()
				else:
					self.daemons[index][4]()
				self.daemons[index][8](self.daemons[index][3]())
		
	def quit(self):
		self.close()
