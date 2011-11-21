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
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap

from Extra.ExtraMessageBox import ExtraMessageBox
from Extra.ExtraActionBox import ExtraActionBox
from Extra.SAPCL import SAPCL

#import libsif
import re
import os
import urllib

ipkg = None #libsif.Ipkg()
addons_loaded = False

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
	pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/" + picture));
	if not pixmap:
		pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/folder.png"));
		
	return (pixmap, name, count)

def UpgradeEntry(name, oldversion, newversion):
	pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/install_now.png"));
		
	return (pixmap, name, oldversion, ">", newversion)
	
def PackageEntry(name, installed, rank):
	rank = int(round(rank, 0))
	star = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star.png"));
	star_disabled = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star_disabled.png"));
	
	if installed:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"));
	else:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_off.png"));
		
	if rank == 1:
		return (picture, name, star, star_disabled, star_disabled, star_disabled, star_disabled)
	elif rank == 2:
		return (picture, name, star, star, star_disabled, star_disabled, star_disabled)
	elif rank == 3:
		return (picture, name, star, star, star, star_disabled, star_disabled)
	elif rank == 4:
		return (picture, name, star, star, star, star, star_disabled)
	elif rank == 5:
		return (picture, name, star, star, star, star, star)
		
	return (picture, name, star_disabled, star_disabled, star_disabled, star_disabled, star_disabled)

def RankEntry(rank, description):
	rank = int(round(rank, 0))
	star = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star.png"));
	star_disabled = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/star_disabled.png"));
	
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
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button(_("All"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
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
		
		for category in self.categories["categories"]:
			if category["packages"] == 1:
				pkgcount = "1 package"
			else:
				pkgcount = "%d packages" % category["packages"]
			if category["description"]:
				self.cachelist.append(CategoryEntry(category["description"], category["identifier"] + ".png", pkgcount))
			else:
				self.cachelist.append(CategoryEntry(category["name"], category["identifier"] + ".png", pkgcount))
			
		self["list"].setList(self.cachelist)
	
	def executeRequestPackages(self):
		api = SAPCL()
		return api.getPackages(self.categories["categories"][self.index]["id"])

	def executeRequestPackagesCallback(self, result):
		self.session.open(AddonsPackages, result)
		
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		if len(self.upgrades) > 0:
			if index == 0:
				self.session.open(AddonsUpgrades, self.upgrades)
				return
				
			index -= 1
		
		self.index = index
		self.session.openWithCallback(self.executeRequestPackagesCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequestPackages)
		
	def feeds(self):
		self.session.open(AddonsFeeds)
		
	def quit(self):
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
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
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
		self.session.open(AddonsPackages, result)
	
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
	def __init__(self, session, packages):
		Screen.__init__(self, session)
		
		self.session = session
		self.packages = packages
		self.cachelist = []
		
		self['list'] = List([])
		self["list"].onSelectionChanged.append(self.selectionChanged)
		self["key_green"] = Button(_("Rank"))
		self["key_red"] = Button(_("Install"))
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button(_("Sort"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"cancel": self.quit,
			"ok": self.ok,
			"green": self.rank
		}, -2)
		
		self.renderList()
	
	def renderList(self):
		self.cachelist = []
		
		for package in self.packages["packages"]:
			rank = 0.0
			if "rank" in package.keys():
				rank = float(package["rank"])
				
			self.cachelist.append(PackageEntry(package["name"], True, rank))
			
		self["list"].setList(self.cachelist)
		self.selectionChanged()
		
	def selectionChanged(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
		#print self.packages["packages"][index]["screenshot"]
		#	index = self["list"].getIndex()
	
	def rank(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
			
		self.session.open(AddonsRank, self.packages["packages"][index])
		#self.index = index
		#self.session.openWithCallback(self.doRank, ExtraMessageBox, "Please rank the application " + self.packages["packages"][index]["name"],
		#							"Rank an application!",
		#							[ [ "Really bad", "star0.png" ],
		#							[ "Can do better", "star1.png" ],
		#							[ "Sufficient", "star2.png" ],
		#							[ "Good", "star3.png" ],
		#							[ "Very good", "star4.png" ],
		#							[ "Excellent", "star5.png" ],
		#							])
		
		
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
	def quit(self):
		self.close()
		
class AddonsRank(Screen):
	def __init__(self, session, package):
		Screen.__init__(self, session)
		
		self.session = session
		self.package = package
		self.cachelist = []
		
		self['list'] = List([])
		self["key_green"] = Button()
		self["key_red"] = Button("")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"cancel": self.quit,
			"ok": self.ok
		}, -2)
		
		self.renderList()
		
	def renderList(self):
		self.cachelist = []
		self.cachelist.append(RankEntry(0.0, "Really bad"))
		self.cachelist.append(RankEntry(1.0, "Can do better"))
		self.cachelist.append(RankEntry(2.0, "Sufficient"))
		self.cachelist.append(RankEntry(3.0, "Good"))
		self.cachelist.append(RankEntry(4.0, "Very good"))
		self.cachelist.append(RankEntry(5.0, "Excellent"))
		self["list"].setList(self.cachelist)
	
	def ok(self):
		if len(self.cachelist) == 0:
			return
			
		index = self["list"].getIndex()
		if index == None:
			index = 0
		
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
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
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

class AddonsPreview(Screen):
	def __init__(self, session, package):
		Screen.__init__(self, session)
		
		self.package = package
		self.session = session
		self.index = 0

		self["Preview"] = Pixmap()
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"red": self.previous,
			"green": self.next,
			"blue": self.close,
			"cancel": self.close,
		}, -2)
		
		self.timer = eTimer()
		self.timer.callback.append(self.getPreview)
		self.timer.start(200, 1)
		
	
	def getFileNameByIndex(self, index):
		if index == 0:
			return self.package.previewimage1
		elif index == 1:
			return self.package.previewimage2
		elif index == 2:
			return self.package.previewimage3
		elif index == 3:
			return self.package.previewimage4
		elif index == 4:
			return self.package.previewimage5
			
	def checkPreviewExistByIndex(self, index):
		if len(self.getFileNameByIndex(index)) > 0:
			return True
		return False
		
	def countPreview(self):
		count = 0
		for i in range (0, 5):
			if not self.checkPreviewExistByIndex(i):
				return count
				
			count += 1
			
		return count
		
	def previous(self):
		if self.index > 0:
			self.index -= 1
			self.getPreview()
	
	def next(self):
		if self.index < self.countPreview()-1:
			self.index += 1
			self.getPreview()
	
	def getPreview(self):
		try:
			f = urllib.urlopen(self.getFileNameByIndex(self.index))
			data = f.read()
			f.close()
			tmp = self.package.previewimage1.split(".")
			localfile = "/tmp/preview.%s" % tmp[len(tmp)-1]
			f2 = open(localfile , "w")
			f2.write(data)
			f2.close()
			self["Preview"].instance.setPixmapFromFile(localfile)
		except ex:
			pass
		
		if self.index > 0:
			self["key_red"].setText(_("Previous"))
		else:
			self["key_red"].setText("")
			
		if self.index < self.countPreview()-1:
			self["key_green"].setText(_("Next"))
		else:
			self["key_green"].setText("")

class AddonsAction(Screen):
	IPKG_UPDATE = 0
	IPKG_UPGRADE = 1
	IPKG_INSTALL = 2
	IPKG_REMOVE = 3
	IPKG_DOWNLOAD = 4
	
	SMALL_VIEW = 0
	LARGE_VIEW = 1
	
	def __init__(self, session, action, pause = False, arg = None):
		Screen.__init__(self, session)
		
		self.session = session
		self.canexit = False
		self.pause = False #pause
		self.showed = False
		self.status = self.SMALL_VIEW
		self.action = action
		self.arg = arg
		self.errors = False
		
		ipkg.setPyProgressCallback(self.progress)
		ipkg.setPyNoticeCallback(self.notice)
		ipkg.setPyErrorCallback(self.error)
		ipkg.setPyEndCallback(self.end)
		self["text"] = ScrollLabel("")
		self["textrow"] = Label("")
		self["info"] = Label(_("Press OK for extended view"))
		self["progress"] = ProgressBar()
		self["progress2"] = ProgressBar()
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
		{
			"up": self.pageup,
			"down": self.pagedown,
			"ok": self.ok,
		}, -2)
		
		self.onShow.append(self.__onShow)
		
		self.quittimer = eTimer()
		self.quittimer.callback.append(self.quit)

		if action == self.IPKG_UPDATE:
			ipkg.update()
		elif action == self.IPKG_UPGRADE:
			ipkg.upgrade()
		elif action == self.IPKG_INSTALL:
			ipkg.install(arg)
		elif action == self.IPKG_REMOVE:
			ipkg.remove(arg)
		elif action == self.IPKG_DOWNLOAD:
			ipkg.download(arg)
		
		self.onLayoutFinish.append(self.layoutFinished)
		
	def layoutFinished(self):
		if self.action == self.IPKG_UPDATE:
			self.setTitle(_("Software Manager - repo update"))
		elif self.action == self.IPKG_UPGRADE:
			self.setTitle(_("Software Manager - upgrade"))
		elif self.action == self.IPKG_INSTALL:
			self.setTitle(_("Software Manager - install"))
		elif self.action == self.IPKG_REMOVE:
			self.setTitle(_("Software Manager - remove"))
		elif self.action == self.IPKG_DOWNLOAD:
			self.setTitle(_("Software Manager - download"))

		self["textrow"].setText("Initializing")
		self["progress"].setValue(0)
		self["progress2"].setValue(0)

	def __onShow(self):
		if not self.showed:
			self.showed = True
			self.largesize = self.instance.csize()
			tmp = self.instance.size()
			tmp2 = self.instance.position()
			xoffset = tmp2.x() + ((tmp.width() - self.largesize.width()) / 2)
			yoffset = tmp2.y() + ((tmp.height() - self.largesize.height()) / 2)
			self.largepos = ePoint(xoffset, yoffset)
			self.screensize = getDesktop(0).size()
			self.showSlim()
	
	def ok(self):
		if self.canexit:
			self.quit()
			return
			
		if self.status == self.SMALL_VIEW:
			self.showFull()
			self.pause = True
			
	def showSlim(self):
		self.status = self.SMALL_VIEW
		self["progress"].hide()
		self["text"].hide()
		self["info"].show()
		self["progress2"].show()
		self["textrow"].show()
		wsize = (560, 90)
		self.instance.resize(eSize(*wsize))
		self.instance.move(ePoint((self.screensize.width()-wsize[0])/2, (self.screensize.height()-wsize[1])/2))
		
	def showFull(self):
		self.status = self.LARGE_VIEW
		self["progress"].show()
		self["text"].show()
		self["info"].hide()
		self["progress2"].hide()
		self["textrow"].hide()
		self.instance.resize(self.largesize)
		self.instance.move(self.largepos)
		
	def pageup(self):
		self["text"].pageUp()
		
	def pagedown(self):
		self["text"].pageDown()
		
	def appendText(self, text):
		str = self["text"].getText()
		str += text;
		self["text"].setText(str)
		self["textrow"].setText(text.strip())
			
	def progress(self, total, now):
		if total > 0:
			self["progress"].setValue(int(now*(100/total)))
			self["progress2"].setValue(int(now*(100/total)))
		else:
			self["progress"].setValue(0)
			self["progress2"].setValue(0)
		return 0
	
	def notice(self, message):
		self.appendText(message)

	def error(self, message):
		self.errors = True
		self.pause = True
		self.appendText("ERROR: %s" % message)
		self.session.open(MessageBox, message, MessageBox.TYPE_ERROR)
			
	def end(self, ret):
		ipkg.clearCallbacks();
		self.canexit = True
		if self.pause:
			self.showFull()
			self.appendText("Press OK to continue")
			self["text"].lastPage()
		else:
			self["text"].lastPage()
			if self.action == self.IPKG_UPDATE:
				self.quittimer.start(100, 1)
			else:
				self.quittimer.start(2000, 1)
			
	def reboot(self, result):
		if result == 0:
			from Screens.Standby import TryQuitMainloop
			self.session.open(TryQuitMainloop, 2)

		self.close()

	def quit(self):
		if self.canexit:
			if self.action == self.IPKG_UPGRADE and self.errors == False:
				self.session.openWithCallback(self.reboot, ExtraMessageBox, "A reboot is suggested", "Upgrade completed",
											[ [ "Reboot now", "reboot.png" ],
											[ "Reboot manually later", "cancel.png" ],
											], 1, 1, 0, 10)
			elif self.action == self.IPKG_INSTALL or self.action == self.IPKG_REMOVE:
				plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
				self.close()
			else:
				self.close()
		
class AddonsFileBrowser(Screen):

	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["filelist"] = FileList("/tmp", matchingPattern = "(?i)^.*\.(ipk|tar\.gz|tgz)")
		
		self["FilelistActions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"ok": self.ok,
				"red": self.ok,
				"cancel": self.exit,
				"blue": self.exit
			})
			
		self["key_green"] = Button("")
		self["key_red"] = Button(_("OK"))
		self["key_blue"] = Button(_("Exit"))
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
				print filename
				self.session.openWithCallback(self.exit, AddonsAction, AddonsAction.IPKG_INSTALL, True, filename)
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
		
		self.updatesipkg = libsif.Ipkg() # we get a second instance to prevent problems with simultaneos actions
		self.updatesipkg.setPyEndCallback(self.end)
		self.updatesipkg.setPyProgressCallback(self.progress)
		self.updatesipkg.setPyNoticeCallback(self.notice)
		self.updatesipkg.setPyErrorCallback(self.error)

		self.updatestimer = eTimer()
		self.updatestimer.callback.append(self.checkupdates)
		self.updatestimer.start(60*1000, 1)	# on init 1 minute delay
		
	def upgraded(self):
			print "[Automatic Updates] system upgraded"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)

	def messageboxCallback(self, ret):
		if ret == 0:
			self.session.openWithCallback(self.upgraded, AddonsAction, AddonsAction.IPKG_UPGRADE, True)
		elif ret == 1:
			config.sifteam.autoupdates.value = "auto"
			self.session.openWithCallback(self.upgraded, AddonsAction, AddonsAction.IPKG_UPGRADE, True)
		elif ret == 2:
			print "[Automatic Updates] disabled by user"
			config.sifteam.autoupdates.value = "disabled"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)
		else:
			print "[Automatic Updates] install later"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)

	def progress(self, total, now):
		pass
	
	def notice(self, message):
		print "[Automatic Updates] " + message.strip()

	def error(self, message):
		print "[Automatic Updates] ERROR: " + message.strip()

	def end(self, ret):
		print "[Automatic Updates] feeds updated"
		if self.updatesipkg.isUpgradeable() == 1:
			print "[Automatic Updates] updates found"
			if config.sifteam.autoupdates.value == "auto":
				pass
			else:
				self.session.openWithCallback(self.messageboxCallback, ExtraMessageBox, "", "New updates found",
											[ [ "Install updates now", "install_now.png" ],
											[ "Always install automatically all updates", "install_auto.png" ],
											[ "Disable automatic updates", "install_disable.png" ],
											[ "Ask later", "install_later.png" ],
											], 1, 3)
		else:
			print "[Automatic Updates] no updates found"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)

	def checkupdates(self):
		global addons_loaded
		if addons_loaded or len(self.session.dialog_stack) > 0:
			print "[Automatic Updates] osd busy"
			print "[Automatic Updates] rescheduled in 10 minutes"
			self.updatestimer.start(10*60*1000, 1)
			return

		if self.session.nav.RecordTimer.isRecording():
			print "[Automatic Updates] record in progress"
			print "[Automatic Updates] rescheduled in 1 hour"
			self.updatestimer.start(1*60*60*1000, 1)
			return

		from Screens.Standby import inStandby
		if inStandby != None:
			print "[Automatic Updates] decoder in standby"
			print "[Automatic Updates] rescheduled in 1 hour"
			self.updatestimer.start(1*60*60*1000, 1)
			return

		if config.sifteam.autoupdates.value == "disabled":
			print "[Automatic Updates] disabled by user"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)
			return

		print "[Automatic Updates] updating feeds..."
		self.updatesipkg.update()

# helper for start autoupdates on mytest init
autoupdates = None
def startAutomatiUpdates(session):
	global autoupdates
	autoupdates = AutoUpdates(session)
