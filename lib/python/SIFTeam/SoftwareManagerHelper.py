from enigma import *
from Screens.Screen import Screen

from Extra.SAPCL import SAPCL
from Extra.ExtraActionBox import ExtraActionBox

from SoftwareManager.Categories import SMCategories

import os

class SMScreenHelper(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.timer = eTimer()
		self.timer.callback.append(self.readCategories)
		self.timer.start(200, 1)

	def executeRequest(self):
		api = SAPCL()
		return api.getCategories(0, True)

	def executeRequestCallback(self, result):
		if result:
			self.session.open(SMCategories, result)
		self.close()

	def readCategories(self):
		self.session.openWithCallback(self.executeRequestCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequest)