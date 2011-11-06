from Converter import Converter
from enigma import eListboxPythonMultiContent, gFont, loadPNG
from Components.Element import cached
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_SKIN

def MenuEntry(name, picture):
	res = [(picture, name)]
	picture = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_panel/" + picture + ".png")
	#print picture
	
	if fileExists(picture):
		res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(48, 48), png=loadPNG(picture)))
	res.append(MultiContentEntryText(pos=(60, 10), size=(420, 38), font=0, text=name))
		
	return res

class MenuList(Converter):
	"""Turns a simple python list into a list which can be used in a listbox."""
	def __init__(self, type):
		Converter.__init__(self, type)
		self.content = None
		self.newlist = None

	def changed(self, what):
		if not self.content:
			self.content = eListboxPythonMultiContent()
			self.content.setFont(0, gFont('Regular', 21))
			self.content.setItemHeight(48)

		if self.source:
			self.newlist = []
			for item in self.source.list:
				self.newlist.append(MenuEntry(item[0], item[2]))
			self.content.setList(self.newlist)
		self.downstream_elements.changed(what)

	def selectionChanged(self, index):
		self.source.selectionChanged(index)

	def setIndex(self, index):
		# update all non-master targets
		print "changed selection in listbox!"
		for x in self.downstream_elements:
			print "downstream element", x
			if x is not self.master:
				print "is not master, so update to index", index
				x.index = index

	def getIndex(self, index):
		return None
	
	index = property(getIndex, setIndex)

	@cached
	def getCurrent(self):
		if self.source.list is None or self.index is None or self.index >= len(self.source.list):
			return None
		return self.source.list[self.index]

	current = property(getCurrent)

	# pass through: getIndex / setIndex to master
	@cached
	def getIndex(self):
		if self.master is None:
			return None
		return self.master.index

	def setIndex(self, index):
		if self.master is not None:
			self.master.index = index

	index = property(getIndex, setIndex)

	def entry_changed(self, index):
		if self.content:
			self.content.invalidateEntry(index)