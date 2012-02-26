##
## ServiceNumber Renderer
## by AliAbdul adapted from sifteam
##
## Example usage in the skin.xml:
## <widget source="session.CurrentService" render="ServiceNumber" position="90,406" size="30,24" font="Regular;20" transparent="1" />
##
## Known issues:
## If you have a service in different bouquets the first one in the list will be taken
## If you rename, move, delete or add a channel the complete numbers will be not shown right. You have to restart E2 then
##
from Components.VariableText import VariableText
from enigma import eLabel, iServiceInformation, eServiceReference, eServiceCenter
from Renderer import Renderer
from SIFTeam.Extra.ServiceList import *
##########################################################################

class ServiceNumber(Renderer, VariableText):
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
					self.text = str(idx)
					break
		else:
			self.text = ""
