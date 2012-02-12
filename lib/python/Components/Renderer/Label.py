from Components.VariableText import VariableText
from Renderer import Renderer

from enigma import eLabel

class Label(VariableText, Renderer):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		self.forced = False
		
	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, what,) in self.skinAttributes:
			if (attrib == 'text'):
				self.setText(what)
				self.forced=True
			else:
				attribs.append((attrib, what))
		return Renderer.applySkin(self, desktop, parent)
		
	GUI_WIDGET = eLabel

	def connect(self, source):
		Renderer.connect(self, source)
		self.changed((self.CHANGED_DEFAULT,))

	def changed(self, what):
		if self.forced:
			return
			
		# it could be called before the applyskin
		try:
			if what[0] == self.CHANGED_CLEAR:
				self.text = ""
			else:
				self.text = self.source.text
		except Exception, e:
			pass

