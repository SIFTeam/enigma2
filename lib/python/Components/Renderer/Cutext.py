#
#
#    Usage:
#    <widget source="session.Event_Now" render="vCutext" noWrap="1" .......... />
#



from Renderer import Renderer
from enigma import eLabel
from Components.VariableText import VariableText
from Components.config import config 


class Cutext(VariableText, Renderer):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)

	GUI_WIDGET = eLabel

	def connect(self, source):
		Renderer.connect(self, source)
		self.changed((self.CHANGED_DEFAULT,))

	def changed(self, what):
		if what[0] == self.CHANGED_CLEAR:
			self.text = ""
		else:
			if (len(self.text) > 25):
				self.text = (self.text[:29] + '...')
			else:
				self.text = self.source.text




