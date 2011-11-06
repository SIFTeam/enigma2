# copied from ServiceNumber.py

from Components.VariableText import VariableText
from enigma import eLabel, iServiceInformation, eServiceReference, eServiceCenter
from Renderer import Renderer
from SIFTeam.Extra.ServiceList import *

class ServiceName(Renderer, VariableText):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		global servicelist
		if len(servicelist) == 0:
			initServiceList()
			
	GUI_WIDGET = eLabel

	def changed(self, what):
		global servicelist
		service = self.source.service
		info = service and service.info()
		if info is None:
			self.text = ""
			return
		
		name = info.getName().replace('\xc2\x86', '').replace('\xc2\x87', '')
		
		if name in servicelist:
			for idx in range(1, len(servicelist)):
				if name == servicelist[idx-1]:
					self.text = str(idx)+". "+name
					break
		else:
			self.text = name

