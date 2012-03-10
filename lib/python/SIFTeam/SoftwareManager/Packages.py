from enigma import *
from Screens.Screen import Screen
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists
from Tools.LoadPixmap import LoadPixmap

from SIFTeam.Extra.SAPCL import SAPCL
from SIFTeam.Extra.ExtraActionBox import ExtraActionBox
from Rank import SMRank
from Sort import SMSort
from Package import SMPackage
from Stack import SMStack, smstack
from Screenshot import SMScreenshot

def PackageEntry(name, installed, rank, description, inprogress, ratings):
	rank = int(round(rank, 0))
	star = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star.png"))
	star_disabled = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star_disabled.png"))
	
	if inprogress:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/empty.png"))
	else:
		if installed:
			picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"))
		else:
			picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_off.png"))
		
	if len(description) > 40:
		idx = description.find(" ", 40)
		if idx != -1:
			description = description[:idx] + "..."
			
	if ratings == 0:
		# TODO: change stars if package never rated
		return (picture, name, star_disabled, star_disabled, star_disabled, star_disabled, star_disabled, description)
		
	if rank == 1:
		return (picture, name, star, star_disabled, star_disabled, star_disabled, star_disabled, description)
	elif rank == 2:
		return (picture, name, star, star, star_disabled, star_disabled, star_disabled, description)
	elif rank == 3:
		return (picture, name, star, star, star, star_disabled, star_disabled, description)
	elif rank == 4:
		return (picture, name, star, star, star, star, star_disabled, description)
	elif rank == 5:
		return (picture, name, star, star, star, star, star, description)
		
	return (picture, name, star_disabled, star_disabled, star_disabled, star_disabled, star_disabled, description)
	
class SMPackages(Screen):
	def __init__(self, session, packages, categoryname, categoryid=-1, showall=False):
		Screen.__init__(self, session)
		
		self.categoryid = categoryid
		self.categoryname = categoryname
		self.session = session
		self.packages = packages
		self.cachelist = []
		self.showall = showall
		self.index = 0
		
		self['list'] = List([])
		self["list"].onSelectionChanged.append(self.selectionChanged)
		if categoryid == -1:
			self["key_green"] = Button("")
			self["key_yellow"] = Button("")
		elif categoryid < -1:
			self["key_green"] = Button(_("Rank"))
			self["key_yellow"] = Button("")
		else:
			self["key_green"] = Button(_("Rank"))
			self["key_yellow"] = Button(_("Sort"))
		self["key_red"] = Button(_("Install"))
		self["key_blue"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.quit,
			"ok": self.ok,
			"green": self.rank,
			"yellow": self.sort,
			"red": self.install,
			"blue": self.screenshot
		}, -2)
		
		self.renderList()
		smstack.callbacks.append(self.renderList)
		
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle("Software Manager - Packages - %s" % self.categoryname)
	
	def renderList(self):
		self.cachelist = []
		
		for package in self.packages["packages"]:
			rank = 0.0
			if "rank" in package.keys():
				rank = float(package["rank"])
			
			ratings = 0
			if "ratings" in package.keys():
				ratings = float(package["ratings"])
				
			installed = fileExists("/usr/lib/opkg/info/%s.control" % package["package"])
			inprogress = smstack.checkIfPending(package["package"])
			
			if inprogress:
				message = smstack.getMessage(package["package"])
			else:
				message = package["description"]
				
			self.cachelist.append(PackageEntry(package["name"], installed, rank, message, inprogress, ratings))
			
		self["list"].setList(self.cachelist)
		self["list"].setIndex(self.index)
		self.selectionChanged()
		
	def executeRequestPackages(self):
		api = SAPCL()
		if self.categoryid == -2:
			self.packages = api.getTopTen("rank")
		elif self.categoryid == -3:
			self.packages = api.getTopTen("downloads")
		else:
			self.packages = api.getPackages(self.categoryid, config.sifteam.addons_packages_sort.value, self.showall == False)

	def executeRequestPackagesCallback(self, result):
		self.renderList()
	
	def selectionChanged(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		if smstack.checkIfPending(self.packages["packages"][index]["package"]):
			self["key_red"].setText("")
		elif fileExists("/usr/lib/opkg/info/%s.control" % self.packages["packages"][index]["package"]):
			self["key_red"].setText(_("Remove"))
		else:
			self["key_red"].setText(_("Install"))
			
		screenshot = None
		if "screenshot" in self.packages["packages"][index].keys():
			screenshot = self.packages["packages"][index]["screenshot"]
			
		if screenshot:
			self["key_blue"].setText(_("Screenshot"))
		else:
			self["key_blue"].setText("")
		
		self.index = index
	
	def rankCallback(self):
		self.session.openWithCallback(self.executeRequestPackagesCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequestPackages)
		
	def rank(self):
		if self.categoryid == -1:
			return
			
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
			
		self.index = index
		self.session.openWithCallback(self.rankCallback, SMRank, self.packages["packages"][index])
		
	def sortCallback(self):
		self.session.openWithCallback(self.executeRequestPackagesCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequestPackages)
		
	def sort(self):
		if self.categoryid < 0:
			return
			
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
			
		self.index = index
		self.session.openWithCallback(self.sortCallback, SMSort)
		
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		self.index = index
		self.session.open(SMPackage, self.packages, index, self.categoryid)
		
	def install(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
			
		if smstack.checkIfPending(self.packages["packages"][index]["package"]):
			return
			
		if fileExists("/usr/lib/opkg/info/%s.control" % self.packages["packages"][index]["package"]):
			smstack.add(SMStack.REMOVE, self.packages["packages"][index]["package"])
		else:
			smstack.add(SMStack.INSTALL, self.packages["packages"][index]["package"])
			
		self.renderList()
		
	def screenshot(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
			
		screenshot = None
		if "screenshot" in self.packages["packages"][index].keys():
			screenshot = self.packages["packages"][index]["screenshot"]
			
		if screenshot:
			self.session.open(SMScreenshot, self.packages["packages"][index])
		
	def quit(self):
		smstack.callbacks.remove(self.renderList)
		self.close()