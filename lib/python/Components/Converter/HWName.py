from Components.Converter.Converter import Converter
from Components.Element import cached

from SIFTeam.Extra.HWType import hwtype

class HWName(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)

	@cached
	def getText(self):
		if hwtype == "dm800":
			return "DM 800"
		elif hwtype == "dm800se":
			return "DM 800se"
		elif hwtype == "dm8000":
			return "DM 8000"
		elif hwtype == "dm500hd":
			return "DM 500hd"
		elif hwtype == "bm750":
			return "Vu+ Duo"
		elif hwtype == "vusolo":
			return "Vu+ Solo"
		elif hwtype == "et9000":
			return "CTech et9000"
		elif hwtype == "et5000":
			return "XTrend et5000"
			
		return ""

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)




