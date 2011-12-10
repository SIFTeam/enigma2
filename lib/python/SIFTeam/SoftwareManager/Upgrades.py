from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap

from SIFTeam.Extra.SAPCL import SAPCL

def UpgradeEntry(name, oldversion, newversion):
	pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/install_now.png"))
		
	return (pixmap, name, oldversion, ">", newversion)
	
class SMUpgrades(Screen):
	def __init__(self, session, upgrades):
		Screen.__init__(self, session)
		
		self.session = session
		self.upgrades = upgrades
		self.cachelist = []
		
		self['list'] = List([])
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button("")
		self["key_yellow"] = Button()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.quit,
			"ok": self.ok
		}, -2)
		
		self.renderList()
		
	def renderList(self):
		self.cachelist = []
		
		for upgrade in self.upgrades:
			self.cachelist.append(UpgradeEntry(upgrade["package"], upgrade["oldversion"], upgrade["newversion"]))
			
		self["list"].setList(self.cachelist)
		
	def ok(self):
		print "ok"
		
	def quit(self):
		self.close()