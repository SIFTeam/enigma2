from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists
from Tools.LoadPixmap import LoadPixmap

from SIFTeam.Extra.SAPCL import SAPCL
from SIFTeam.Extra.ExtraActionBox import ExtraActionBox
from Packages import SMPackages

import os

def CategoryEntry(name, picture, count):
	pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/" + picture))
	if not pixmap:
		pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/folder.png"))
		
	return (pixmap, name, count)

class SMFeeds(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.session = session
		self.cachelist = []
		try:
			self.feeds = sorted(os.listdir("/var/lib/opkg/lists"))
			self.feedspath = "/var/lib/opkg/lists"
		except Exception, e:
			self.feeds = sorted(os.listdir("/var/lib/opkg"))
			self.feedspath = "/var/lib/opkg"
		
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
		
		feed = open(self.feedspath + "/" + self.feeds[self.index], "r")
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
				
			if "package" not in package:
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
		self.session.open(SMPackages, result, self.feeds[self.index])
	
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