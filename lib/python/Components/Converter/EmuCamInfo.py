from Components.Converter.Converter import Converter
from Components.Element import cached
from Poll import Poll
from enigma import iPlayableService

from SIFTeam.Extra.Emud import emud

class EmuCamInfo(Poll, Converter, object):
	SYSTEM = 0
	CAID = 1
	PID = 2
	PROTOCOL = 3
	ADDRESS = 4
	PROVID = 5
	TIME = 6
	HOPS = 7
	CW0 = 8
	CW1 = 9
	NAME = 10
	NAME_SLIM = 11
	BASIC_INFO = 12
	CRYPT_INFO = 13
	
	type = -1
	
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 2*1000
		self.poll_enabled = True
		
		if type == "System":
			self.type = self.SYSTEM
		elif type == "CaID":
			self.type = self.CAID
		elif type == "Pid":
			self.type = self.PID
		elif type == "Protocol":
			self.type = self.PROTOCOL
		elif type == "Address" or type == "ServerInfo":
			self.type = self.ADDRESS
		elif type == "ProvID":
			self.type = self.PROVID
		elif type == "Time" or type == "ECMTime":
			self.type = self.TIME
		elif type == "Hops":
			self.type = self.HOPS
		elif type == "CW0":
			self.type = self.CW0
		elif type == "CW1":
			self.type = self.CW1
		elif type == "Name":
			self.type = self.NAME
		elif type == "EMU":
			self.type = self.NAME_SLIM
		elif type == "BasicInfo" or type == "IDInfo":
			self.type = self.BASIC_INFO
		elif type == "CryptInfo":
			self.type = self.CRYPT_INFO

	@cached
	def getText(self):
		if self.type == self.SYSTEM:
			return "System: %s" % emud.getInfoSystem()
		elif self.type == self.CAID:
			return "CaID: %s" % emud.getInfoCaID()
		elif self.type == self.PID:
			return "Pid: %s" % emud.getInfoPid()
		elif self.type == self.PROTOCOL:
			return "Protocol: %s" % emud.getInfoProtocol()
		elif self.type == self.ADDRESS:
			return "Address: %s" % emud.getInfoAddress()
		elif self.type == self.PROVID:
			return "ProvID: %s" % emud.getInfoProvID()
		elif self.type == self.TIME:
			return "Delay time (ms): %s" % emud.getInfoTime()
		elif self.type == self.HOPS:
			return "Hops: %s" % emud.getInfoHops()
		elif self.type == self.CW0:
			return "CW0: %s" % emud.getInfoCW0()
		elif self.type == self.CW1:
			return "CW1: %s" % emud.getInfoCW1()
		elif self.type == self.NAME:
			return "Name: %s" % emud.getInfoName()
		elif self.type == self.NAME_SLIM:
			return emud.getInfoName()
		elif self.type == self.BASIC_INFO:
			return "%s %s:%s %s" % (emud.getInfoSystem(), emud.getInfoCaID(), emud.getInfoProvID(), emud.getInfoPid())
		elif self.type == self.CRYPT_INFO:
			return "CaID: %s Pid: %s" % (emud.getInfoCaID(), emud.getInfoPid())
		return "Error"
		
	text = property(getText)
