from enigma import *
from Screens.Screen import Screen
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Sources.List import List

from SIFTeam.Extra.SAPCL import SAPCL

class SMSort(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.session = session
		self.cachelist = []
		
		self['list'] = List([])
		self["key_green"] = Button()
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
		self.cachelist.append((_("Sort by name"),))
		self.cachelist.append((_("Sort by rank"),))
		self.cachelist.append((_("Sort by ratings"),))
		self.cachelist.append((_("Sort by donwloads"),))
		self["list"].setList(self.cachelist)
	
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		if index == 0:
			config.sifteam.addons_packages_sort.value = "name"
		elif index == 1:
			config.sifteam.addons_packages_sort.value = "rank"
		elif index == 2:
			config.sifteam.addons_packages_sort.value = "ratings"
		elif index == 3:
			config.sifteam.addons_packages_sort.value = "download"
		config.sifteam.addons_packages_sort.save()
		self.close()
		
	def quit(self):
		self.close()