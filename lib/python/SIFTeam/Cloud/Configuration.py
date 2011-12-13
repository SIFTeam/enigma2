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

from SIFTeam.Scheduler import loadDefaultScheduler
import time

class CloudConfiguration(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = [
			getConfigListEntry(_("Update image and softwares automatically:"), config.sifteam.cloud.softwareupdates),
			getConfigListEntry(_("Update settings automatically:"), config.sifteam.cloud.settingsupdates),
			getConfigListEntry(_("Time for automatic updates"), config.sifteam.cloud.timeautoupdates),
			getConfigListEntry(_("Send crashlogs:"), config.sifteam.cloud.crashlogs)
		]
		
		ConfigListScreen.__init__(self, self.list, session = session)
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
				{
					"ok": self.ok,
					"cancel": self.keyCancel,
				}, -2)
				
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		
	def ok(self):
		self.keySave()
		loadDefaultScheduler()
		self.close()
		
