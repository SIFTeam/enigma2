from enigma import *

from datetime import datetime
from Components.config import config

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
	hour = int(config.sifteam.cloud.timeautoupdates.value/3600)
	minute = int(config.sifteam.cloud.timeautoupdates.value%3600/60)
	
	from SIFTeam.SoftwareManager.AutoUpdates import startAutomatiUpdates
	scheduler.add("autoupdates", hour, minute, startAutomatiUpdates, None)
	
def initScheduler(session):
	global scheduler
	scheduler = Scheduler(session)
	loadDefaultScheduler()
	