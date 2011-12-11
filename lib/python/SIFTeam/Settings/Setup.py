from Screens.Screen import Screen

from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config
from Components.ActionMap import ActionMap
from Components.Button import Button

class STSetup(Screen, ConfigListScreen):
		
	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = [
			getConfigListEntry(_("Keep terrestrial settings:"), config.sifteam.settings.keepterrestrial),
			getConfigListEntry(_("Keep satellites.xml:"), config.sifteam.settings.keepsatellitesxml),
			getConfigListEntry(_("Keep terrestrial.xml:"), config.sifteam.settings.keepterrestrialxml),
			getConfigListEntry(_("Keep cables.xml:"), config.sifteam.settings.keepcablesxml),
		]

		ConfigListScreen.__init__(self, self.list, session = session)
		self["key_red"] = Button("")
		self["key_green"] = Button("")
		self["key_yellow"] = Button("")
		self["key_blue"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
				{
					"ok": self.ok,
					"cancel": self.keyCancel,
				}, -2)
	
	
	def ok(self):
		self.keySave()