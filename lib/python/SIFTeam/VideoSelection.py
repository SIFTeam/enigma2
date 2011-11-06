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

from Extra.ExtraMessageBox import ExtraMessageBox
from Extra.ExtrasList import ExtrasList, SimpleEntry

class VideoSelectionHelper():
    def __init__(self, session):
        self.session = session
        self.videomodes = ["4_3_letterbox", "4_3_panscan", "16_9", "16_9_always", "16_10_letterbox", "16_10_panscan", "16_9_letterbox"]
        self.videodescs = ["4:3 Letterbox", "4:3 Panscan", "16:9", "16:9 Always", "16:10 Letterbox", "16:10 Panscan", "16:9 Letterbox"]
        
    def changeMode(self):
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
        
        if len(self.videomodes_enabled) < 2:
            return
        
        iAVSwitch = AVSwitch()
        aspectnum = iAVSwitch.getAspectRatioSetting()
        if aspectnum >= len(self.videomodes):
            aspectnum = 0
            
        currentmode = self.videomodes[aspectnum]
        
        aspectnum = 0
        for i in range(0, len(self.videomodes_enabled)):
            if self.videomodes_enabled[i] == currentmode:
                aspectnum = i
                break
                
        aspectnum += 1
        if aspectnum >= len(self.videomodes_enabled):
            aspectnum = 0
            
        newmode = self.videomodes_enabled[aspectnum]
        
        aspectnum = 0
        for i in range(0, len(self.videomodes)):
            if self.videomodes[i] == newmode:
                aspectnum = i
                break
                
        iAVSwitch.setAspectRatio(aspectnum)
        config.av.aspectratio.setValue(self.videomodes[aspectnum])
        self.session.open(VideoSelectionNotify, self.videodescs[aspectnum])

class VideoSelectionNotify(Screen):
    def __init__(self, session, text):
        Screen.__init__(self, session)
        self.session = session
        self["text"] = Label(text)
        
        self.timer = eTimer()
        self.timer.callback.append(self.close)
        self.timer.start(2000, 1)
        
        self["actions"] = ActionMap(["SetupActions", "ColorActions"], 
            {
                "green": self.next
            })
            
    def next(self):
        self.timer.stop()
        vm = VideoSelectionHelper(self.session)
        vm.changeMode()
        self.close()
        