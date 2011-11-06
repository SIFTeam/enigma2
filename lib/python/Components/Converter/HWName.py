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
		elif hwtype == "dm7025hd":
			return "DM 7025hd"
		elif hwtype == "vuduo":
			return "Vu+ Duo"
		elif hwtype == "vusolo":
			return "Vu+ Solo"
		elif hwtype == "vuuno":
			return "Vu+ Uno"
		elif hwtype == "et9x00":
			return "Clark/Xtrend et9x00"
		elif hwtype == "et6x00":
			return "Clark/Xtrend et6x00"
		elif hwtype == "et5x00":
			return "Clark/XTrend et5x00"
			
		return ""

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)




