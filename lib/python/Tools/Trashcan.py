import time
import os
import enigma
import Components.Task
from Components.config import config
from Components import Harddisk
from Components.GUIComponent import GUIComponent
from Components.VariableText import VariableText
from twisted.internet import threads

def getTrashFolder(path):
	# Returns trash folder without symlinks. Path may be file or directory or whatever.
	mountpoint = Harddisk.findMountPoint(os.path.realpath(path))
	movie = os.path.join(mountpoint, 'movie')
	if os.path.isdir(movie):
		mountpoint = movie
	return os.path.join(mountpoint, ".Trash")

def createTrashFolder(path):
	# Create and return trash folder for given file or dir
	trash = getTrashFolder(path)
	if not os.path.isdir(trash):
		print "[Trashcan] create:", trash
		os.mkdir(trash)
	return trash

def enumTrashFolders():
	# Walk through all Trash folders. This may access network
	# drives and similar, so might block for minutes.
	for mount in Harddisk.getProcMounts():
		if mount[1].startswith('/media/'):
			mountpoint = mount[1]
			movie = os.path.join(mountpoint, 'movie')
			if os.path.isdir(movie):
				mountpoint = movie
			result = os.path.join(mountpoint, ".Trash")
			if os.path.isdir(result):
				yield result

def get_size(start_path = '.'):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(start_path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_size += os.path.getsize(fp)
	return total_size

class Trashcan:
	def __init__(self):
		self.isCleaning = False
		self.session = None
		self.dirty = set()

	def init(self, session):
		self.session = session
		session.nav.record_event.append(self.gotRecordEvent)

	def markDirty(self, path):
		# Marks a path for purging, for when a recording on that
		# device starts or ends.
		if not path:
			return
		trash = getTrashFolder(path)
		self.dirty.add(trash)

	def gotRecordEvent(self, service, event):
		if (event == enigma.iRecordableService.evEnd):
			self.cleanIfIdle()

	def destroy(self):
		if self.session is not None:
			self.session.nav.record_event.remove(self.gotRecordEvent)
		self.session = None

	def __del__(self):
		self.destroy()

	def cleanIfIdle(self, path=None):
		# RecordTimer calls this when preparing a recording. That is a
		# nice moment to clean up. It also mentions the path, so mark
		# it as dirty.
		self.markDirty(path)
		if not self.dirty:
			return
		if self.isCleaning:
			print "[Trashcan] Cleanup already running"
			return
		if (self.session is not None) and self.session.nav.getRecordings():
			return
		self.isCleaning = True
		ctimeLimit = time.time() - (config.usage.movielist_trashcan_days.value * 3600 * 24)
		reserveBytes = 1024*1024*1024 * int(config.usage.movielist_trashcan_reserve.value)
		cleanset = self.dirty
		self.dirty = set()
		threads.deferToThread(purge, cleanset, ctimeLimit, reserveBytes).addCallbacks(self.cleanReady, self.cleanFail)

	def cleanReady(self, result=None):
		self.isCleaning = False
		# schedule another clean loop if needed (so we clean up all devices, not just one)
		self.cleanIfIdle()

	def cleanFail(self, failure):
		print "[Trashcan] ERROR in clean:", failure
		self.isCleaning = False

def purge(cleanset, ctimeLimit, reserveBytes):
	# Remove expired items from trash, and attempt to have
	# reserveBytes of free disk space.
	for trash in cleanset:
		if not os.path.isdir(trash):
			print "[Trashcan] No trash.", trash
			return 0
		diskstat = os.statvfs(trash)
		free = diskstat.f_bfree * diskstat.f_bsize
		bytesToRemove = reserveBytes - free 
		candidates = []
		print "[Trashcan] bytesToRemove", bytesToRemove, trash
		size = 0
		for root, dirs, files in os.walk(trash, topdown=False):
			for name in files:
				try:
					fn = os.path.join(root, name)
					st = os.stat(fn)
					if st.st_ctime < ctimeLimit:
						print "[Trashcan] Too old:", name, st.st_ctime
						enigma.eBackgroundFileEraser.getInstance().erase(fn)
						bytesToRemove -= st.st_size
					else:
						candidates.append((st.st_ctime, fn, st.st_size))
						size += st.st_size
				except Exception, e:
					print "[Trashcan] Failed to stat %s:"% name, e 
			# Remove empty directories if possible
			for name in dirs:
				try:
					os.rmdir(os.path.join(root, name))
				except:
					pass
		candidates.sort()
		# Now we have a list of ctime, candidates, size. Sorted by ctime (=deletion time)
		print "[Trashcan] Bytes to remove remaining:", bytesToRemove, trash
		for st_ctime, fn, st_size in candidates:
			if bytesToRemove < 0:
				break
			enigma.eBackgroundFileEraser.getInstance().erase(fn)
			bytesToRemove -= st_size
			size -= st_size
		print "[Trashcan] Size after purging:", size, trash
 
def cleanAll(trash):
	if not os.path.isdir(trash):
		print "[Trashcan] No trash.", trash
		return 0
	for root, dirs, files in os.walk(trash, topdown=False):
		for name in files:
			fn = os.path.join(root, name)
			try:
				enigma.eBackgroundFileEraser.getInstance().erase(fn)
			except Exception, e:
				print "[Trashcan] Failed to erase %s:"% name, e
		# Remove empty directories if possible
		for name in dirs:
			try:
				os.rmdir(os.path.join(root, name))
			except:
				pass

def init(session):
	global instance
	instance.init(session)

instance = Trashcan()

class CleanTrashTask(Components.Task.PythonTask):
	def openFiles(self, ctimeLimit, reserveBytes):
		self.ctimeLimit = ctimeLimit
		self.reserveBytes = reserveBytes

	def work(self):
		mounts=[]
		matches = []
		print "[Trashcan] probing folders"
		f = open('/proc/mounts', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			mounts.append(parts[1])
		f.close()

 		for mount in mounts:
			if os.path.isdir(os.path.join(mount,'.Trash')):
				matches.append(os.path.join(mount,'.Trash'))
			if os.path.isdir(os.path.join(mount,'movie/.Trash')):
				matches.append(os.path.join(mount,'movie/.Trash'))

		print "[Trashcan] found following trashcan's:",matches
		if len(matches):
			for trashfolder in matches:
				print "[Trashcan] looking in trashcan",trashfolder
				trashsize = get_size(trashfolder)
				diskstat = os.statvfs(trashfolder)
				free = diskstat.f_bfree * diskstat.f_bsize
				bytesToRemove = self.reserveBytes - free
				print "[Trashcan] " + str(trashfolder) + ": Size:",trashsize
				candidates = []
				size = 0
				for root, dirs, files in os.walk(trashfolder, topdown=False):
					for name in files:
						try:
							fn = os.path.join(root, name)
							st = os.stat(fn)
							if st.st_ctime < self.ctimeLimit:
								enigma.eBackgroundFileEraser.getInstance().erase(fn)
								bytesToRemove -= st.st_size
							else:
								candidates.append((st.st_ctime, fn, st.st_size))
								size += st.st_size
						except Exception, e:
							print "[Trashcan] Failed to stat %s:"% name, e
					# Remove empty directories if possible
					for name in dirs:
						try:
							os.rmdir(os.path.join(root, name))
						except:
							pass
					candidates.sort()
					# Now we have a list of ctime, candidates, size. Sorted by ctime (=deletion time)
					for st_ctime, fn, st_size in candidates:
						if bytesToRemove < 0:
							break
						enigma.eBackgroundFileEraser.getInstance().erase(fn)
						bytesToRemove -= st_size
						size -= st_size
					print "[Trashcan] " + str(trashfolder) + ": Size now:",size

class TrashInfo(VariableText, GUIComponent):
	FREE = 0
	USED = 1
	SIZE = 2

	def __init__(self, path, type, update = True):
		GUIComponent.__init__(self)
		VariableText.__init__(self)
		self.type = type
		if update:
			self.update(path)

	def update(self, path):
		try:
			total_size = get_size(getTrashFolder(path))
		except OSError:
			return -1

		if self.type == self.USED:
			try:
				if total_size < 10000000:
					total_size = _("%d Kb") % (total_size >> 10)
				elif total_size < 10000000000:
					total_size = _("%d Mb") % (total_size >> 20)
				else:
					total_size = _("%d Gb") % (total_size >> 30)
				self.setText(_("Trashcan:") + " " + total_size)
			except:
				# occurs when f_blocks is 0 or a similar error
				self.setText("-?-")

	GUI_WIDGET = enigma.eLabel