from enigma import *
from Screens.Screen import Screen
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap

class AboutTeam(Screen):
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		
		abouttxt = """Skaman (developer & coder)
Ukiller_Bestia (web master and server maintainer)
Genge (manager)
Ipbox2008 (coder)
Dr_Gogeta86(fuzzy coder)
Morpheus883(Settings Master Chief)
Cus2k (betatester)
Raskino (betatester)
Theseven (betatester)
Biondo79 (betatester)"""
Katapip (katatester)
Barrett (stuntman)
		
		self["about"] = Label(abouttxt)
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"cancel": self.quit,
		}, -2)
		
	def quit(self):
		self.close()
