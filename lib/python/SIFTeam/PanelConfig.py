from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_SKIN
from Tools.LoadPixmap import LoadPixmap
from Components.config import config
from Components.SystemInfo import SystemInfo
from Components.Button import Button
from Screens.Setup import Setup, getSetupTitle
from Components.PluginComponent import plugins
from Components.PluginList import *
from Plugins.Plugin import PluginDescriptor

from Emulator import Emulator, CardServer
from Scripts import Scripts
from Preferences import Preferences
from About import AboutTeam
from Addons import Addons

from Extra.ExtraMessageBox import ExtraMessageBox

import xml.etree.cElementTree

# some code in this component is copied from enigma2 code

mdom = xml.etree.cElementTree.parse(resolveFilename(SCOPE_SKIN, 'menu.xml'))

class boundFunction:
	def __init__(self, fnc, *args):
		self.fnc = fnc
		self.args = args
	def __call__(self):
		self.fnc(*self.args)

class PanelExec():
	def __init__(self, session):
		self.session = session
		
	def runPlugin(self, name):
		pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
		for plugin in pluginlist:
			x = PluginEntryComponent(plugin)
			if x[1][7] == name:
				x[0](session=self.session)
				return

	def runExtension(self, name, servicelist):
		pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_EXTENSIONSMENU)
		for plugin in pluginlist:
			x = PluginEntryComponent(plugin)
			if x[1][7] == name:
				x[0](session=self.session, servicelist=servicelist)
				return

	def runMenu(self, name, callback):
		self.callback = callback
		ret = self.searchMenu(mdom.getroot(), name)
		if ret is not None:
			ret()

	def execText(self, text):
		exec text

	def runScreen(self, arg):
		if arg[0] != "":
			exec "from " + arg[0] + " import *"
			
		self.openDialog(*eval(arg[1]))

	def openDialog(self, *dialog):				# in every layer needed
		if self.callback is not None:
			self.session.openWithCallback(self.callback, *dialog)
		else:
			self.session.open(*dialog)

	def openSetup(self, dialog):
		if self.callback is not None:
			self.session.openWithCallback(self.callback, Setup, dialog)
		else:
			self.session.open(Setup, dialog)

	def searchMenu(self, parent, name):
		menuID = None
		ret = None
		for x in parent:
			if x.tag == "item":
				requires = x.get("requires")
				if requires:
					if requires[0] == '!':
						if SystemInfo.get(requires[1:], False):
							continue
					elif not SystemInfo.get(requires, False):
						continue

				item_text = x.get("text", "").encode("UTF-8")
				entryID = x.get("entryID", "")

				if entryID == name:
					for z in x:
						if z.tag == 'screen':
							module = z.get("module")
							screen = z.get("screen")

							if screen is None:
								screen = module

							print module, screen
							if module[:7] == "SIFTeam":
								pass	# we don't need any change to module
							elif module:
								module = "Screens." + module
							else:
								module = ""

							# check for arguments. they will be appended to the
							# openDialog call
							args = z.text or ""
							screen += ", " + args

							ret = boundFunction(self.runScreen, (module, screen))
						elif z.tag == 'code':
							ret = boundFunction(self.execText, z.text)
						elif z.tag == 'setup':
							id = z.get("id")
							ret = boundFunction(self.openSetup, id)
							
			elif x.tag == "menu":
				if ret is None:
					ret = self.searchMenu(x, name)
					
			elif x.tag == "id":
				menuID = x.get("val")

		if menuID is not None:
			for l in plugins.getPluginsForMenu(menuID):
				if l[2] == name:
					ret = boundFunction(l[1], self.session)
					
		return ret


class MenuConfig():
	def __init__(self):
		self.filename = "/etc/enigma2/panel.conf"
		self.items = []
		
	def load(self):
		try:
			try:
				f = open(self.filename, "r")
			except:
				f = open("/usr/share/enigma2/defaults/panel.conf", "r")
			
			rows = f.read().split("\n")
			for row in rows:
				tmp = row.split(":")
				if len(tmp) == 3:
					self.items.append([tmp[0], tmp[1], tmp[2]])
			f.close()
			
		except Exception:
			pass
			
	def save(self):
		try:
			f = open(self.filename, "w")
			for item in self.items:
				f.write("%s:%s:%s\n" % (item[0], item[1], item[2]))
			f.close()
			
		except Exception:
			pass
			
	def add(self, category, entryID, name):
		self.items.append([category, entryID, name])
		
class PanelConfig(Screen):
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.session = session
		self.drawList = []
		
		self['menu'] = List(self.drawList)
		self["menu"].onSelectionChanged.append(self.selectionChanged)
		self["key_red"] = Button(_("Add"))
		self["key_green"] = Button("")
		self["key_yellow"] = Button("")
		self["key_blue"] = Button("")
		
		self["actions"] = ActionMap(["ColorActions", "SetupActions"],
		{
			"red": self.add,
			"green": self.remove,
			"yellow": self.moveUp,
			"blue": self.moveDown,
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
		self.selectionChanged()
		
	def selectionChanged(self):
		if len(self.cacheList) > 0:
			self["key_green"].setText(_("Remove"))
			
		index = self['menu'].getIndex()
		if index == 0:
			self["key_yellow"].setText("")
		else:
			self["key_yellow"].setText(_("Move up"))
			
		if index == len(self.cacheList) - 1:
			self["key_blue"].setText("")
		else:
			self["key_blue"].setText(_("Move down"))
			

	def save(self):
		config = MenuConfig()
		config.items = self.cacheList
		config.save()
		
	def add(self):
		self.save()
		self.session.openWithCallback(self.load, PanelConfigAdd)
		
	def remove(self):
		if len(self.cacheList) == 0:
			return
			
		index = self['menu'].getIndex()
		self.cacheList.pop(index)
		self.draw()
	
	def moveUp(self):
		index = self['menu'].getIndex()
		if index > 0:
			tmp = self.cacheList[index-1]
			self.cacheList[index-1] = self.cacheList[index]
			self.cacheList[index] = tmp
			self.draw()
			self["menu"].setCurrentIndex(index - 1)
			
	def moveDown(self):
		index = self['menu'].getIndex()
		if index < len(self.cacheList) - 1:
			tmp = self.cacheList[index+1]
			self.cacheList[index+1] = self.cacheList[index]
			self.cacheList[index] = tmp
			self.draw()
			self["menu"].setCurrentIndex(index + 1)
	
	def quit(self):
		self.save()
		self.close()
	
class PanelConfigAdd(Screen):
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.session = session
		
		self.root = mdom.getroot()
		
		self.drawList = []
		self.cacheList = []
		
		self['menu'] = List(self.drawList)
		self["key_red"] = Button(_("Add"))
		self["key_green"] = Button(_("Menu"))
		self["key_yellow"] = Button(_("Plugins"))
		self["key_blue"] = Button(_("Extensions"))
		
		self["actions"] = ActionMap(["ColorActions", "SetupActions"],
		{
			"red": self.add,
			"green": self.showMenu,
			"yellow": self.showPlugins,
			"blue": self.showExtensions,
			"cancel": self.quit,
		}, -2)
		
		self.showMenu()
		
	def add(self):
		if len(self.cacheList) == 0:
			return
			
		index = self['menu'].getIndex()
		config = MenuConfig()
		config.load()
		config.add(self.current, self.cacheList[index][1], self.cacheList[index][0])
		config.save()
		self.close()
	
	def showMenu(self):
		self.current = "menu"
		self.cacheList = []
		self.drawList = []
		
		self.parseMenu(self.root)
		self.cacheList.sort(key=lambda x: str(x[0]))
		for item in self.cacheList:
			pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_panel/" + item[1] + ".png"));
			if not pixmap:
				pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/empty.png"));
			self.drawList.append((pixmap, _(item[0])))
			
		self['menu'].setList(self.drawList)
		
	def showPlugins(self):
		self.current = "plugins"
		self.cacheList = []
		self.drawList = []

		self.readPlugins()
		self.cacheList.sort(key=lambda x: str(x[0]))
		for item in self.cacheList:
			pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_panel/" + item[1] + ".png"));
			if not pixmap:
				pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/empty.png"));
			self.drawList.append((pixmap, _(item[0])))

		self['menu'].setList(self.drawList)

	def showExtensions(self):
		self.current = "extensions"
		self.cacheList = []
		self.drawList = []

		self.readExtensions()
		self.cacheList.sort(key=lambda x: str(x[0]))
		for item in self.cacheList:
			pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_panel/" + item[1] + ".png"));
			if not pixmap:
				pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/empty.png"));
			self.drawList.append((pixmap, _(item[0])))

		self['menu'].setList(self.drawList)

	def readPlugins(self):
		pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
		for plugin in pluginlist:
			x = PluginEntryComponent(plugin)
			self.cacheList.append([x[1][7], x[1][7]])

	def readExtensions(self):
		pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_EXTENSIONSMENU)
		for plugin in pluginlist:
			x = PluginEntryComponent(plugin)
			self.cacheList.append([x[1][7], x[1][7]])

	def parseMenu(self, parent):
		menuID = None
		for x in parent:
			if x.tag == "item":
				self.addItem(x)
			elif x.tag == "menu":
				self.parseMenu(x)
			elif x.tag == "id":
				menuID = x.get("val")

		if menuID is not None:
			for l in plugins.getPluginsForMenu(menuID):
				plugin_menuid = l[2]
				for x in self.cacheList:
					if x[1] == plugin_menuid:
						self.cacheList.remove(x)
						break

				self.cacheList.append([l[0], l[2]])

	def addItem(self, node):
		requires = node.get("requires")
		if requires:
			if requires[0] == '!':
				if SystemInfo.get(requires[1:], False):
					return
			elif not SystemInfo.get(requires, False):
				return

		item_text = node.get("text", "").encode("UTF-8")
		entryID = node.get("entryID", "")
		weight = node.get("weight", 50)

		for x in node:
			if x.tag == 'setup':
				id = x.get("id")
				if item_text == "":
					item_text = _(getSetupTitle(id))
					
		if entryID == "":
			return

		self.cacheList.append([item_text, entryID])
		
	def quit(self):
		self.close()
