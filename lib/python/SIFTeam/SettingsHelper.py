from enigma import *
from Screens.Screen import Screen

from Extra.SAPCL import SAPCL
from Extra.ExtraActionBox import ExtraActionBox

from Settings.Categories import STCategories

import os

class STScreenHelper(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.timer = eTimer()
		self.timer.callback.append(self.readCategories)
		self.timer.start(200, 1)

	def executeRequest(self):
		api = SAPCL()
		self.settings = api.getChannelsSettings()
		return True

	def executeRequestCallback(self, result):
		if result:
			self.session.open(STCategories, self.settings)
		self.close()

	def readCategories(self):
		self.session.openWithCallback(self.executeRequestCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequest)