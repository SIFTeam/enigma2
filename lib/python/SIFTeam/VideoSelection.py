from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Components.config import getConfigListEntry, config
from Components.ConfigList import ConfigList
from Tools.Directories import fileExists
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from PanelConfig import MenuConfig, PanelExec
from Components.config import KEY_LEFT, KEY_RIGHT, config
from Components.AVSwitch import AVSwitch
from Components.Label import Label
from Components.Sources.List import List

from Extra.ExtraMessageBox import ExtraMessageBox
from Extra.ExtrasList import ExtrasList, SimpleEntry

class VideoSelectionMenu(Screen):
	skin = """<screen name="VideoSelectionMenu" position="center,center" size="400,250" title="Video Format Selection" backgroundColor="#000000">
		<widget source="menu" render="Listbox" position="0,0" size="400,250" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{"template": [
					MultiContentEntryText(pos = (10, 5), size = (360, 30), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),
					],
					"fonts": [gFont("Regular", 22)],
					"itemHeight": 40
				}
			</convert>
		</widget>
	</screen>"""
	
	videomodes = ["4_3_letterbox", "4_3_panscan", "16_9", "16_9_always", "16_10_letterbox", "16_10_panscan", "16_9_letterbox"]
	videodescs = ["4:3 Letterbox", "4:3 Panscan", "16:9", "16:9 Always", "16:10 Letterbox", "16:10 Panscan", "16:9 Letterbox"]
	
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session

		self['menu'] = List([])
		self["actions"] = ActionMap(["SetupActions"],
		{
			"ok": self.ok,
			"cancel": self.quit
		}, -2)
		
		self.onLayoutFinish.append(self.draw)
		
	def draw(self):
		self.drawList = []
		self.listindex = 0
		self.videomodes_enabled = []
		if config.sifteam.switch_4_3_letterbox.value == True:
			self.videomodes_enabled.append("4_3_letterbox")
		if config.sifteam.switch_4_3_panscan.value == True:
			self.videomodes_enabled.append("4_3_panscan")
		if config.sifteam.switch_16_9.value == True:
			self.videomodes_enabled.append("16_9")
		if config.sifteam.switch_16_9_always.value == True:
			self.videomodes_enabled.append("16_9_always")
		if config.sifteam.switch_16_10_letterbox.value == True:
			self.videomodes_enabled.append("16_10_letterbox")
		if config.sifteam.switch_16_10_panscan.value == True:
			self.videomodes_enabled.append("16_10_panscan")
		if config.sifteam.switch_16_9_letterbox.value == True:
			self.videomodes_enabled.append("16_9_letterbox")
		
		try:
			iAVSwitch = AVSwitch()
			current_videomode = self.videomodes[iAVSwitch.getAspectRatioSetting()]
			self.listindex = self.videomodes_enabled.index(current_videomode)
		except Exception:
			pass
		
		for videomode in self.videomodes_enabled:
			index = self.videomodes.index(videomode)
			self.drawList.append((_(self.videodescs[index]),))
			
		self["menu"].setList(self.drawList)
		self["menu"].setIndex(self.listindex)
    
	def ok(self):
		index = self['menu'].getIndex()
		videomode = self.videomodes_enabled[index]
		
		iAVSwitch = AVSwitch()
		iAVSwitch.setAspectRatio(self.videomodes.index(videomode))
		config.av.aspectratio.setValue(videomode)
		self.close()
		
	def quit(self):
		self.close()