from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest

from PanelConfig import MenuConfig, PanelExec

from Extra.ExtraMessageBox import ExtraMessageBox

class Panel(Screen):
	def __init__(self, session, servicelist):
		Screen.__init__(self, session)
		self.servicelist = servicelist
		self.session = session
		self.drawList = []
		self.listindex = 0
		
		self['menu'] = List(self.drawList)
		self["actions"] = ActionMap(["SetupActions"],
		{
			"ok": self.ok,
			"cancel": self.quit,
		}, -2)
		
		self.load()
		
	def load(self, arg = None):
		config = MenuConfig()
		config.load()
		self.cacheList = config.items
		self.draw()
		
	def draw(self):
		self.drawList = []
		for item in self.cacheList:
			pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_panel/" + item[1] + ".png"));
			if not pixmap:
				pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/empty.png"));
			self.drawList.append((pixmap, _(item[2])))
		self['menu'].setList(self.drawList)
		if self.listindex < len(self.drawList):
			self["menu"].setIndex(self.listindex)
			
	def ok(self):
		if len(self.cacheList) == 0:
			return
			
		index = self['menu'].getIndex()
		self.listindex = index
		panelexec = PanelExec(self.session)
		if self.cacheList[index][0] == "menu":
			panelexec.runMenu(self.cacheList[index][1], self.load)
		elif self.cacheList[index][0] == "plugins":
			panelexec.runPlugin(self.cacheList[index][1])
		elif self.cacheList[index][0] == "extensions":
			panelexec.runExtension(self.cacheList[index][1], self.servicelist)
		
	def quit(self):
		self.close()
