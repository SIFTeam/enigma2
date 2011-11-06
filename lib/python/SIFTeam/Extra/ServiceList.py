from Components.VariableText import VariableText
#from Components.config import config
from enigma import eLabel, iServiceInformation, eServiceReference, eServiceCenter

servicelist = []
radioservicelist = []

def initServiceList():
	getList()
	getRadioList()

def getList():
	global servicelist
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) || (type == 134) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
	bouquets = services and services.getContent("SN", True)
	
	for bouquet in bouquets:
		list = serviceHandler.list(eServiceReference(bouquet[0]))
		if list:
			while True:
				s = list.getNext()
				#print s
				if not s.valid():
					break
				if not (s.flags & (eServiceReference.isDirectory | eServiceReference.isMarker | eServiceReference.isGroup)):
					info = serviceHandler.info(s)
					if info:
						servicelist.append(info.getName(s).replace('\xc2\x86', '').replace('\xc2\x87', ''))
						
def getRadioList():
	global radioservicelist
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('1:7:2:0:0:0:0:0:0:0:(type == 2) FROM BOUQUET "bouquets.radio" ORDER BY bouquet'))
	bouquets = services and services.getContent("SN", True)
	
	for bouquet in bouquets:
		list = serviceHandler.list(eServiceReference(bouquet[0]))
		if list:
			while True:
				s = list.getNext()
				#print s
				if not s.valid():
					break
				if not (s.flags & (eServiceReference.isDirectory | eServiceReference.isMarker | eServiceReference.isGroup)):
					info = serviceHandler.info(s)
					if info:
						radioservicelist.append(info.getName(s).replace('\xc2\x86', '').replace('\xc2\x87', ''))
