from Screens.Screen import Screen
#from Components.Sources.Source import ObsoleteSource

class SkinDeveloperSummary(Screen):
	skin = """
	<screen position="0,0" size="132,64">
		<widget source="parent.DeveloperTag" render="Label" position="6,4" size="120,42" font="Regular;18" />
	</screen>"""
	def __init__(self, session, parent):

		Screen.__init__(self, session, parent = parent)

		names = parent.skinName
		if not isinstance(names, list):
		  names = [names]

		self.skinName = [ x + "_summary" for x in names ]
		self.skinName.append("SkinDeveloperSummary")

		# if parent has a "skin_summary" defined, use that as default
		self.skin = parent.__dict__.get("skin_summary", self.skin)
		
	def updateProgress(self, value):
		pass
		
	def updateService(self, name):
		pass