from Screens.MessageBox import MessageBox
from Components.config import config
from enigma import eTimer

import os
import time
import libemu

class Emud():
	def __init__(self):
		self.messages = libemu.EmuMessages()
		self.messages.setPyErrorCallback(self.error)
		self.emuclient = libemu.EmuClient(libemu.EmuClient.EMU, self.messages)
		self.csclient = libemu.EmuClient(libemu.EmuClient.CS, self.messages)
		
	def setSession(self, session):
		self.session = session
	
	def connect(self):
		if self.csclient.connect():
			print "sifteam cs client connected"
		else:
			print "cannot connect cs client to emud"
			
		if self.emuclient.connect():
			print "sifteam emu client connected"
		else:
			print "cannot connect emu client to emud"
			
	def disconnect(self):
		if self.emuclient.isConnected():
			self.emuclient.disconnect()
			print "sifteam emu client disconnected"
			
		if self.csclient.isConnected():
			self.csclient.disconnect()
			print "sifteam cs client disconnected"
			
	def error(self, message):
		if self.session.in_exec:
			self.session.open(MessageBox, message, type = MessageBox.TYPE_ERROR, timeout = 30)
		
	def startDefaults(self):
		if self.emuclient.isConnected() and self.csclient.isConnected():
			delay = int(config.sifteam.emudelay.value)
			if delay == 0:
				self._startDefaults()
			else:
				print "start default emu/cs delayed"
				self.stimer = eTimer()
				self.stimer.callback.append(self._startDefaults)
				self.stimer.start(delay * 1000, 1)
		
	def _startDefaults(self):
		if self.emuclient.isConnected() and self.csclient.isConnected():
			csstarted = False
			css = self.getCsList()
			for cs in css:
				if cs[3]:
					csstarted = True
					
			if not csstarted:
				if self.csclient.sendStart():
					print "default card server started"
					print "wait 10 seconds"
					time.sleep(10)
			else:
				print "default card server already started"
				
			emustarted = False
			emus = self.getEmuList()
			for emu in emus:
				if emu[3]:
					emustarted = True
					
			if not emustarted:
				if self.emuclient.sendStart():
					print "default emulator started"
			else:
				print "default emulator already started"
			
	def getEmuList(self):
		ret = []
		if not self.emuclient.isConnected():
			return ret
			
		self.emuclient.sendList()
		if self.emuclient.emuCount() > 0:
			self.emuclient.emuFirst()
			while True:
				ret.append(
					(self.emuclient.emuGetName(),
					self.emuclient.emuGetVersion(),
					self.emuclient.emuGetDescription(),
					self.emuclient.emuGetIsStarted(),
					self.emuclient.emuGetId()))
				if not self.emuclient.emuNext():
					break;
		return ret
		
	def startEmu(self, id):
		if self.emuclient.isConnected():
			self.emuclient.sendStart(id)
		
	def stopEmu(self):
		if self.emuclient.isConnected():
			self.emuclient.sendStop()
		
	def restartEmu(self):
		if self.emuclient.isConnected():
			self.emuclient.sendRestart()
		
	def getCsList(self):
		ret = []
		if not self.csclient.isConnected():
			return ret
			
		self.csclient.sendList()
		if self.csclient.emuCount() > 0:
			self.csclient.emuFirst()
			while True:
				ret.append(
					(self.csclient.emuGetName(),
					self.csclient.emuGetVersion(),
					self.csclient.emuGetDescription(),
					self.csclient.emuGetIsStarted(),
					self.csclient.emuGetId()))
				if not self.csclient.emuNext():
					break;
		return ret
		
	def startCs(self, id):
		if self.csclient.isConnected():
			self.csclient.sendStart(id)

	def stopCs(self):
		if self.csclient.isConnected():
			self.csclient.sendStop()

	def restartCs(self):
		if self.csclient.isConnected():
			self.csclient.sendRestart()
		
	def getInfoSystem(self):
		return self.emuclient.getInfoSystem()
		
	def getInfoCaID(self):
		return self.emuclient.getInfoCaID()
		
	def getInfoSystemByte(self):
		if len(self.emuclient.getInfoCaID()) == 5:	# with 0x
			return self.emuclient.getInfoCaID()[2:3]
		elif len(self.emuclient.getInfoCaID()) == 6:
			return self.emuclient.getInfoCaID()[2:4]

		return ""
		
	def getInfoPid(self):
		return self.emuclient.getInfoPid()
		
	def getInfoProtocol(self):
		return self.emuclient.getInfoProtocol()
		
	def getInfoAddress(self):
		return self.emuclient.getInfoAddress()
		
	def getInfoProvID(self):
		return self.emuclient.getInfoProvID()
		
	def getInfoTime(self):
		return self.emuclient.getInfoTime()
		
	def getInfoHops(self):
		return self.emuclient.getInfoHops()
		
	def getInfoCW0(self):
		return self.emuclient.getInfoCW0()
		
	def getInfoCW1(self):
		return self.emuclient.getInfoCW1()
		
	def getInfoName(self):
		return self.emuclient.getInfoName()
		
emud = Emud()
