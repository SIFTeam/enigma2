from enigma import eTimer
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config

from SIFTeam.Extra.SAPCL import SAPCL
from SIFTeam.Extra.ExtraActionBox import ExtraActionBox

import time

class AccountConfiguration(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = [
			getConfigListEntry(_("Username:"), config.sifteam.cloud.username),
			getConfigListEntry(_("Password:"), config.sifteam.cloud.password)
		]
		
		ConfigListScreen.__init__(self, self.list, session = session)
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
				{
					"ok": self.ok,
					"cancel": self.keyCancel,
				}, -2)
				
		self["status"] = Label("")
		self["info"] = Label("Register a new account: http://forum.sifteam.eu/register.php\nLost password: http://forum.sifteam.eu/login.php?do=lostpw")
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		
	def executeRequest(self):
		api = SAPCL()
		return api.getAccount()

	def executeRequestCallback(self, result):
		if result["result"]:
			self.keySave()
			self.close()
		else:
			self["status"].setText(result["message"])
	
	def ok(self):
		self.session.openWithCallback(self.executeRequestCallback, ExtraActionBox, _("Validating on sifteam server..."), "Account Configuration", self.executeRequest)
		

