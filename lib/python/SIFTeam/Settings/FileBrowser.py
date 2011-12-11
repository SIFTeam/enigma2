from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.FileList import FileList
from Components.Button import Button

from SIFTeam.Extra.ExtraActionBox import ExtraActionBox

from Deflate import STDeflate
from Common import TMP_IMPORT_PWD, TMP_SETTINGS_PWD, SettingsLoader

import shutil

class STFileBrowser(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["filelist"] = FileList("/tmp", matchingPattern = "(?i)^.*\.(ipk|tar\.gz|tgz|zip)")
		
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
		self.setTitle("Settings - File Browser - /tmp")
		
	def load(self):
		STDeflate().deflate(self.filename)
		
		settings = SettingsLoader()
		settings.apply()
		
		try:
			shutil.rmtree(TMP_SETTINGS_PWD)
		except Exception, e:
			pass
			
		try:
			shutil.rmtree(TMP_IMPORT_PWD)
		except Exception, e:
			pass

		try:
			os.unlink(result["filename"])
		except Exception, e:
			pass
			
		self.session.open(MessageBox, _("Settings installed"), type = MessageBox.TYPE_INFO, timeout = 5)
		
	def ok(self):
		if self["filelist"].canDescent(): # isDir
			self["filelist"].descent()
			self.setTitle("Settings - File Browser - " + self["filelist"].getCurrentDirectory())
		else:
			self.filename = self["filelist"].getCurrentDirectory() + '/' + self["filelist"].getFilename()
			self.session.openWithCallback(self.close, ExtraActionBox, _("Loading settings"), _("Loading ..."), self.load)

	def exit(self):
		self.close()