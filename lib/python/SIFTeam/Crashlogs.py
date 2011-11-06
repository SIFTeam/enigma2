from enigma import *
from Screens.Screen import Screen
from Components.config import config

from Extra.ExtraMessageBox import ExtraMessageBox
from Extra.ExtraActionBox import ExtraActionBox

import os
import httplib
import mimetypes

class SendCrashlog():
	def __init__(self, session):
		self.session = session
		
		self.updatestimer = eTimer()
		self.updatestimer.callback.append(self.checkCrashLogs)
		self.updatestimer.start(30*1000, 1)	# on init 1 minute delay

		self.sendtimer = eTimer()
		self.sendtimer.callback.append(self.sendCrashLogs)

	def messageboxCallback(self, ret):
		if ret == 0:
			self.sendtimer.start(500, 1)
		elif ret == 1:
			config.sifteam.crashlogs.value = "auto"
			config.sifteam.crashlogs.save()
			self.sendtimer.start(500, 1)
		elif ret == 2:
			print "[Automatic Updates] disabled by user"
			config.sifteam.crashlogs.value = "disabled"
			config.sifteam.crashlogs.save()

	def postMultipart(self, host, selector, filename, fieldname, content):
		content_type, body = self.encodeMultipartFormdata(filename, fieldname, content)
		h = httplib.HTTP(host)
		h.putrequest('POST', selector)
		h.putheader("Host", "%s:80" % (host))
		h.putheader('content-type', content_type)
		h.putheader('content-length', str(len(body)))
		h.endheaders()
		h.send(body)
		errcode, errmsg, headers = h.getreply()
		return h.file.read()

	def encodeMultipartFormdata(self, filename, fieldname, content):
		BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
		CRLF = '\r\n'
		L = []
		L.append('--' + BOUNDARY)
		L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (fieldname, filename))
		L.append('Content-Type: %s' % self.getContentType(filename))
		L.append('')
		L.append(content)
		L.append('--' + BOUNDARY + '--')
		L.append('')
		body = CRLF.join(L)
		content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
		return content_type, body

	def getContentType(self, filename):
		return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
			
	def sendCrashLogsT(self):
		dir = os.listdir("/hdd")
		for file in dir:
			if file[:14] == "enigma2_crash_" and file[-4:] == ".log":
				try:
					content = open("/hdd/" + file).read()
					self.postMultipart('crashlogs.enigma2.sifteam.eu', '/crashlog.php', file, "crashlog", content)
					print "posted crashlog: " + file
					os.unlink("/hdd/" + file)
				except Exception, ex:
					print ex
					
	def sendCrashLogs(self):
		self.session.open(ExtraActionBox, "Sending chrash logs ...", "Crash Logs", self.sendCrashLogsT)
		
	def foundCrashLogs(self):
		print "[Send Crashlogs] found crash logs"
		if config.sifteam.crashlogs.value == "disabled":
			print "[Send Crashlogs] submit disabled... skipping"
		elif config.sifteam.crashlogs.value == "auto":
			print "[Send Crashlogs] auto submit"
			self.sendtimer.start(500, 1)
		elif config.sifteam.crashlogs.value == "ask":
			print "[Send Crashlogs] ask"
			self.session.openWithCallback(self.messageboxCallback, ExtraMessageBox, "", "New crash logs found",
										[ [ "Send crash logs now", "install_now.png" ],
										[ "Always send automatically all crash logs", "install_auto.png" ],
										[ "Disable crash logs submit", "install_disable.png" ],
										[ "Ask later", "install_later.png" ],
										], 1, 3)

	def checkCrashLogs(self):
		if len(self.session.dialog_stack) > 0:
			print "[Send Crashlogs] osd busy"
			print "[Send Crashlogs] rescheduled in 10 minutes"
			self.updatestimer.start(10*60*1000, 1)
			return
			
		exist = False
		dir = os.listdir("/hdd")
		for file in dir:
			if file[:14] == "enigma2_crash_" and file[-4:] == ".log":
				exist = True
				break
			
		if exist:
			self.foundCrashLogs()

# helper for start autoupdates on mytest init
sendchrashlog = None
def startSendCrashlog(session):
	global sendchrashlog
	sendchrashlog = SendCrashlog(session)
