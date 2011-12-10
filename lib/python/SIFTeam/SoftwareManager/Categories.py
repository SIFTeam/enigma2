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
from SIFTeam.Extra.ExtraActionBox import ExtraActionBox
from Packages import SMPackages
from FileBrowser import SMFileBrowser
from Upgrades import SMUpgrades
from Feeds import SMFeeds
from Status import SMStatus
from Stack import SMStack, smstack

def CategoryEntry(name, picture, count):
	pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/" + picture))
	if not pixmap:
		pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/folder.png"))
		
	return (pixmap, name, count)

class SMCategories(Screen):
	def __init__(self, session, categories, upgrades):
		Screen.__init__(self, session)
		
		self.session = session
		self.sifapi = SAPCL()
		self.categories = categories
		self.upgrades = upgrades
		self.showall = False
		self.cachelist = []
		
		self['list'] = List([])
		self["key_green"] = Button(_("Feeds"))
		self["key_red"] = Button("")
		self["key_blue"] = Button(_("Status"))
		self["key_yellow"] = Button(_("All"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.status,
			"cancel": self.quit,
			"ok": self.ok,
			"yellow": self.toggleShowAll,
			"green": self.feeds,
			"red": self.upgrade
		}, -2)
		
		self.renderList()
		
	def toggleShowAll(self):
		self.showall = not self.showall
		if self.showall:
			self["key_yellow"].setText(_("Essentials"))
		else:
			self["key_yellow"].setText(_("All"))
		self.session.openWithCallback(self.executeRequestCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequest)
			
	def executeRequest(self):
		api = SAPCL()
		return api.getCategories(0, not self.showall)

	def executeRequestCallback(self, result):
		self.categories = result
		self.renderList()
	
	def renderList(self):
		self.cachelist = []
		if len(self.upgrades) > 0:
			self.cachelist.append(CategoryEntry("%d updates found" % len(self.upgrades), "install_now.png", ""))
			self["key_red"].setText(_("Update"))
		else:
			self["key_red"].setText("")
		
		self.cachelist.append(CategoryEntry("Top 10 (highest rank)", "top10.png", ""))
		self.cachelist.append(CategoryEntry("Top 10 (most downloaded)", "top10.png", ""))
		
		for category in self.categories["categories"]:
			if category["packages"] == 1:
				pkgcount = "1 package"
			else:
				pkgcount = "%d packages" % category["packages"]
			if category["description"]:
				self.cachelist.append(CategoryEntry(category["description"], category["identifier"] + ".png", pkgcount))
			else:
				self.cachelist.append(CategoryEntry(category["name"], category["identifier"] + ".png", pkgcount))
			
		self.cachelist.append(CategoryEntry("Install from file (ipk/tar.gz)", "package.png", ""))
		
		self["list"].setList(self.cachelist)
	
	def executeRequestPackages(self):
		api = SAPCL()
		if self.index == -1:
			return api.getTopTen("rank")
		elif self.index == -2:
			return api.getTopTen("downloads")
		else:
			return api.getPackages(self.categories["categories"][self.index]["id"], config.sifteam.addons_packages_sort.value)

	def executeRequestPackagesCallback(self, result):
		if self.index == -1:
			self.session.open(SMPackages, result, "Top 10 (highest rank)", -2)
		elif self.index == -2:
			self.session.open(SMPackages, result, "Top 10 (highest rank)", -3)
		else:
			self.session.open(SMPackages, result, self.categories["categories"][self.index]["name"], self.categories["categories"][self.index]["id"])
		
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
			
		if len(self.cachelist) == index + 1:
			self.session.open(SMFileBrowser)
			return
				
		if len(self.upgrades) > 0:
			if index == 0:
				self.session.open(SMUpgrades, self.upgrades)
				return
				
			index -= 1
			
		if index == 0:
			print "top 10 rate"
			self.index = -1
			self.session.openWithCallback(self.executeRequestPackagesCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequestPackages)
			return
				
		index -= 1
		
		if index == 0:
			print "top 10 download"
			self.index = -2
			self.session.openWithCallback(self.executeRequestPackagesCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequestPackages)
			return
				
		index -= 1
		
		self.index = index
		self.session.openWithCallback(self.executeRequestPackagesCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequestPackages)
		
	def feeds(self):
		self.session.open(SMFeeds)
		
	def upgrade(self):
		smstack.add(SMStack.UPGRADE, "")
		self.session.open(SMStatus)
		
	def status(self):
		self.session.open(SMStatus)
		
	def quit(self):
		self.close()