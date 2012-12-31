# -*- coding: iso-8859-1 -*-
# (c) 2006 Stephan Reichholf
# This Software is Free, use it where you want, when you want for whatever you want and modify it if you want but don't remove my copyright!
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Plugins.Plugin import PluginDescriptor
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from os import path, walk
from enigma import eEnv

class SkinSelector(Screen):
	# for i18n:
	# _("Choose your Skin")
	skinlist = []
	skincache = []
	skincache_filtered = []
	root = eEnv.resolve("${datadir}/enigma2/")
	parent = ""

	def __init__(self, session, args = None):

		Screen.__init__(self, session)

		self.skincache = []
		self.previewPath = ""
		self.parent = ""
		path.walk(self.root, self.find, "")
		self.countVariants()
		self.fixLabels()
		self.skincache = sorted(self.skincache, key=lambda k: k['label'])
		self.buildSkinList("")

		self["key_red"] = StaticText(_("Close"))
		self["introduction"] = StaticText(_("Press OK to activate the selected skin."))
		self["SkinList"] = MenuList(self.skinlist)
		self["Preview"] = Pixmap()

		self["actions"] = NumberActionMap(["WizardActions", "InputActions", "EPGSelectActions"],
		{
			"ok": self.ok,
			"back": self.back,
			"red": self.back,
			"up": self.up,
			"down": self.down,
			"left": self.left,
			"right": self.right,
			"info": self.info,
		}, -1)

		self.onLayoutFinish.append(self.layoutFinished)

	def incrementeVariantCounter(self, parent):
		for entry in self.skincache:
			if entry["dirname"] == parent:
				entry["variant_count"] += 1
		
	def countVariants(self):
		for entry in self.skincache:
			if entry["parent"] != "":
				self.incrementeVariantCounter(entry["parent"])
		
	def fixLabels(self):
		for entry in self.skincache:
			if entry["variant_count"] > 0:
				entry["label"] = entry["original_label"] + (" (with %d variants)" % entry["variant_count"])
			
	def buildSkinList(self, parent):
		self.skinlist = []
		self.skincache_filtered = []
		for entry in self.skincache:
			if entry["parent"] == parent:
				self.skincache_filtered.append(entry)
				self.skinlist.append(entry["label"])
				
		if parent != "":
			for entry in self.skincache:
				if entry["dirname"] == parent:
					self.skincache_filtered = [entry,] + self.skincache_filtered
					self.skinlist = [entry["original_label"],] + self.skinlist
				
	def layoutFinished(self):
		tmp = config.skin.primary_skin.value.find('/skin.xml')
		if tmp != -1:
			tmp = config.skin.primary_skin.value[:tmp]
			idx = 0
			for skin in self.skinlist:
				if skin == tmp:
					break
				idx += 1
			if idx < len(self.skinlist):
				self["SkinList"].moveToIndex(idx)
		self.loadPreview()

	def up(self):
		self["SkinList"].up()
		self.loadPreview()

	def down(self):
		self["SkinList"].down()
		self.loadPreview()

	def left(self):
		self["SkinList"].pageUp()
		self.loadPreview()

	def right(self):
		self["SkinList"].pageDown()
		self.loadPreview()

	def info(self):
		aboutbox = self.session.open(MessageBox,_("Enigma2 skin selector"), MessageBox.TYPE_INFO)
		aboutbox.setTitle(_("About..."))

	def find(self, arg, dirname, names):
		isSkin = False
		parent = ""
		label = ""
		
		for x in names:
			if x == "skin.xml":
				isSkin = True
			elif x == ".label":
				label = open(dirname + "/.label").read().strip()
			elif x == ".parent":
				parent = open(dirname + "/.parent").read().strip()
				
		if isSkin:
			entry = {}
			entry["dirname"] = dirname[len(self.root):]
			if label == "":
				if dirname <> self.root:
					label = entry["dirname"].replace('_', ' ').title()
				else:
					label = "Default Skin"
			entry["label"] = label
			entry["original_label"] = label
			entry["parent"] = parent
			entry["variant_count"] = 0
			
			self.skincache.append(entry)

	def ok(self):
		index = self["SkinList"].getSelectedIndex()
		if self.parent == "" and self.skincache_filtered[index]["variant_count"] > 0:
			self.setTitle("Skin Selector - %s" % self.skincache_filtered[index]["original_label"])
			self.parent = self.skincache_filtered[index]["dirname"]
			self.buildSkinList(self.parent)
			self["SkinList"].setList(self.skinlist)
			self["SkinList"].moveToIndex(0)
			return
			
		if self.skincache_filtered[index]["dirname"] == "":
			skinfile = "skin.xml"
		else:
			skinfile = self.skincache_filtered[index]["dirname"] + "/skin.xml"

		print "Skinselector: Selected Skin: "+self.root+skinfile
		config.skin.primary_skin.value = skinfile
		config.skin.primary_skin.save()
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply a new skin\nDo you want to restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI now?"))

	def loadPreview(self):
		index = self["SkinList"].getSelectedIndex()
		pngpath = self.root + self.skincache_filtered[index]["dirname"] + "/prev.png"

		if not path.exists(pngpath):
			pngpath = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/SkinSelector/noprev.png")

		if self.previewPath != pngpath:
			self.previewPath = pngpath

		self["Preview"].instance.setPixmapFromFile(self.previewPath)
		
	def back(self):
		if self.parent != "":
			self.setTitle("Skin Selector")
			self.parent = ""
			self.buildSkinList(self.parent)
			self["SkinList"].setList(self.skinlist)
			self["SkinList"].moveToIndex(0)
			return
			
		self.close()
			
	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)

def SkinSelMain(session, **kwargs):
	session.open(SkinSelector)

def SkinSelSetup(menuid, **kwargs):
	if menuid == "system":
		return [(_("Skin"), SkinSelMain, "skin_selector", None)]
	else:
		return []

def Plugins(**kwargs):
	return PluginDescriptor(name="Skinselector", description="Select Your Skin", where = PluginDescriptor.WHERE_MENU, needsRestart = False, fnc=SkinSelSetup)
