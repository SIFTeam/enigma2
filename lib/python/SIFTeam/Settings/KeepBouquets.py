from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.config import getConfigListEntry, config
from Components.Sources.List import List
from Components.ActionMap import ActionMap
from Components.Button import Button
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN

from Common import ENIGMA2_SETTINGS_PWD, SettingsLoader

from urlparse import urlparse

class STKeepBouquets(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.session = session
		self.drawList = []

		self["list"] = List(self.drawList)
		self["key_red"] = Button("")
		self["key_green"] = Button("")
		self["key_yellow"] = Button("")
		self["key_blue"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
				{
					"ok": self.ok,
					"cancel": self.quit
				}, -2)
				
		self.refresh()
	
	def buildListEntry(self, enabled, name, type):
		if enabled:
			pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"))
		else:
			pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_off.png"))

		return((pixmap, name, type))
		
	def refresh(self):
		settings = SettingsLoader()
		self.listTv = settings.readBouquetsTvList(ENIGMA2_SETTINGS_PWD)
		self.listRadio = settings.readBouquetsRadioList(ENIGMA2_SETTINGS_PWD)
		self.drawList = []
		self.listAll = []
		self.bouquets = config.sifteam.settings.keepbouquets.value.split("|")
		
		if self.listTv is not None and self.listRadio is not None:
			for x in self.listTv:
				if x[0] in self.bouquets:
					self.drawList.append(self.buildListEntry(True, x[1], "TV"))
				else:
					self.drawList.append(self.buildListEntry(False, x[1], "TV"))
				self.listAll.append(x)

			for x in self.listRadio:
				if x[0] in self.bouquets:
					self.drawList.append(self.buildListEntry(True, x[1], "Radio"))
				else:
					self.drawList.append(self.buildListEntry(False, x[1], "Radio"))
				self.listAll.append(x)
				
		self["list"].setList(self.drawList)
		
	def ok(self):
		if len(self.listAll) == 0:
			return
		index = self["list"].getIndex()
		
		if self.listAll[index][0] in self.bouquets:
			self.bouquets.remove(self.listAll[index][0])
		else:
			self.bouquets.append(self.listAll[index][0])
		config.sifteam.settings.keepbouquets.value = "|".join(self.bouquets)
		config.save()
		self.refresh()
		self["list"].setIndex(index)

	def quit(self):
		self.close()