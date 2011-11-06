from threading import Thread

import os
import time

class FifoListener(Thread):
	def __init__(self):
		Thread.__init__(self)
		
	def setSession(self, session):
		self.session = session
		
	def run(self):
		self.exit = False
		os.system("rm -f /tmp/e2_commands")
		os.system("mkfifo -m 666 /tmp/e2_commands");
		fifo = os.open("/tmp/e2_commands", os.O_NONBLOCK | os.O_RDONLY)
		
		print "sifteam fifolistener started"
		
		while not self.exit:
			line = None
			try:
				line = os.read(fifo, 256)
			except Exception, e:
				pass
			if line:
				cmd = line.strip()
				if cmd == "reboot":
					from Screens.Standby import TryQuitMainloop
					self.session.open(TryQuitMainloop, 3)
				if cmd == "reload_settings":
					from enigma import eDVBDB
					edvbdb = eDVBDB.getInstance()
					edvbdb.reloadServicelist()
					edvbdb.reloadBouquets()
				
			time.sleep(1)
		os.close(fifo)
		
	def stop(self):
		self.exit = True
		self.join()
		print ("sifteam fifolistener stopped")
			
fifolistener = FifoListener()
