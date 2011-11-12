import os
import re

class Disks():
	ptypes = {
	 "0": "Empty"             , "24":  "NEC DOS"        , "81":  "Minix / old Lin"     , "bf":  "Solaris",
	 "1": "FAT12"             , "39":  "Plan 9"         , "82":  "Linux swap / Solaris", "c1":  "DRDOS/sec (FAT)",
	 "2": "XENIX root"        , "3c":  "PartitionMagic" , "83":  "Linux"               , "c4":  "DRDOS/sec (FAT)",
	 "3": "XENIX usr"         , "40":  "Venix 80286"    , "84":  "OS/2 hidden C:"      , "c6":  "DRDOS/sec (FAT)",
	 "4": "FAT16 <32M"        , "41":  "PPC PReP Boot"  , "85":  "Linux extended"      , "c7":  "Syrinx",
	 "5": "Extended"          , "42":  "SFS"            , "86":  "NTFS volume set"     , "da":  "Non-FS data",
	 "6": "FAT16"             , "4d":  "QNX4.x"         , "87":  "NTFS volume set"     , "db":  "CP/M / CTOS",
	 "7": "HPFS/NTFS"         , "4e":  "QNX4.x 2nd part", "88":  "Linux plaintext"     , "de":  "Dell Utility",
	 "8": "AIX"               , "4f":  "QNX4.x 3rd part", "8e":  "Linux LVM"           , "df":  "BootIt",
	 "9": "AIX bootable"      , "50":  "OnTrack DM"     , "93":  "Amoeba"              , "e1":  "DOS access",
	 "a": "OS/2 Boot Manager" , "51":  "OnTrack DM6 Aux", "94":  "Amoeba BBT"          , "e3":  "DOS R/O",
	 "b": "W95 FAT32"         , "52":  "CP/M"           , "9f":  "BSD/OS"              , "e4":  "SpeedStor",
	 "c": "W95 FAT32 (LBA)"   , "53":  "OnTrack DM6 Aux", "a0":  "IBM Thinkpad hi"     , "eb":  "BeOS fs",
	 "e": "W95 FAT16 (LBA)"   , "54":  "OnTrackDM6"     , "a5":  "FreeBSD"             , "ee":  "GPT",
	 "f": "W95 Ext'd (LBA)"   , "55":  "EZ-Drive"       , "a6":  "OpenBSD"             , "ef":  "EFI",
	"10": "OPUS"              , "56":  "Golden Bow"     , "a7":  "NeXTSTEP"            , "f0":  "Linux/PA-RISC",
	"11": "Hidden FAT12"      , "5c":  "Priam Edisk"    , "a8":  "Darwin UFS"          , "f1":  "SpeedStor",
	"12": "Compaq diagnostic" , "61":  "SpeedStor"      , "a9":  "NetBSD"              , "f4":  "SpeedStor",
	"14": "Hidden FAT16"      , "63":  "GNU HURD"       , "ab":  "Darwin boot"         , "f2":  "DOS secondary",
	"16": "Hidden FAT16"      , "64":  "Novell Netware" , "af":  "HFS / HFS+"          , "fb":  "VMware VMFS",
	"17": "Hidden HPFS/NTFS"  , "65":  "Novell Netware" , "b7":  "BSDI fs"             , "fc":  "VMware VMKCORE",
	"18": "AST SmartSleep"    , "70":  "DiskSecure Mult", "b8":  "BSDI swap"           , "fd":  "Linux raid auto",
	"1b": "Hidden W95 FAT32"  , "75":  "PC/IX"          , "bb":  "Boot Wizard hidden"  , "fe":  "LANstep",
	"1c": "Hidden W95 FAT32"  , "80":  "Old Minix"      , "be":  "Solaris boot"        , "ff":  "BBT",
	"1e": "Hidden W95 FAT16" }
	
	def __init__(self):
		self.disks = []
		self.readDisks()
		self.readPartitions()
		
	def readDisks(self):
		partitions = open("/proc/partitions")
		for part in partitions:
			res = re.sub("\s+", " ", part).strip().split(" ")
			if res and len(res) == 4:
				if len(res[3]) == 3 and res[3][:2] == "sd":
					self.disks.append([ res[3],
										int(res[2]) * 1024,
										self.isRemovable(res[3]),
										self.getModel(res[3]),
										self.getVendor(res[3]),
										[ ] ])
		
	def readPartitions(self):
		partitions = open("/proc/partitions")
		for part in partitions:
			res = re.sub("\s+", " ", part).strip().split(" ")
			if res and len(res) == 4:
				if len(res[3]) > 3 and res[3][:2] == "sd":
					for i in self.disks:
						if i[0] == res[3][:3]:
							i[5].append([ res[3], int(res[2]) * 1024, self.isLinux(res[3]) ])
							break
							
	def isRemovable(self, device):
		removable = open("/sys/block/%s/removable" % device, "r").read().strip()
		if removable == "1":
			return True
		return False
		
	# in this case device is full device with slice number... for example sda1
	def isLinux(self, device):
		cmd = "/usr/sbin/sfdisk -c /dev/%s %s" % (device[:3], device[3:])
		fdisk = os.popen(cmd, "r")
		res = fdisk.read().strip()
		fdisk.close()
		if res in self.ptypes.keys():
			return self.ptypes[res]
		return res
		
	def getModel(self, device):
		return open("/sys/block/%s/device/model" % device, "r").read().strip()
		
	def getVendor(self, device):
		return open("/sys/block/%s/device/vendor" % device, "r").read().strip()
		
	def isMounted(self, device):
		mounts = open("/proc/mounts")
		for mount in mounts:
			res = mount.split(" ")
			if res and len(res) > 1:
				if res[0][:8] == "/dev/%s" % device:
					mounts.close()
					return True
		mounts.close()
		return False
		
	def isMountedP(self, device, partition):
		mounts = open("/proc/mounts")
		for mount in mounts:
			res = mount.split(" ")
			if res and len(res) > 1:
				if res[0][:9] == "/dev/%s%s" % (device, partition):
					mounts.close()
					return True
		mounts.close()
		return False
	
	def getMountedP(self, device, partition):
		mounts = open("/proc/mounts")
		for mount in mounts:
			res = mount.split(" ")
			if res and len(res) > 1:
				if res[0] == "/dev/%s%d" % (device, partition):
					mounts.close()
					return res[1]
		mounts.close()
		return None
		
	def umount(self, device):
		mounts = open("/proc/mounts")
		for mount in mounts:
			res = mount.split(" ")
			if res and len(res) > 1:
				if res[0][:8] == "/dev/%s" % device:
					print "umount %s" % res[0]
					if os.system("umount %s" % res[0]) != 0:
						mounts.close()
						return False
		mounts.close()
		return True
		
	def umountP(self, device, partition):
		if os.system("umount /dev/%s%d" % (device, partition)) != 0:
			return False
			
		return True
			
	def mountP(self, device, partition, path):
		if os.system("mount /dev/%s%d %s" % (device, partition, path)) != 0:
			return False
		return True
		
	def mount(self, fdevice, path):
		if os.system("mount /dev/%s %s" % (fdevice, path)) != 0:
			return False
		return True
		
	# type:
	# 0 -> one partition
	# 1 -> two partition (2 x 50%)
	# 2 -> two partition (75% 25%)
	# 3 -> three partition (3 x 33%)
	# 4 -> four partition (4 x 25%)
	#
	# return value:
	# 0 -> ok
	# -1 -> umount failed
	# -2 -> sfdisk failed
	def fdisk(self, device, size, type):
		print "partitioning device %s" % device
		if self.isMounted(device):
			print "device is mounted... umount"
			if not self.umount(device):
				print "umount failed!"
				return -1
			
		if type == 0:
			flow = "0,\n;\n;\n;\ny\n"
		elif type == 1:
			psize = (size / (1024*1024)) / 2
			flow = ",%d\n;\n;\n;\ny\n" % psize
		elif type == 2:
			psize = ((size / (1024*1024)) / 4) * 3
			flow = ",%d\n;\n;\n;\ny\n" % psize
		elif type == 3:
			psize = (size / (1024*1024)) / 3
			flow = ",%d\n,%d\n;\n;\ny\n" % (psize, psize)
		elif type == 4:
			psize = (size / (1024*1024)) / 4
			flow = ",%d\n,%d\n,%d\n;\ny\n" % (psize, psize, psize)
		
		cmd = "%s -f -uM /dev/%s" % ("/usr/sbin/sfdisk", device)
		sfdisk = os.popen(cmd, "w")
		sfdisk.write(flow)
		if sfdisk.close():
			return -2
			
		return 0
		
	# return value:
	# 0 -> ok
	# -1 -> umount failed
	# -2 -> sfdisk failed
	def chkfs(self, device, partition):
		fdevice = "%s%d" % (device, partition)
		print "checking device %s" % fdevice
		if self.isMountedP(device, partition):
			oldmp = self.getMountedP(device, partition)
			print "partition is mounted... umount"
			if not self.umountP(device, partition):
				print "umount failed!"
				return -1
		else:
			oldmp = ""

		if self.isMountedP(device, partition):
				return -1
			
		ret = os.system("/sbin/fsck /dev/%s" % fdevice)
		
		if len(oldmp) > 0:
			self.mount(fdevice, oldmp)
			
		if ret == 0:
			return 0
		return -2;
		
	def mkfs(self, device, partition):
		dev = "%s%d" % (device, partition)
		size = 0
		partitions = open("/proc/partitions")
		for part in partitions:
			res = re.sub("\s+", " ", part).strip().split(" ")
			if res and len(res) == 4:
				if res[3] == dev:
					size = int(res[2])
					break
					
		if size == 0:
			return -1
			
		if self.isMountedP(device, partition):
			oldmp = self.getMountedP(device, partition)
			print "partition is mounted... umount"
			if not self.umountP(device, partition):
				print "umount failed!"
				return -2
		else:
			oldmp = ""
				
		cmd = "/sbin/mkfs.ext2 "
		if size > 4 * 1024 * 1024 * 1024:
			cmd += "-T largefile "
		cmd += "-m0 /dev/" + dev
		ret = os.system(cmd)
		
		if len(oldmp) > 0:
			self.mount(dev, oldmp)
			
		if ret == 0:
			return 0
		return -3;
