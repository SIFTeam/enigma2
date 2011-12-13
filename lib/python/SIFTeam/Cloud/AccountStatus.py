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

MONTHS = (_("January"),
          _("February"),
          _("March"),
          _("April"),
          _("May"),
          _("June"),
          _("July"),
          _("August"),
          _("September"),
          _("October"),
          _("November"),
          _("December"))

dayOfWeek = (_("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat"), _("Sun"))

class AccountStatusHelper(Screen):
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		
		self.timer = eTimer()
		self.timer.callback.append(self.readAccountInfo)
		self.timer.start(200, 1)

	def executeRequest(self):
		api = SAPCL()
		return api.getAccount()

	def executeRequestCallback(self, result):
		if result["result"]:
			self.session.open(AccountStatus, result["status"])
		else:
			self.session.open(MessageBox, result["message"], MessageBox.TYPE_ERROR)
		self.close()

	def readAccountInfo(self):
		self.session.openWithCallback(self.executeRequestCallback, ExtraActionBox, _("Reading from sifteam server..."), "Account status", self.executeRequest)

class AccountStatus(Screen):
	def __init__(self, session, status):
		Screen.__init__(self, session)
		
		msg = "Username: %s\n" % status["username"]
		msg += "Email: %s\n" % status["email"]
		msg += "Title: %s\n" % status["usertitle"]
		msg += "Posts: %i\n" % status["posts"]
		jt = time.localtime(status["joindate"])
		lt = time.localtime(status["lastpost"])
		msg += "Join date: %s %s %s %s at %02d:%02d\n" % (dayOfWeek[jt[6]], str(jt[2]), MONTHS[jt[1]-1], jt[0], jt.tm_hour, jt.tm_min)
		msg += "Last post date: %s %s %s %s at %02d:%02d\n" % (dayOfWeek[lt[6]], str(lt[2]), MONTHS[lt[1]-1], lt[0], lt.tm_hour, lt.tm_min)
		
		self["status"] = Label(msg)
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["key_blue"] = Button("")
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.quit,
		}, -2)
		
	def quit(self):
		self.close()
		
