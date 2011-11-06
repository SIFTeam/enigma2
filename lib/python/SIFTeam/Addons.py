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

import libsif
import re
import os
import urllib

ipkg = libsif.Ipkg()
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

def CategoryEntry(name, picture):
	pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/" + picture));
	if not pixmap:
		pixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/folder.png"));
		
	return (pixmap, name)

def PackageEntry(name, version, size, installed):
	if installed:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"));
	else:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_off.png"));
		
	return (name, version, FormatSize(size), picture)

class Addons():
	def __init__(self, session):
		self.session = session
		self.lastresult = 0
		self.version = "000"
		self.shortcut = ""
		try:
			f = open("/etc/openee-version", "r")
			self.version = f.read().strip()
			f.close()
		except:
			pass


	def showMenu(self, callback):
		global addons_loaded
		addons_loaded = True
		self.callback = callback
		self.session.openWithCallback(self.updateCallback, AddonsAction, AddonsAction.IPKG_UPDATE)

	def goToShortcut(self, shortcut, callback):
		global addons_loaded
		addons_loaded = True
		self.callback = callback
		self.shortcut = shortcut
		if self.shortcut.find("_remove") > -1:
			self.session.openWithCallback(self.showShortcut, ExtraActionBox, _("Loading data..."), "Software Manager", ipkg.categoryInit)
		else:
			self.session.openWithCallback(self.updateCallbackForShortcut, AddonsAction, AddonsAction.IPKG_UPDATE)

	def install(self, name, callback):
		global addons_loaded
		addons_loaded = True
		self.name = name
		self.callback = callback
		self.session.openWithCallback(self.updateCallbackInstall, AddonsAction, AddonsAction.IPKG_UPDATE)

	def remove(self, name, callback):
		global addons_loaded
		addons_loaded = True
		self.callback = callback
		self.session.openWithCallback(self.end, AddonsAction, AddonsAction.IPKG_REMOVE, True, name)

	def menuCallback(self, result):
		self.lastresult = result
		if result == 999:
			self.endWithDeinit()
			return

		if result < ipkg.xmlCategoriesCount():
			self.session.openWithCallback(self.showNow, AddonsPackages, None, result)
		else:
			result -= ipkg.xmlCategoriesCount()
			if result == 0:
				self.session.openWithCallback(self.showNow, AddonsCategories)
			elif result == 1:
				self.session.openWithCallback(self.showNow, AddonsFileBrowser)
			elif result == 2:
				self.session.openWithCallback(self.updateCallback, AddonsAction, AddonsAction.IPKG_UPGRADE, True)
				
	def updateCallback(self):
		self.session.openWithCallback(self.showNow, ExtraActionBox, _("Loading data..."), "Software Manager", ipkg.categoryInit)

	def updateCallbackForShortcut(self):
		self.session.openWithCallback(self.showShortcut, ExtraActionBox, _("Loading data..."), "Software Manager", ipkg.categoryInit)

	def updateCallbackInstall(self):
		self.session.openWithCallback(self.end, AddonsAction, AddonsAction.IPKG_INSTALL, True, self.name)

	def end(self):
		global addons_loaded
		addons_loaded = False
		self.callback()

	def endWithDeinit(self):
		global addons_loaded
		addons_loaded = False
		ipkg.categoryDeinit()
		self.callback()

	def upgradeCallback(self):
		self.session.openWithCallback(self.showNow, ExtraActionBox, _("Reloading data..."), "Software Manager", ipkg.categoryRefresh)

	def showNow(self, result = None):
		menu = []
		for i in range (0, ipkg.xmlCategoriesCount()):
			cat = ipkg.categoryGetXml(i)
			text = "%s (%d/%d)" % (cat.getName(), cat.countInstalled(), cat.count())
			menu.append([text, cat.getIcon()])

		menu.append([_("All packages (%d/%d)") % (ipkg.categoryGetAll().countInstalled(), ipkg.categoryGetAll().count()), "packages.png"])
		menu.append([_("Install from file (ipk or tar.gz)"), "package.png"])

		totalupdates =  ipkg.categoryGetUpdates().count();
		if totalupdates == 1:
			menu.append([_("%d update found. Update now") % totalupdates, "install_now.png"]);
		elif totalupdates > 1:
			menu.append([_("%d updates found. Update now") % totalupdates, "install_now.png"]);

		if self.lastresult > 5:
			self.lastresult = 0
		self.session.openWithCallback(self.menuCallback, ExtraMessageBox, "", "Software Manager - current svn: %s" % self.version, menu, 1, 999, self.lastresult)

	def showShortcut(self, result = None):
		menu = []
		for i in range (0, ipkg.xmlCategoriesCount()):
			cat = ipkg.categoryGetXml(i)
			shortcuts = cat.getShortcut().split(",")
			for shortcut in shortcuts:
				if shortcut == self.shortcut:
					if self.shortcut.find("_install") > -1:
						self.session.openWithCallback(self.endWithDeinit, AddonsPackages, None, i, "install")
					elif self.shortcut.find("_remove") > -1:
						self.session.openWithCallback(self.endWithDeinit, AddonsPackages, None, i, "remove")
					else:
						self.session.openWithCallback(self.endWithDeinit, AddonsPackages, None, i)
					return
				
		self.session.open(MessageBox, _("Error loading selected shortcut"), MessageBox.TYPE_ERROR)
		self.endWithDeinit()

class AddonsCategories(Screen):
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		
		self.session = session
		self.cachelist = []
		self.uilist = []
		self.lastindex = 0
		
		self['list'] = List([])
		self["list"].onSelectionChanged.append(self.selectionChanged)
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"cancel": self.quit,
			"ok": self.ok,
		}, -2)
		
		self.timer = eTimer()
		self.timer.callback.append(self.listUpdated)
		self.timer.start(200, 1)
		
	def listUpdated(self):
		self.uilist = []
		self.cachelist = []
		cat = ipkg.categoryGetAll()
		self.uilist.append(CategoryEntry("%s (%d/%d)" % (cat.getName(), cat.countInstalled(), cat.count()), "%s.png" % cat.getName()))
		self.cachelist.append(cat)
		ipkg.categoryFirst()
		while True:
			cat = ipkg.categoryGet() #.getName()
			self.uilist.append(CategoryEntry("%s (%d/%d)" % (cat.getName(), cat.countInstalled(), cat.count()), "%s.png" % cat.getName()))
			self.cachelist.append(cat)
			if not ipkg.categoryNext():
				break
			
		self["list"].setList(self.uilist)
		if self.lastindex < len(self.cachelist):
			self['list'].setCurrentIndex(self.lastindex)
		
	def reinit(self, res = False):
		if res:
			self.cachelist = []
			self['list'].setList([])
			ipkg.categoryRefresh()
			self.listUpdated()
			self.ok()
	
	def selectionChanged(self):
		if len(self.cachelist) > 0:
			index = self["list"].getIndex()
	
	def ok(self):
		if len(self.cachelist) > 0:
			index = self["list"].getIndex()
			self.lastindex = index
			self.session.openWithCallback(self.reinit, AddonsPackages, self.cachelist[index])
	
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
  
class AddonsPackages(Screen):
	def __init__(self, session, category, smartcategory = None, statusfilter = None):
		Screen.__init__(self, session)
		
		self.category = category
		self.smartcategory = smartcategory
		self.statusfilter = statusfilter

		if self.smartcategory is not None:
			self.category = ipkg.categoryGetXml(self.smartcategory)

		self.session = session
		self.uilist = []
		
		self['list'] = List([])
		self["list"].onSelectionChanged.append(self.selectionChanged)
		self["text"] = ScrollLabel("")
		self["key_green"] = Button(_("Download"))
		self["key_red"] = Button("")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"cancel": self.quit,
			"red": self.install,
			"green": self.download,
			"yellow": self.preview
		}, -2)
		
		self.timer = eTimer()
		self.timer.callback.append(self.drawList)
		self.timer.start(200, 1)

	def drawList(self):
		self.uilist = []
		self.cachelist = []
		if self.category.count() > 0:
			self.category.packageFirst()
			while True:
				ok = False
				if self.statusfilter == None:
					ok = True
				elif self.statusfilter == "install" and not self.category.packageGet().installed:
					ok = True
				elif self.statusfilter == "remove" and self.category.packageGet().installed:
					ok = True
				if ok:
					self.cachelist.append(self.category.packageGet())
					if len(self.category.packageGet().friendlyname) > 0:
						name = self.category.packageGet().friendlyname
					else:
						name = self.category.packageGet().name
					self.uilist.append(PackageEntry(name,
												self.category.packageGet().version,
												self.category.packageGet().size,
												self.category.packageGet().installed))
				if not self.category.packageNext():
					break
			
		self["list"].setList(self.uilist)
		if self.statusfilter == None:
			self.setTitle("Software Manager - %s" % self.category.getName())
		elif self.statusfilter == "install":
			self.setTitle("Software Manager - %s - Install" % self.category.getName())
		elif self.statusfilter == "remove":
			self.setTitle("Software Manager - %s - Remove" % self.category.getName())

	def selectionChanged(self):
		if len(self.cachelist) > 0:
			index = self["list"].getIndex()
			newline = re.compile("(\n)")
			spaces = re.compile("\s+")
			try:
				desc = newline.sub(" ", self.cachelist[index].description)
				desc = spaces.sub(" ", desc)
			except Exception:
				desc = ""

			text = ""
			text += _("Name: %s") % self.cachelist[index].name
			text += _("    Version: %s\n") % self.cachelist[index].version
			text += _("Size: %s") % FormatSize(self.cachelist[index].size)
			text += _("    Architecture: %s\n") % self.cachelist[index].architecture
			text += _("Description: %s") % desc
			self["text"].setText(text)
			
			if self.cachelist[index].installed:
				self["key_red"].setText(_("Remove"))
			else:
				self["key_red"].setText(_("Install"))

			if len(self.cachelist[index].previewimage1) > 0:
				self["key_yellow"].setText(_("Preview"))
			else:
				self["key_yellow"].setText("")

	def install(self):
		if len(self.cachelist) > 0:
			index = self["list"].getIndex()
			if self.cachelist[index].installed:
				self.session.openWithCallback(self.reinit, AddonsAction, AddonsAction.IPKG_REMOVE, True, self.cachelist[index].name)
			else:
				self.session.openWithCallback(self.reinit, AddonsAction, AddonsAction.IPKG_INSTALL, True, self.cachelist[index].name)

	def download(self):
		if len(self.cachelist) > 0:
			index = self["list"].getIndex()
			self.session.openWithCallback(self.reinit, AddonsAction, AddonsAction.IPKG_DOWNLOAD, True, self.cachelist[index].name)

	def preview(self):
		if len(self.cachelist) > 0:
			index = self["list"].getIndex()
			if len(self.cachelist[index].previewimage1) > 0:
				self.session.open(AddonsPreview, self.cachelist[index])

	def reinit(self):
		if self.smartcategory is None:
			self.close(True)
		else:
			ipkg.categoryRefresh()
			self.category = ipkg.categoryGetXml(self.smartcategory)
			self.drawList()

	def quit(self):
		self.close()

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

class AddonsScreenHelper(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.timer = eTimer()
		self.timer.callback.append(self.start)
		self.timer.start(200, 1)

	def start(self):
		self.addons = Addons(self.session)
		self.addons.showMenu(self.close)
