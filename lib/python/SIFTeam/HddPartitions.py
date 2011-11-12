from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Components.Button import Button
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Extra.Disks import Disks
from Extra.ExtraActionBox import ExtraActionBox
from Extra.MountPoints import MountPoints
from HddMount import HddMount

import os
import sys

def PartitionEntry(description, size):
	picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/partitionmanager.png"));
		
	return (picture, description, size)

class HddPartitions(Screen):
	def __init__(self, session, disk):
		self.session = session
		
		Screen.__init__(self, session)
		self.disk = disk
		self.refreshMP(False)
		
		self["menu"] = List(self.partitions)
		self["menu"].onSelectionChanged.append(self.selectionChanged)
		self["key_red"] = Button("")
		self["key_green"] = Button("")
		self["key_yellow"] = Button("")
		self["key_blue"] = Button(_("Exit"))
		self["label_disk"] = Label("%s - %s" % (self.disk[0], self.disk[3]))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"yellow": self.yellow,
			"green": self.green,
			"red": self.red,
			"cancel": self.quit,
		}, -2)
		
		if len(self.disk[5]) > 0:
			if self.disk[5][0][2] == "Linux":
				self["key_green"].setText(_("Check"))
				self["key_yellow"].setText(_("Format"))
				
		if self.disk[5][0][2] == "Linux swap":
			self["key_red"].setText("")
		else:
			mp = self.mountpoints.get(self.disk[0], 1)
			rmp = self.mountpoints.getRealMount(self.disk[0], 1)
			if len(mp) > 0 or len(rmp) > 0:
				self.mounted = True
				self["key_red"].setText(_("Umount"))
			else:
				self.mounted = False
				self["key_red"].setText(_("Mount"))
		
	def selectionChanged(self):
		self["key_green"].setText("")
		self["key_yellow"].setText("")
		if len(self.disk[5]) > 0:
			index = self["menu"].getIndex()
			if self.disk[5][index][2] == "Linux":
				self["key_green"].setText(_("Check"))
				self["key_yellow"].setText(_("Format"))
				
			if self.disk[5][index][2] == "Linux swap":
				self["key_red"].setText("")
			else:
				mp = self.mountpoints.get(self.disk[0], index+1)
				rmp = self.mountpoints.getRealMount(self.disk[0], index+1)
				if len(mp) > 0 or len(rmp) > 0:
					self.mounted = True
					self["key_red"].setText(_("Umount"))
				else:
					self.mounted = False
					self["key_red"].setText(_("Mount"))
				
	def chkfs(self):
		disks = Disks()
		ret = disks.chkfs(self.disk[5][self.index][0][:3], self.index+1)
		if ret == 0:
			self.session.open(MessageBox, _("Check disk terminated with success"), MessageBox.TYPE_INFO)
		elif ret == -1:
			self.session.open(MessageBox, _("Cannot umount current drive.\nA record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem.\nPlease stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
		else:
			self.session.open(MessageBox, _("Error checking disk. The disk may be damaged"), MessageBox.TYPE_ERROR)
			
	def mkfs(self):
		disks = Disks()
		ret = disks.mkfs(self.disk[5][self.index][0][:3], self.index+1)
		if ret == 0:
			self.session.open(MessageBox, _("Format terminated with success"), MessageBox.TYPE_INFO)
		elif ret == -2:
			self.session.open(MessageBox, _("Cannot format current drive.\nA record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem.\nPlease stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
		else:
			self.session.open(MessageBox, _("Error formatting disk. The disk may be damaged"), MessageBox.TYPE_ERROR)
			
	def green(self):
		if len(self.disk[5]) > 0:
			index = self["menu"].getIndex()
			if self.disk[5][index][2] == "Linux":
				self.index = index
				self.session.open(ExtraActionBox, "Checking disk %s" % self.disk[5][index][0], "Checking disk", self.chkfs)
				
	def yellow(self):
		if len(self.disk[5]) > 0:
			index = self["menu"].getIndex()
			if self.disk[5][index][2] == "Linux":
				self.index = index
				self.session.open(ExtraActionBox, "Formatting disk %s" % self.disk[5][index][0], "Formatting disk", self.mkfs)
				
	def refreshMP(self, uirefresh = True):
		self.partitions = []
		self.mountpoints = MountPoints()
		self.mountpoints.read()
		count = 1
		for part in self.disk[5]:
			capacity = "%d MB" % (part[1] / (1024 * 1024))
			mp = self.mountpoints.get(self.disk[0], count)
			rmp = self.mountpoints.getRealMount(self.disk[0], count)
			if len(mp) > 0:
				self.partitions.append(PartitionEntry("P. %d - %s (Fixed: %s)" % (count, part[2], mp), capacity))
			elif len(rmp) > 0:
				self.partitions.append(PartitionEntry("P. %d - %s (Auto: %s)" % (count, part[2], rmp), capacity))
			else:
				self.partitions.append(PartitionEntry("P. %d - %s" % (count, part[2]), capacity))
			count += 1
		
		if uirefresh:
			self["menu"].setList(self.partitions)
		
	def red(self):
		if len(self.disk[5]) > 0:
			index = self["menu"].getIndex()
			if self.disk[5][index][2] == "Linux swap":
				return
				
		if len(self.partitions) > 0:
			self.sindex = self['menu'].getIndex()
			if self.mounted:
				mp = self.mountpoints.get(self.disk[0], self.sindex+1)
				rmp = self.mountpoints.getRealMount(self.disk[0], self.sindex+1)
				if len(mp) > 0:
					if self.mountpoints.isMounted(mp):
						if self.mountpoints.umount(mp):
							self.mountpoints.delete(mp)
							self.mountpoints.write()
						else:
							self.session.open(MessageBox, _("Cannot umount device.\nA record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem.\nPlease stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
					else:
						self.mountpoints.delete(mp)
						self.mountpoints.write()
				elif len(rmp) > 0:
					self.mountpoints.umount(rmp)
				self.refreshMP()
			else:
				self.session.openWithCallback(self.refreshMP, HddMount, self.disk[0], self.sindex+1)
		
	def quit(self):
		self.close()
