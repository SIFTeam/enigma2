from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap

from SIFTeam.Extra.SAPCL import SAPCL
from Stack import SMStack, smstack
from Log import SMLog

def StatusEntry(name, description, done, error):
	if error:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_error.png"))
	else:
		if done:
			picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"))
		else:
			picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_off.png"))
		
	if len(description) > 40:
		idx = description.find(" ", 40)
		if idx != -1:
			description = description[:idx] + "..."
			
	return (picture, name, description)
	
class SMStatus(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.cachelist = []
		self.index = 0
		
		self['list'] = List([])
		self["list"].onSelectionChanged.append(self.selectionChanged)
		self["key_green"] = Button("")
		self["key_red"] = Button(_("Clear"))
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"red": self.clear,
			"cancel": self.quit,
			"ok": self.ok
		}, -2)
		
		smstack.callbacks.append(self.renderList)
		self.renderList()
		
	def renderList(self):
		self.cachelist = []
		
		for cmd in smstack.stack:
			name = ""
			if cmd["cmd"] == SMStack.INSTALL:
				name = "Install " + cmd["package"]
			elif cmd["cmd"] == SMStack.REMOVE:
				name = "Remove " + cmd["package"]
			elif cmd["cmd"] == SMStack.DOWNLOAD:
				name = "Download " + cmd["package"]
			elif cmd["cmd"] == SMStack.UPGRADE:
				name = "Upgrading system"
				
			
			self.cachelist.append(StatusEntry(name, cmd["message"], cmd["status"] == SMStack.DONE, cmd["status"] == SMStack.ERROR))
			
		self["list"].setList(self.cachelist)
		self["list"].setIndex(self.index)
		
	def selectionChanged(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		self.index = index
		
	def clear(self):
		smstack.clear()
		self.renderList()
		
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
			
		self.session.open(SMLog, smstack.stack[index])
		
	def quit(self):
		smstack.callbacks.remove(self.renderList)
		self.close()