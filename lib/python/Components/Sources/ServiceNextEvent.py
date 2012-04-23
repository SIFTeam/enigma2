from Components.Element import cached
from enigma import eServiceCenter, eServiceReference as Ref, eEPGCache
from Source import Source

class ServiceNextEvent(Source, object):
	def __init__(self):
		Source.__init__(self)
		self.service = None 

	@cached
	def getCurrentService(self):
		return self.service

	@cached
	def getNextEvent(self):
		evt = self.service and self.info and self.info.getEvent(self.service)
		if evt is not None:
			epgcache = eEPGCache.getInstance()
			evt = epgcache.lookupEventTime(self.service, evt.getBeginTime() + evt.getDuration())
		print "**", evt
		return evt

	@cached
	def getInfo(self):
		return self.service and eServiceCenter.getInstance().info(self.service)

	event = property(getNextEvent)
	info = property(getInfo)

	def newService(self, ref):
		if not self.service or not ref or self.service != ref:
			self.service = ref
			if not ref:
				self.changed((self.CHANGED_CLEAR,))
			else:
				self.changed((self.CHANGED_ALL,))
