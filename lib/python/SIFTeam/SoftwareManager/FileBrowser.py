from enigma import *
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.FileList import FileList

from SIFTeam.Extra.SAPCL import SAPCL
from SIFTeam.Extra.ExtraActionBox import ExtraActionBox
from Stack import SMStack, smstack
from Status import SMStatus

import os

class SMFileBrowser(Screen):

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
		self.setTitle("%s - %s" % ("Software Manager - File Browser", "/tmp"))
		
	def tgz(self):
		self.tgzret = os.system("tar zxf \"%s\" -C /" % self.filename)
		
	def ok(self):
		if self["filelist"].canDescent(): # isDir
			self["filelist"].descent()
			self.setTitle("%s - %s" % ("Software Manager - File Browser", self["filelist"].getCurrentDirectory()))
		else:
			filename = self["filelist"].getCurrentDirectory() + '/' + self["filelist"].getFilename()
			if filename[-3:] == "ipk":
				smstack.add(SMStack.INSTALL, filename)
				self.session.open(SMStatus)
				self.close()
			else:
				self.filename = filename
				self.session.openWithCallback(self.tgzexit, ExtraActionBox, "Deflating %s to /" % self["filelist"].getFilename(), "Install from tar.gz", self.tgz)
			
	def tgzexit(self, result):
		if self.tgzret == 0:
			self.session.open(MessageBox, _("Package installed succesfully"), MessageBox.TYPE_INFO)
		else:
			self.session.open(MessageBox, _("Error installing package"), MessageBox.TYPE_ERROR)
		self.close()
		
	def exit(self):
		self.close()
		
