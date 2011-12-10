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
		self.categories = api.getCategories(0, True)
		os.system("opkg update")
		rows = os.popen("opkg list_upgradable").read().strip().split("\n")
		self.upgrades = []
		for row in rows:
			tmp = row.split(" - ")
			if len(tmp) == 3:
				self.upgrades.append({
					"package": tmp[0],
					"oldversion": tmp[1],
					"newversion": tmp[2]
				})
		return True

	def executeRequestCallback(self, result):
		if result:
			self.session.open(SMCategories, self.categories, self.upgrades)
		self.close()

	def readCategories(self):
		self.session.openWithCallback(self.executeRequestCallback, ExtraActionBox, _("Retrieving data from sifteam server..."), "Software Manager", self.executeRequest)