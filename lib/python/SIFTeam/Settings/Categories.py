from enigma import *
from Screens.Screen import Screen
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap

from SIFTeam.Extra.SAPCL import SAPCL

from Settings import STSettings
from FileBrowser import STFileBrowser
from KeepBouquets import STKeepBouquets
from Setup import STSetup

def CategoryEntry(name, count, picture):
	pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/" + picture))
	if not pixmap:
		pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/folder.png"))
		
	return (pixmap, name, count)

class STCategories(Screen):
	def __init__(self, session, settings):
		Screen.__init__(self, session)
		
		self.session = session
		self.settings = settings
		self.categories = []
		for setting in self.settings["settings"]:
			if "category" in setting and setting["category"] not in self.categories:
				self.categories.append(setting["category"])
				
		self.categories = sorted(self.categories)
		
		self['list'] = List([])
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.quit,
			"ok": self.open
		}, -2)
		
		self.renderList()
		
	def renderList(self):
		self.cachelist = []
		self.cachelist.append(CategoryEntry(_("Options"), "", "config.png"))
		if config.sifteam.settings.keepterrestrial.value:
			self.cachelist.append(CategoryEntry(_("Select bouquets to keep"), "", "bookmark.png"))
		
		for category in self.categories:
			count = 0
			for setting in self.settings["settings"]:
				if setting["category"] == category:
					count += 1
					
			if count == 1:
				pkgcount = _("1 package")
			else:
				pkgcount = _("%d packages") % count
				
			self.cachelist.append(CategoryEntry(category, pkgcount, "folder.png"))
			
		self.cachelist.append(CategoryEntry(_("Load from file"), "", "packages.png"))
		self["list"].setList(self.cachelist)
		
	def open(self):
		if len(self.categories) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		if len(self.cachelist) == index + 1:
			self.session.open(STFileBrowser)
			return
				
		if index == 0:
			self.session.openWithCallback(self.renderList, STSetup)
			return
			
		index -= 1
		
		if config.sifteam.settings.keepterrestrial.value:
			if index == 0:
				self.session.open(STKeepBouquets)
				return

			index -= 1
			
		category = self.categories[index]
		tmp = []
		for setting in self.settings["settings"]:
			if setting["category"] == category:
				tmp.append(setting)
				
		self.session.open(STSettings, tmp)
		
	def quit(self):
		self.close()