from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel

from SIFTeam.Extra.SAPCL import SAPCL
from Stack import smstack

class SMLog(Screen):
	def __init__(self, session, item):
		Screen.__init__(self, session)
		self.session = session
		self.item = item
		
		self['info'] = Label(item["systemcmd"])
		self['log'] = ScrollLabel(item["log"])
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
		{
			"up": self.pageup,
			"down": self.pagedown,
			"cancel": self.quit
		}, -2)
		
		smstack.callbacks.append(self.updatelog)
		self.onLayoutFinish.append(self.layoutFinished)
		
	def layoutFinished(self):
		self.setTitle("Software Manager - Log - %s" % self.item["package"])
		
	def updatelog(self):
		self["log"].setText(self.item["log"])
		
	def pageup(self):
		self["log"].pageUp()
		
	def pagedown(self):
		self["log"].pageDown()
		
	def quit(self):
		smstack.callbacks.remove(self.updatelog)
		self.close()