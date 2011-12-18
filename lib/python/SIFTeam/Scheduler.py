from enigma import *

from datetime import datetime
from Components.config import config

def addMinutesToTime(entry, minutes):
	ret = entry + (minutes * 60)
	if ret >= 86400:
		ret -= 86400
		
	return ret
	
def getMinuteFromTime(entry):
	return int(entry % 3600 / 60)
	
def getHourFromTime(entry):
	return int(entry / 3600)
	
class Scheduler(object):
	entries = []
	
	def __init__(self, session):
		self.session = session
		
		self.timer = eTimer()
		self.timer.callback.append(self.ticker)
		self.timer.start(60000)
		
	def ticker(self):
		now = datetime.now()
		for entry in self.entries:
			if entry["minute"] != now.minute and entry["minute"] != -1:
				continue
				
			if entry["hour"] != now.hour and entry["hour"] != -1:
				continue
				
			entry["callback"](self.session, entry["id"], entry["arg"])
		
	def add(self, id, hour, minute, callback, arg):
		for entry in self.entries:
			if entry["id"] == id:
				entry["hour"] = hour
				entry["minute"] = minute
				entry["callback"] = callback
				entry["arg"] = arg
				return
				
		self.entries.append({
			"id": id,
			"hour": hour,
			"minute": minute,
			"callback": callback,
			"arg": arg
		})
		
scheduler = None

def loadDefaultScheduler():
	autosendcrashlogs = config.sifteam.cloud.timeautoupdates.value
	autoupdates_settings = addMinutesToTime(autosendcrashlogs, 5)
	autoupdates_software = addMinutesToTime(autoupdates_settings, 2)
	
	from SIFTeam.Crashlogs import autoSendCrashLogs
	scheduler.add("autosendcrashlogs", getHourFromTime(autosendcrashlogs), getMinuteFromTime(autosendcrashlogs), autoSendCrashLogs, None)
	
	from SIFTeam.Settings.AutoUpdates import startAutomaticSettingsUpdates
	scheduler.add("autoupdates_settings", getHourFromTime(autoupdates_settings), getMinuteFromTime(autoupdates_settings), startAutomaticSettingsUpdates, None)
	
	from SIFTeam.SoftwareManager.AutoUpdates import startAutomaticSoftwareUpdates
	scheduler.add("autoupdates_software", getHourFromTime(autoupdates_software), getMinuteFromTime(autoupdates_software), startAutomaticSoftwareUpdates, None)
	
def initScheduler(session):
	global scheduler
	scheduler = Scheduler(session)
	loadDefaultScheduler()
	