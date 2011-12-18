from Components.config import config
from Extra.SAPCL import SAPCL

import os

def autoSendCrashLogs(session, id, arg):
	if not config.sifteam.cloud.crashlogs.value:
		return
		
	api = SAPCL()
	files = os.listdir("/hdd/")
	if not files:
		return
		
	for file in files:
		try:
			if file[:14] != "sifteam_crash_" or file[-4:] != ".log" or file[-9:] == "_sent.log":
				continue
				
			buff = open("/hdd/" + file).read()
			api.sendCrashLog(buff)
			os.rename("/hdd/" + file, "/hdd/" + file.replace(".log", "_sent.log"))
		except Exception, e:
			pass

