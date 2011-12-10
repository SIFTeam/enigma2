from enigma import *
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap

from SIFTeam.Extra.SAPCL import SAPCL
from SIFTeam.Extra.ExtraActionBox import ExtraActionBox

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
	
class SMRank(Screen):
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