from Renderer import Renderer
from enigma import eLabel
from enigma import ePoint, eTimer
from Components.VariableText import VariableText

class Roller(VariableText, Renderer):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		self.skinsize = (0, 0)
		self.skinposition = (0, 0)
		self.maxwidth = 0
		self.timer = eTimer()
		self.timer.callback.append(self.tick)
		
	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
			if (attrib == 'size'):
				tmp = value.split(",")
				self.skinsize = (int(tmp[0]), int(tmp[1]))
				attribs.append((attrib, value))
			elif (attrib == 'position'):
				tmp = value.split(",")
				self.skinposition = (int(tmp[0]), int(tmp[1]))
				attribs.append((attrib, value))
			elif (attrib == 'maxWidth'):
				self.maxwidth = int(value)
			else:
				attribs.append((attrib, value))
				
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)
		
	GUI_WIDGET = eLabel
	
	def connect(self, source):
		Renderer.connect(self, source)
		self.changed((self.CHANGED_DEFAULT,))

	def changed(self, what):
		self.timer.stop()

		if (what[0] == self.CHANGED_CLEAR):
			self.text = ''
		else:
			self.text = self.source.text
			
		if self.instance:
			self.instance.move(ePoint(self.skinposition[0], self.skinposition[1]))
			s = self.instance.calculateSize()
			if s.width() > self.maxwidth:
				self.offset = s.width() - self.maxwidth + 40
				self.x = self.skinposition[0]
				self.timer.start(2000, 1)
				
	def tick(self):
		self.timer.stop()
		if self.x > self.skinposition[0] - self.offset:
			self.x = self.x - 2
			self.instance.move(ePoint(self.x, self.skinposition[1]))
			self.timer.start(50, 1)
		else:
			self.instance.move(ePoint(self.skinposition[0], self.skinposition[1]))
			
			self.curtext = self.text[:-3]
			self.text = "%s..." % self.curtext
			while len(self.curtext) > 0:
				s = self.instance.calculateSize()
				if s.width() <= self.maxwidth:
					break
				
				self.curtext = self.curtext[:-1]
				self.text = "%s..." % self.curtext
				
