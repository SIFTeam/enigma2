from Components.Converter.Converter import Converter
from Components.Element import cached

from SIFTeam.Extra.HWType import getHWTypeText

class HWName(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)

	@cached
	def getText(self):
		return getHWTypeText()

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)




