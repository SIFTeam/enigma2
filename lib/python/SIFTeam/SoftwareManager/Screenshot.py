from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.Button import Button
from Components.Pixmap import Pixmap

from SIFTeam.Extra.SAPCL import SAPCL

import urllib

class SMScreenshot(Screen):
	def __init__(self, session, package):
		Screen.__init__(self, session)
		
		self.package = package
		self.session = session

		self["screenshot"] = Pixmap()
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.close
		}, -2)
		
		self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.paintScreenshotPixmapCB)
		
		self.timer = eTimer()
		self.timer.callback.append(self.getPreview)
		self.timer.start(200, 1)
		
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle("Software Manager - Screenshot - %s" % self.package["name"])
		
	def getPreview(self):
		try:
			f = urllib.urlopen(self.package["screenshot"])
			data = f.read()
			f.close()
			tmp = self.package["screenshot"].split(".")
			localfile = "/tmp/preview.%s" % tmp[len(tmp)-1]
			f2 = open(localfile , "w")
			f2.write(data)
			f2.close()
			sc = AVSwitch().getFramebufferScale()
			self.picload.setPara((self["screenshot"].instance.size().width(), self["screenshot"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
			self.picload.startDecode(localfile)
		except ex:
			print ex
			
	def paintScreenshotPixmapCB(self, picInfo=None):
		ptr = self.picload.getData()
		if ptr != None:
			self["screenshot"].instance.setPixmap(ptr.__deref__())
			self["screenshot"].show()