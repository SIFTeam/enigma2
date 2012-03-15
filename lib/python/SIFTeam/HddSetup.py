from enigma import *
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Components.Button import Button
from Components.Label import Label
from Screens.MessageBox import MessageBox
from HddPartitions import HddPartitions
from HddInfo import HddInfo
from Extra.Disks import Disks
from Extra.ExtraMessageBox import ExtraMessageBox
from Extra.ExtraActionBox import ExtraActionBox
from Extra.MountPoints import MountPoints

import os
import sys

def DiskEntry(model, size, removable):
	if removable:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/diskusb.png"));
	else:
		picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/sifteam_others/disk.png"));
		
	return (picture, model, size)
	
class HddSetup(Screen):
	def __init__(self, session, args = 0):
		self.session = session
		
		Screen.__init__(self, session)
		self.disks = list ()
		
		self.mdisks = Disks()
		for disk in self.mdisks.disks:
			capacity = "%d MB" % (disk[1] / (1024 * 1024))
			self.disks.append(DiskEntry(disk[3], capacity, disk[2]))
		
		self["menu"] = List(self.disks)
		self["key_red"] = Button(_("Mounts"))
		self["key_green"] = Button(_("Info"))
		self["key_yellow"] = Button(_("Initialize"))
		self["key_blue"] = Button(_("Exit"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"yellow": self.yellow,
			"green": self.green,
			"red": self.red,
			"cancel": self.quit,
		}, -2)
	
	def mkfs(self):
		self.formatted += 1
		return self.mdisks.mkfs(self.mdisks.disks[self.sindex][0], self.formatted, self.fsresult)
		
	def refresh(self):
		self.disks = list ()
		
		self.mdisks = Disks()
		for disk in self.mdisks.disks:
			capacity = "%d MB" % (disk[1] / (1024 * 1024))
			self.disks.append(DiskEntry(disk[3], capacity, disk[2]))
			
		self["menu"].setList(self.disks)
		
	def checkDefault(self):
		mp = MountPoints()
		mp.read()
		if not mp.exist("/hdd"):
			mp.add(self.mdisks.disks[self.sindex][0], 1, "/hdd")
			mp.write()
			mp.mount(self.mdisks.disks[self.sindex][0], 1, "/hdd")
			os.system("/bin/mkdir /hdd/movie")
			os.system("/bin/mkdir /hdd/music")
			os.system("/bin/mkdir /hdd/picture")
		
	def format(self, result):
		if result != 0:
			self.session.open(MessageBox, _("Cannot format partition %d" % self.formatted), MessageBox.TYPE_ERROR)
		if self.result == 0:
			if self.formatted > 0:
				self.checkDefault()
				self.refresh()
				return
		elif self.result > 0 and self.result < 3:
			if self.formatted > 1:
				self.checkDefault()
				self.refresh()
				return
		elif self.result == 3:
			if self.formatted > 2:
				self.checkDefault()
				self.refresh()
				return
		elif self.result == 4:
			if self.formatted > 3:
				self.checkDefault()
				self.refresh()
				return
				
		self.session.openWithCallback(self.format, ExtraActionBox, "Formatting partition %d" % (self.formatted + 1), "Initialize disk", self.mkfs)
		
	def fdiskEnded(self, result):
		if result == 0:
			self.format(0)
		elif result == -1:
			self.session.open(MessageBox, _("Cannot umount device.\nA record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem.\nPlease stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
		else:
			self.session.open(MessageBox, _("Partitioning failed!"), MessageBox.TYPE_ERROR)

	def fdisk(self):
		return self.mdisks.fdisk(self.mdisks.disks[self.sindex][0], self.mdisks.disks[self.sindex][1], self.result, self.fsresult)

	def initialaze(self, result):
		if result != 4:
			self.fsresult = result
			self.formatted = 0
			mp = MountPoints()
			mp.read()
			mp.deleteDisk(self.mdisks.disks[self.sindex][0])
			mp.write()
			self.session.openWithCallback(self.fdiskEnded, ExtraActionBox, "Partitioning...", "Initialize disk", self.fdisk)
		
	def chooseFSType(self, result):
		if result != 5:
			self.result = result
			self.session.openWithCallback(self.initialaze, ExtraMessageBox, "Please select your preferred configuration.", "HDD Partitioner",
										[ [ "Ext4", "partitionmanager.png" ],
										[ "Ext3", "partitionmanager.png" ],
										[ "NTFS", "partitionmanager.png" ],
										[ "Fat32", "partitionmanager.png" ],
										[ "Cancel", "cancel.png" ],
										], 1, 4)
		
	def yellow(self):
		if len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getIndex()
			self.session.openWithCallback(self.chooseFSType, ExtraMessageBox, "Please select your preferred configuration.", "HDD Partitioner",
										[ [ "One partition", "partitionmanager.png" ],
										[ "Two partitions (50% - 50%)", "partitionmanager.png" ],
										[ "Two partitions (75% - 25%)", "partitionmanager.png" ],
										[ "Three partitions (33% - 33% - 33%)", "partitionmanager.png" ],
										[ "Four partitions (25% - 25% - 25% - 25%)", "partitionmanager.png" ],
										[ "Cancel", "cancel.png" ],
										], 1, 5)
		
	def green(self):
		if len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getIndex()
			self.session.open(HddInfo, self.mdisks.disks[self.sindex][0])
		
	def red(self):
		if len(self.mdisks.disks) > 0:
			self.sindex = self['menu'].getIndex()
			if len(self.mdisks.disks[self.sindex][5]) == 0:
				self.session.open(MessageBox, _("You need to initialize your usb storage device first"), MessageBox.TYPE_ERROR)
			else:
				self.session.open(HddPartitions, self.mdisks.disks[self.sindex])
		
	def quit(self):
		self.close()
