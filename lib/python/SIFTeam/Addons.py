from enigma import *
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Components.Pixmap import Pixmap
from Components.FileList import FileList
from Components.config import config
from Components.PluginComponent import plugins
from Components.Sources.List import List
from Components.AVSwitch import AVSwitch
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS, fileExists
from Tools.LoadPixmap import LoadPixmap

from Extra.ExtraMessageBox import ExtraMessageBox
from Extra.ExtraActionBox import ExtraActionBox
from Extra.SAPCL import SAPCL

import re
import os
import urllib

def FormatSize(size):
	try:
		isize = int(size)
	except Exception:
		return ""
	
	_abbrevs = [ (1<<20L, ' MB'), (1<<10L, ' KB'), (1, ' bytes') ]
	for factor, suffix in _abbrevs:
		if isize > factor:
			break
	return `int(isize/factor)` + suffix

def CategoryEntry(name, picture, count):
	pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/" + picture))
	if not pixmap:
		pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/folder.png"))
		
	return (pixmap, name, count)

def UpgradeEntry(name, oldversion, newversion):
	pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/install_now.png"))
		
	return (pixmap, name, oldversion, ">", newversion)
	
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
	
def RankEntry(rank, description):
	rank = int(round(rank, 0))
	star = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star.png"))
	star_disabled = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star_disabled.png"))
	
	if rank == 1:
		return (star, star_disabled, star_disabled, star_disabled, star_disabled, description)
	elif rank == 2:
		return (star, star, star_disabled, star_disabled, star_disabled, description)
	elif rank == 3:
		return (star, star, star, star_disabled, star_disabled, description)
	elif rank == 4:
		return (star, star, star, star, star_disabled, description)
	elif rank == 5:
		return (star, star, star, star, star, description)
		
	return (star_disabled, star_disabled, star_disabled, star_disabled, star_disabled, description)
	
class AddonsStack(object):
	INSTALL = 0
	REMOVE = 1
	UPGRADE = 2
	DOWNLOAD = 3
	
	WAIT = 0
	PROGRESS = 1
	DONE = 2
	ERROR = 3
	
	stack = []
	current = None
	
	callbacks = []
	
	def __init__(self):
		pass
		
	def add(self, cmd, package):
		if not self.clearPackage(package):
			return False
		
		self.stack.append({
			"cmd": cmd,
			"package": package,
			"status": self.WAIT,
			"message": "Waiting...",
			"log": "",
			"systemcmd": ""
		})
		if not self.current:
			self.processNextCommand()
		return True
		
	def clear(self):
		newstack = []
		for item in self.stack:
			if item["status"] < 2:
				newstack.append(item)
		self.stack = newstack
		
	def doCallbacks(self):
		for cb in self.callbacks:
			cb()
			
	def clearPackage(self, package):
		for item in self.stack:
			if item["package"] == package:
				if item["status"] < 2:
					return False
				self.stack.remove(item)
				return True
		
		return True
		
	def checkIfPending(self, package):
		for item in self.stack:
			if item["package"] == package:
				return item["status"] < 2
		
		return False
		
	def getMessage(self, package):
		for item in self.stack:
			if item["package"] == package:
				return item["message"]
				
		return ""
		
	def processNextCommand(self):
		for item in self.stack:
			if item["status"] == self.WAIT:
				self.current = item
				break
				
		if not self.current:
			return
			
		self.app = eConsoleAppContainer()
		self.app.appClosed.append(self.cmdFinished)
		self.app.dataAvail.append(self.cmdData)
		
		self.current["status"] = self.PROGRESS
		
		if self.current["cmd"] == self.INSTALL:
			cmd = "opkg -V2 install " + self.current["package"]
			print "Installing package %s (%s)" % (self.current["package"], cmd)
			self.current["message"] = "Installing " + self.current["package"]
		elif self.current["cmd"] == self.REMOVE:
			cmd = "opkg -V2 remove " + self.current["package"]
			print "Removing package %s (%s)" % (self.current["package"], cmd)
			self.current["message"] = "Removing " + self.current["package"]
		elif self.current["cmd"] == self.DOWNLOAD:
			cmd = "cd /tmp && opkg -V2 download " + self.current["package"]
			print "Downloading package %s (%s)" % (self.current["package"], cmd)
			self.current["message"] = "Downloading " + self.current["package"]
		elif self.current["cmd"] == self.UPGRADE:
			cmd = "opkg -V2 upgrade"
			print "Upgrading (%s)" % cmd
			self.current["message"] = "Upgrading"
		else:
			self.cmdFinished(-1)
			
		self.current["systemcmd"] = cmd
		if self.app.execute(cmd):
			self.cmdFinished(-1)
			
	def cmdData(self, data):
		self.current["log"] += data
		
		rows = data.split("\n")
		for row in rows:
			if row[:16] == "opkg_install_pkg":
				self.current["message"] = row[17:].strip()
				self.doCallbacks()
			elif row[:11] == "Installing ":
				self.current["message"] = row.strip()
				self.doCallbacks()
			elif row[:12] == "Downloading ":
				self.current["message"] = row.strip()
				self.doCallbacks()
			elif row[:12] == "Configuring ":
				self.current["message"] = row.strip()
				self.doCallbacks()
				
	def cmdFinished(self, result):
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		if result == 0:
			print "Cmd '%s' done" % self.current["systemcmd"]
			self.current["status"] = self.DONE
			self.current["message"] = "Done."
		else:
			print "Error on cmd '%s' (return code %d)" % (self.current["systemcmd"], result)
			self.current["status"] = self.ERROR
			self.current["message"] = "Error!"
		self.current = None
		self.doCallbacks()
		self.processNextCommand()
		
		
addonstack = AddonsStack()
		
class AddonsScreenHelper(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.timer = eTimer()
		self.timer.callback.append(self.readCategories)
		self.timer.start(200, 1)

	def executeRequest(self):
		api = SAPCL()
		self.categories = api.getCategories(0, True)
		os.system("opkg update")
		rows = os.popen("opkg list_upgradable").read().strip().split("\n")
		self.upgrades = []
		for row in rows:
			tmp = row.split(" - ")
			if len(tmp) == 3:
				self.upgrades.append({
					"package": tmp[0],
					"oldversion": tmp[1],
					"newversion": tmp[2]
				})
		return True

	def executeRequestCallback(self, result):
		if result:
			self.session.open(Addons, self.categories, self.upgrades)
		self.close()

	def readCategories(self):
		self.session.openWithCallback(self.executeRequestCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequest)

class Addons(Screen):
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
			"green": self.feeds
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
		return api.getPackages(self.categories["categories"][self.index]["id"], config.sifteam.addons_packages_sort.value)

	def executeRequestPackagesCallback(self, result):
		self.session.open(AddonsPackages, result, self.categories["categories"][self.index]["name"], self.categories["categories"][self.index]["id"])
		
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
			
		if len(self.cachelist) == index + 1:
			self.session.open(AddonsFileBrowser)
			return
				
		if len(self.upgrades) > 0:
			if index == 0:
				self.session.open(AddonsUpgrades, self.upgrades)
				return
				
			index -= 1
			
		if index == 0:
			print "top 10 rate"
			#self.session.open(AddonsUpgrades, self.upgrades)
			return
				
		index -= 1
		
		if index == 0:
			print "top 10 download"
			#self.session.open(AddonsUpgrades, self.upgrades)
			return
				
		index -= 1
		
		self.index = index
		self.session.openWithCallback(self.executeRequestPackagesCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequestPackages)
		
	def feeds(self):
		self.session.open(AddonsFeeds)
		
	def status(self):
		self.session.open(AddonsStatus)
		
	def quit(self):
		self.close()
		
class AddonsStatus(Screen):
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
		
		addonstack.callbacks.append(self.renderList)
		self.renderList()
		
	def renderList(self):
		self.cachelist = []
		
		for cmd in addonstack.stack:
			name = ""
			if cmd["cmd"] == AddonsStack.INSTALL:
				name = "Install " + cmd["package"]
			elif cmd["cmd"] == AddonsStack.REMOVE:
				name = "Remove " + cmd["package"]
			elif cmd["cmd"] == AddonsStack.DOWNLOAD:
				name = "Download " + cmd["package"]
			elif cmd["cmd"] == AddonsStack.UPGRADE:
				name = "Upgrading system"
				
			
			self.cachelist.append(StatusEntry(name, cmd["message"], cmd["status"] == AddonsStack.DONE, cmd["status"] == AddonsStack.ERROR))
			
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
		addonstack.clear()
		self.renderList()
		
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
			
		self.session.open(AddonsLog, addonstack.stack[index])
		
	def quit(self):
		addonstack.callbacks.remove(self.renderList)
		self.close()
		
class AddonsLog(Screen):
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
		
		addonstack.callbacks.append(self.updatelog)
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
		addonstack.callbacks.remove(self.updatelog)
		self.close()
		
class AddonsFeeds(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.session = session
		self.cachelist = []
		self.feeds = sorted(os.listdir("/var/lib/opkg"))
		
		self['list'] = List([])
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.quit,
			"ok": self.ok
		}, -2)
		
		self.renderList()
		
	def renderList(self):
		self.cachelist = []
		for feed in self.feeds:
			self.cachelist.append(CategoryEntry(feed, "folder.png", ""))
			
		self["list"].setList(self.cachelist)
	
	def readFeed(self):
		self.packages = []
		
		feed = open("/var/lib/opkg/" + self.feeds[self.index], "r")
		pkgstmp = feed.read().split("\n\n")
		for pkgtmp in pkgstmp:
			package = {}
			rowstmp = pkgtmp.strip().split("\n")
			for rowtmp in rowstmp:
				if len(rowtmp) == 0:
					continue
				tmp = rowtmp.split(":")
				tmp.reverse()
				name = tmp.pop().lower()
				tmp.reverse()
				value = ":".join(tmp).strip()
				package[name] = value
				
			if len(package) == 0:
				continue
				
			package["name"] = package["package"]
			if "section" not in package.keys() or len(package["section"]) == 0:
				package["category"] = "Unknown"
			else:
				package["category"] = package["section"]
				
			self.packages.append(package)
				
		feed.close()
		return {
			"result": True,
			"message": "",
			"packages": sorted(self.packages, key=lambda k: k['name']) 
		}
		
	def readFeedCallback(self, result):
		self.session.open(AddonsPackages, result, self.feeds[self.index])
	
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		self.index = index
		self.session.openWithCallback(self.readFeedCallback, ExtraActionBox, _("Reading local feed..."), "Software Manager", self.readFeed)
		
	def quit(self):
		self.close()
		
class AddonsPackages(Screen):
	def __init__(self, session, packages, categoryname, categoryid=-1):
		Screen.__init__(self, session)
		
		self.categoryid = categoryid
		self.categoryname = categoryname
		self.session = session
		self.packages = packages
		self.cachelist = []
		self.index = 0
		
		self['list'] = List([])
		self["list"].onSelectionChanged.append(self.selectionChanged)
		if categoryid == -1:
			self["key_green"] = Button("")
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
		addonstack.callbacks.append(self.renderList)
		
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
			inprogress = addonstack.checkIfPending(package["package"])
			
			if inprogress:
				message = addonstack.getMessage(package["package"])
			else:
				message = package["description"]
				
			self.cachelist.append(PackageEntry(package["name"], installed, rank, message, inprogress, ratings))
			
		self["list"].setList(self.cachelist)
		self["list"].setIndex(self.index)
		self.selectionChanged()
		
	def executeRequestPackages(self):
		api = SAPCL()
		self.packages = api.getPackages(self.categoryid, config.sifteam.addons_packages_sort.value)

	def executeRequestPackagesCallback(self, result):
		self.renderList()
	
	def selectionChanged(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		if addonstack.checkIfPending(self.packages["packages"][index]["package"]):
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
		self.session.openWithCallback(self.rankCallback, AddonsRank, self.packages["packages"][index])
		
	def sortCallback(self):
		self.session.openWithCallback(self.executeRequestPackagesCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequestPackages)
		
	def sort(self):
		if self.categoryid == -1:
			return
			
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
			
		self.index = index
		self.session.openWithCallback(self.sortCallback, AddonsSort)
		
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		self.index = index
		self.session.open(AddonsPackage, self.packages, index, self.categoryid)
		
	def install(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
			
		if addonstack.checkIfPending(self.packages["packages"][index]["package"]):
			return
			
		if fileExists("/usr/lib/opkg/info/%s.control" % self.packages["packages"][index]["package"]):
			addonstack.add(AddonsStack.REMOVE, self.packages["packages"][index]["package"])
		else:
			addonstack.add(AddonsStack.INSTALL, self.packages["packages"][index]["package"])
			
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
			self.session.open(AddonsScreenshot, self.packages["packages"][index])
		
	def quit(self):
		addonstack.callbacks.remove(self.renderList)
		self.close()
		

class AddonsPackage(Screen):
	def __init__(self, session, packages, packageindex, categoryid=-1):
		Screen.__init__(self, session)
		
		self.categoryid = categoryid
		self.session = session
		self.packages = packages
		self.packageindex = packageindex
		self.package = packages["packages"][packageindex]
		
		if categoryid == -1:
			self["key_green"] = Button("")
		else:
			self["key_green"] = Button(_("Rank"))
			
		if fileExists("/usr/lib/opkg/info/%s.control" % packages["packages"][packageindex]["package"]):
			self["key_red"] = Button(_("Remove"))
		else:
			self["key_red"] = Button(_("Install"))
			
		self["key_yellow"] = Button(_("Download"))
		self["key_blue"] = Button("")
		self["title"] = Label("")
		self["rating"] = Label("")
		self["label"] = Label("")
		self["description"] = Label("")
		self["star1"] = Pixmap()
		self["star2"] = Pixmap()
		self["star3"] = Pixmap()
		self["star4"] = Pixmap()
		self["star5"] = Pixmap()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.quit,
			"green": self.rank,
			"red": self.install,
			"yellow": self.download,
			"blue": self.screenshot
		}, -2)
		
		addonstack.callbacks.append(self.renderInfo)
		self.timer = eTimer()
		self.timer.callback.append(self.renderInfo)
		self.timer.start(200, 1)
		
		self.onLayoutFinish.append(self.layoutFinished)
		
	def layoutFinished(self):
		self.setTitle("Software Manager - Package - %s" % self.package["name"])
			
	def renderInfo(self):
		frank = 0.0
		if "rank" in self.package.keys():
			frank = float(self.package["rank"])
		
		rank = int(frank)
		if rank < 1:
			self["star1"].instance.setPixmap(LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star_disabled.png")))
		else:
			self["star1"].instance.setPixmap(LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star.png")))
		if rank < 2:
			self["star2"].instance.setPixmap(LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star_disabled.png")))
		else:
			self["star2"].instance.setPixmap(LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star.png")))
		if rank < 3:
			self["star3"].instance.setPixmap(LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star_disabled.png")))
		else:
			self["star3"].instance.setPixmap(LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star.png")))
		if rank < 4:
			self["star4"].instance.setPixmap(LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star_disabled.png")))
		else:
			self["star4"].instance.setPixmap(LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star.png")))
		if rank < 5:
			self["star5"].instance.setPixmap(LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star_disabled.png")))
		else:
			self["star5"].instance.setPixmap(LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star.png")))
		
		if addonstack.checkIfPending(self.package["package"]):
			message = addonstack.getMessage(self.package["package"])
		else:
			if fileExists("/usr/lib/opkg/info/%s.control" % self.package["package"]):
				message = "Status: installed"
			else:
				message = "Status: not installed"
			
		ratings = 0
		if "ratings" in self.package.keys():
			ratings = int(self.package["ratings"])
			
		self["title"].setText(self.package["name"])
		self["label"].setText(message)
		self["rating"].setText("Ranked %d times, score %.1f" % (ratings, frank))
		self["description"].setText(self.package["description"])
		
		screenshot = None
		if "screenshot" in self.package.keys():
			screenshot = self.package["screenshot"]
		
		if screenshot:
			self["key_blue"].setText(_("Screenshot"))
		
	def executeRequestPackages(self):
		api = SAPCL()
		packages = api.getPackages(self.categoryid, config.sifteam.addons_packages_sort.value)
		for package in packages["packages"]:
			if package["package"] == self.package["package"]:
				self.package["rank"] = package["rank"]

	def executeRequestPackagesCallback(self, result):
		self.renderInfo()
		
	def rankCallback(self):
		self.session.openWithCallback(self.executeRequestPackagesCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequestPackages)
		
	def rank(self):
		if self.categoryid == -1:
			return
			
		self.session.openWithCallback(self.rankCallback, AddonsRank, self.package)
		
	def install(self):
		if addonstack.checkIfPending(self.package["package"]):
			return
			
		if fileExists("/usr/lib/opkg/info/%s.control" % self.package["package"]):
			addonstack.add(AddonsStack.REMOVE, self.package["package"])
		else:
			addonstack.add(AddonsStack.INSTALL, self.package["package"])
			
		self.renderInfo()
		
	def download(self):
		addonstack.add(AddonsStack.DOWNLOAD, self.package["package"])
		self.renderInfo()
		
	def screenshot(self):
		screenshot = None
		if "screenshot" in self.package.keys():
			screenshot = self.package["screenshot"]
		
		self.session.open(AddonsScreenshot, self.package)
		
	def quit(self):
		addonstack.callbacks.remove(self.renderInfo)
		self.close()
		
class AddonsScreenshot(Screen):
	def __init__(self, session, package):
		Screen.__init__(self, session)
		
		self.package = package
		self.session = session

		self["screenshot"] = Pixmap()
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.close
		}, -2)
		
		self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.paintScreenshotPixmapCB)
		
		self.timer = eTimer()
		self.timer.callback.append(self.getPreview)
		self.timer.start(200, 1)
		
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle("Software Manager - Screenshot - %s" % self.package["name"])
		
	def getPreview(self):
		try:
			f = urllib.urlopen(self.package["screenshot"])
			data = f.read()
			f.close()
			tmp = self.package["screenshot"].split(".")
			localfile = "/tmp/preview.%s" % tmp[len(tmp)-1]
			f2 = open(localfile , "w")
			f2.write(data)
			f2.close()
			sc = AVSwitch().getFramebufferScale()
			self.picload.setPara((self["screenshot"].instance.size().width(), self["screenshot"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
			self.picload.startDecode(localfile)
		except ex:
			print ex
			
	def paintScreenshotPixmapCB(self, picInfo=None):
		ptr = self.picload.getData()
		if ptr != None:
			self["screenshot"].instance.setPixmap(ptr.__deref__())
			self["screenshot"].show()
		
class AddonsRank(Screen):
	def __init__(self, session, package):
		Screen.__init__(self, session)
		
		self.session = session
		self.package = package
		self.cachelist = []
		
		self['list'] = List([])
		self["text"] = Label("Rank the application %s" % package["name"])
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
		
		self.onLayoutFinish.append(self.layoutFinished)
		
	def layoutFinished(self):
		self.setTitle("Software Manager - Rank - %s" % self.package["name"])
		
	def renderList(self):
		self.cachelist = []
		self.cachelist.append(RankEntry(0.0, "Really bad"))
		self.cachelist.append(RankEntry(1.0, "Can do better"))
		self.cachelist.append(RankEntry(2.0, "Sufficient"))
		self.cachelist.append(RankEntry(3.0, "Good"))
		self.cachelist.append(RankEntry(4.0, "Very good"))
		self.cachelist.append(RankEntry(5.0, "Excellent"))
		self["list"].setList(self.cachelist)
	
	def rank(self):
		id = -1
		try:
			id = int(self.package["id"])
		except Exception, e:
			pass
			
		api = SAPCL()
		return api.rank(id, self.index)
		
	def rankCallback(self, result):
		if result["result"]:
			self.session.open(MessageBox, _("Thanks for your rank!"), MessageBox.TYPE_INFO, 3)
		else:
			self.session.open(MessageBox, _(result["message"]), MessageBox.TYPE_ERROR)
		self.quit()
		
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		self.index = index
		self.session.openWithCallback(self.rankCallback, ExtraActionBox, _("Ranking %s...") % self.package["name"], "Software Manager", self.rank)
		
	def quit(self):
		self.close()
		
class AddonsSort(Screen):
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
		
class AddonsUpgrades(Screen):
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

class AddonsFileBrowser(Screen):

	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["filelist"] = FileList("/tmp", matchingPattern = "(?i)^.*\.(ipk|tar\.gz|tgz)")
		
		self["FilelistActions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"ok": self.ok,
				"cancel": self.exit
			})
			
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		
		self.onLayoutFinish.append(self.layoutFinished)
		
	def layoutFinished(self):
		self.setTitle("%s - %s" % ("Software Manager - file browser", "/tmp"))
		
	def tgz(self):
		self.tgzret = os.system("tar zxf \"%s\" -C /" % self.filename)
		
	def ok(self):
		if self["filelist"].canDescent(): # isDir
			self["filelist"].descent()
			self.setTitle("%s - %s" % ("Software Manager - file browser", self["filelist"].getCurrentDirectory()))
		else:
			filename = self["filelist"].getCurrentDirectory() + '/' + self["filelist"].getFilename()
			if filename[-3:] == "ipk":
				addonstack.add(AddonsStack.INSTALL, filename)
				self.session.open(AddonsStatus)
				self.close()
			else:
				self.filename = filename
				self.session.openWithCallback(self.tgzexit, ExtraActionBox, "Deflating %s to /" % self["filelist"].getFilename(), "Addons install tgz", self.tgz)
			
	def tgzexit(self, result):
		if self.tgzret == 0:
			self.session.open(MessageBox, _("Package installed succesfully"), MessageBox.TYPE_INFO)
		else:
			self.session.open(MessageBox, _("Error installing package"), MessageBox.TYPE_ERROR)
		self.close()
		
	def exit(self):
		self.close()
		
class AutoUpdates():
	def __init__(self, session):
		self.session = session
		
		self.updatestimer = eTimer()
		self.updatestimer.callback.append(self.checkupdates)
		self.updatestimer.start(60*1000, 1)	# on init 1 minute delay
		
	def upgrade(self):
			print "[Automatic Updates] system upgraded"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)

	def messageboxCallback(self, ret):
		if ret == 0:
			self.upgrade()
		elif ret == 1:
			config.sifteam.autoupdates.value = "auto"
			config.sifteam.autoupdates.save()
			self.upgrade()
		elif ret == 2:
			print "[Automatic Updates] disabled by user"
			config.sifteam.autoupdates.value = "disabled"
			config.sifteam.autoupdates.save()
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)
		else:
			print "[Automatic Updates] install later"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)

	def checkupdates(self):
		if config.sifteam.autoupdates.value == "disabled":
			print "[Automatic Updates] disabled by user"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)
			return
			
		if len(self.session.dialog_stack) > 0:
			print "[Automatic Updates] osd busy"
			print "[Automatic Updates] rescheduled in 10 minutes"
			self.updatestimer.start(10*60*1000, 1)
			return

		if self.session.nav.RecordTimer.isRecording():
			print "[Automatic Updates] record in progress"
			print "[Automatic Updates] rescheduled in 1 hour"
			self.updatestimer.start(1*60*60*1000, 1)
			return

		print "[Automatic Updates] updating feeds..."
		os.system("opkg update")
		print "[Automatic Updates] feeds updated"
		
		rows = os.popen("opkg list_upgradable").read().strip().split("\n")
		self.upgrades = []
		for row in rows:
			tmp = row.split(" - ")
			if len(tmp) == 3:
				self.upgrades.append({
					"package": tmp[0],
					"oldversion": tmp[1],
					"newversion": tmp[2]
				})
				
		if len(self.upgrades) == 0:
			print "[Automatic Updates] no updates found"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)
			return
			
		print "[Automatic Updates] updates found"
		if config.sifteam.autoupdates.value == "auto":
			self.upgrade()
		else:
			self.session.openWithCallback(self.messageboxCallback, ExtraMessageBox, "", "New updates found",
										[ [ "Install updates now", "install_now.png" ],
										[ "Always install automatically all updates", "install_auto.png" ],
										[ "Disable automatic updates", "install_disable.png" ],
										[ "Ask later", "install_later.png" ],
										], 1, 3)
		
			
# helper for start autoupdates on mytest init
autoupdates = None
def startAutomatiUpdates(session):
	global autoupdates
	autoupdates = AutoUpdates(session)
