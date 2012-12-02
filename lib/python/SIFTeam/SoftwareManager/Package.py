from enigma import *
from Screens.Screen import Screen
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists
from Tools.LoadPixmap import LoadPixmap

from SIFTeam.Extra.SAPCL import SAPCL
from SIFTeam.Extra.ExtraActionBox import ExtraActionBox
from Rank import SMRank
from Stack import SMStack, smstack
from Screenshot import SMScreenshot

class SMPackage(Screen):
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
			
		if fileExists("/var/lib/opkg/info/%s.control" % packages["packages"][packageindex]["package"]):
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
		
		smstack.callbacks.append(self.renderInfo)
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
		
		if smstack.checkIfPending(self.package["package"]):
			message = smstack.getMessage(self.package["package"])
		else:
			if fileExists("/var/lib/opkg/info/%s.control" % self.package["package"]):
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
			
		self.session.openWithCallback(self.rankCallback, SMRank, self.package)
		
	def install(self):
		if smstack.checkIfPending(self.package["package"]):
			return
			
		if fileExists("/var/lib/opkg/info/%s.control" % self.package["package"]):
			smstack.add(SMStack.REMOVE, self.package["package"])
		else:
			smstack.add(SMStack.INSTALL, self.package["package"])
			
		self.renderInfo()
		
	def download(self):
		smstack.add(SMStack.DOWNLOAD, self.package["package"])
		self.renderInfo()
		
	def screenshot(self):
		screenshot = None
		if "screenshot" in self.package.keys():
			screenshot = self.package["screenshot"]
		
		self.session.open(SMScreenshot, self.package)
		
	def quit(self):
		smstack.callbacks.remove(self.renderInfo)
		self.close()