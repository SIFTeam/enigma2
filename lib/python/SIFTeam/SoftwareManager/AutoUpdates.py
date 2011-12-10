from enigma import *
from Screens.Screen import Screen
from Components.config import config

from SIFTeam.Extra.SAPCL import SAPCL
from SIFTeam.Extra.ExtraMessageBox import ExtraMessageBox

import os

class SMAutoUpdates():
	def __init__(self, session):
		self.session = session
		
		self.updatestimer = eTimer()
		self.updatestimer.callback.append(self.checkupdates)
		self.updatestimer.start(60*1000, 1)	# on init 1 minute delay
		
	def upgrade(self):
			print "[Automatic Updates] system upgraded"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)

	def messageboxCallback(self, ret):
		if ret == 0:
			self.upgrade()
		elif ret == 1:
			config.sifteam.autoupdates.value = "auto"
			config.sifteam.autoupdates.save()
			self.upgrade()
		elif ret == 2:
			print "[Automatic Updates] disabled by user"
			config.sifteam.autoupdates.value = "disabled"
			config.sifteam.autoupdates.save()
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)
		else:
			print "[Automatic Updates] install later"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)

	def checkupdates(self):
		if config.sifteam.autoupdates.value == "disabled":
			print "[Automatic Updates] disabled by user"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)
			return
			
		if len(self.session.dialog_stack) > 0:
			print "[Automatic Updates] osd busy"
			print "[Automatic Updates] rescheduled in 10 minutes"
			self.updatestimer.start(10*60*1000, 1)
			return

		if self.session.nav.RecordTimer.isRecording():
			print "[Automatic Updates] record in progress"
			print "[Automatic Updates] rescheduled in 1 hour"
			self.updatestimer.start(1*60*60*1000, 1)
			return

		print "[Automatic Updates] updating feeds..."
		os.system("opkg update")
		print "[Automatic Updates] feeds updated"
		
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
				
		if len(self.upgrades) == 0:
			print "[Automatic Updates] no updates found"
			print "[Automatic Updates] rescheduled in 24 hours"
			self.updatestimer.start(24*60*60*1000, 1)
			return
			
		print "[Automatic Updates] updates found"
		if config.sifteam.autoupdates.value == "auto":
			self.upgrade()
		else:
			self.session.openWithCallback(self.messageboxCallback, ExtraMessageBox, "", "New updates found",
										[ [ "Install updates now", "install_now.png" ],
										[ "Always install automatically all updates", "install_auto.png" ],
										[ "Disable automatic updates", "install_disable.png" ],
										[ "Ask later", "install_later.png" ],
										], 1, 3)
		
			
# helper for start autoupdates on mytest init
autoupdates = None
def startAutomatiUpdates(session):
	global autoupdates
	autoupdates = SMAutoUpdates(session)