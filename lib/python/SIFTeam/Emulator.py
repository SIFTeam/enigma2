from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Components.Button import Button

from Extra.ExtraActionBox import ExtraActionBox
from Extra.Emud import emud

import os
import sys

def EmulatorEntry(name, version, description, started):
	if started:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"));
	else:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_off.png"));
		
	return (name, version, description, picture)
	
class Emulator(Screen):
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		
		self.cachelist = []
		self.started = []
		self.lastindex = 0
		
		self["menu"] = List(self.cachelist)
		self["menu"].onSelectionChanged.append(self.selectionChanged)
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"red": self.red,
			"green": self.green,
			"blue": self.quit,
			"cancel": self.quit,
		}, -2)
		
		self.timer = eTimer()
		self.timer.callback.append(self.listUpdated)
		self.timer.start(200, 1)
	
	def selectionChanged(self):
		if len(self.cachelist) > 0:
			index = self["menu"].getIndex()
			if self.started[index]:
				self["key_red"].setText(_("Stop"))
				self["key_green"].setText(_("Restart"))
			else:
				self["key_red"].setText(_("Start"))
				self["key_green"].setText("")

	def listUpdated(self):
		self.cachelist = []
		self.started = []
		self.ids = []
		emus = emud.getEmuList()
		for emu in emus:
			self.cachelist.append(EmulatorEntry(emu[0], emu[1], emu[2], emu[3]))
			self.started.append(emu[3])
			self.ids.append(emu[4])
			
		self["menu"].setList(self.cachelist)
		if self.lastindex < len(self.cachelist):
			self["menu"].setCurrentIndex(self.lastindex)

	def start(self):
		emud.startEmu(self.ids[self.lastindex])
		self.listUpdated()
		
	def stop(self):
		emud.stopEmu()
		self.listUpdated()
		
	def restart(self):
		emud.restartEmu()
		self.listUpdated()
		
	def green(self):
		if len(self.cachelist) > 0:
			index = self["menu"].getIndex()
			if self.started[index]:
				self.session.open(ExtraActionBox, "Restarting emulator...", "Restart emu", self.restart)
			
	def red(self):
		if len(self.cachelist) > 0:
			index = self["menu"].getIndex()
			self.lastindex = index
			if self.started[index]:
				self.session.open(ExtraActionBox, "Stopping emulator...", "Stop emu", self.stop)
			else:
				self.session.open(ExtraActionBox, "Starting emulator...", "Start emu", self.start)
		
	def quit(self):
		self.close()

class EmulatorInfo(Screen):
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"cancel": self.quit,
		}, -2)
		
	def quit(self):
		self.close()

class CardServer(Screen):
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		
		self.cachelist = []
		self.started = []
		self.lastindex = 0
		
		self["menu"] = List(self.cachelist)
		self["menu"].onSelectionChanged.append(self.selectionChanged)
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"red": self.red,
			"green": self.green,
			"blue": self.quit,
			"cancel": self.quit,
		}, -2)
		
		self.timer = eTimer()
		self.timer.callback.append(self.listUpdated)
		self.timer.start(200, 1)
		
	def selectionChanged(self):
		if len(self.cachelist) > 0:
			index = self["menu"].getIndex()
			if self.started[index]:
				self["key_red"].setText(_("Stop"))
				self["key_green"].setText(_("Restart"))
			else:
				self["key_red"].setText(_("Start"))
				self["key_green"].setText("")
				
	def listUpdated(self):
		self.cachelist = []
		self.started = []
		self.ids = []
		
		emus = emud.getCsList()
		for emu in emus:
			self.cachelist.append(EmulatorEntry(emu[0], emu[1], emu[2], emu[3]))
			self.started.append(emu[3])
			self.ids.append(emu[4])
		
		self["menu"].setList(self.cachelist)
		if self.lastindex < len(self.cachelist):
			self["menu"].setCurrentIndex(self.lastindex)
			
	def start(self):
		emud.startCs(self.ids[self.lastindex])
		self.listUpdated()
		
	def stop(self):
		emud.stopCs()
		self.listUpdated()
		
	def restart(self):
		emud.restartCs()
		self.listUpdated()
		
	def green(self):
		if len(self.cachelist) > 0:
			index = self["menu"].getIndex()
			if self.started[index]:
				self.session.open(ExtraActionBox, "Restarting card server...", "Restart cs", self.restart)
			
	def red(self):
		if len(self.cachelist) > 0:
			index = self["menu"].getIndex()
			self.lastindex = index
			if self.started[index]:
				self.session.open(ExtraActionBox, "Stopping card server...", "Stop cs", self.stop)
			else:
				self.session.open(ExtraActionBox, "Starting card server...", "Start cs", self.start)
				
	def quit(self):
		self.close()
