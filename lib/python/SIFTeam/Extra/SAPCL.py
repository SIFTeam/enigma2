from Components.config import config

import os
import re
import urllib
import httplib
import xml.etree.cElementTree

class StatusCodeError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class SAPCL(object):
	def __init__(self):
		pass
		
	def getHost(self):
		return "api.sifteam.eu"
		
	def getIP(self):
		return "85.17.231.249"
		
	def getBranch(self):
		try:
			return open("/etc/branch").read().strip()
		except Exception, e:
			return ""
		
	def getMachine(self):
		try:
			return open("/etc/machine").read().strip()
		except Exception, e:
			return ""
		
	def getVersion(self):
		return "0.1"
		
	def getUsername(self):
		return config.sifteam.cloud.username.value
	
	def getPassword(self):
		return config.sifteam.cloud.password.value
		
	def request(self, page, args, post_args=None):
		useragent = "SIFTeam API Python Client Library %s (%s/%s)" % (self.getVersion(), self.getBranch(), self.getMachine())
		headers = { "Host": self.getHost(), "User-Agent": useragent }
		args["branch"] = self.getBranch()
		args["machine"] = self.getMachine()
		conn = httplib.HTTPSConnection(self.getIP())
		if post_args:
			print "[SAPCL] HTTP POST Request: %s?%s" % (page, urllib.urlencode(args))
			conn.request("POST", "%s?%s" % (page, urllib.urlencode(args)), urllib.urlencode(post_args), headers)
		else:
			print "[SAPCL] HTTP GET Request: %s?%s" % (page, urllib.urlencode(args))
			conn.request("GET", "%s?%s" % (page, urllib.urlencode(args)), None, headers)
		httpres = conn.getresponse()
		
		self.filename = ""
		contentdisposition = httpres.getheader("content-disposition")
		if contentdisposition:
			res = re.search("filename=\"(.*)\"", contentdisposition)
			if res:
				self.filename = res.group(1)
		
		if httpres.status == 200:
			print "[SAPCL] HTTP Ok 200"
			return httpres.read()
		elif httpres.status == 201:
			print "[SAPCL] HTTP Created 201"
			return httpres.read()
		elif httpres.status == 304:
			print "[SAPCL] HTTP Not Modified 304"
			return None
		else:
			print "[SAPCL] HTTP Error %i - %s" % (httpres.status, httpres.reason)
			raise StatusCodeError("HTTP Error %i" % httpres.status)
		
	def nodeToDictionary(self, node):
		ret = {}
		for field in node:
			ret[field.tag] = None
			
			if field.get("nil") == "true":
				continue
				
			if field.get("type") == "integer":
				ret[field.tag] = int(field.text)
			elif field.get("type") == "boolean":
				ret[field.tag] = field.text == "true"
			else:
				ret[field.tag] = field.text
		return ret
		
	def xmlToGenericList(self, data, tag):
		mdom = xml.etree.cElementTree.fromstring(data)
		
		ret = []
		for node in mdom:
			if node.tag == tag:
				ret.append(self.nodeToDictionary(node))
				
		return ret
		
	def getAccount(self):
		args = {}
		
		post_args = {
			"username": self.getUsername(),
			"password": self.getPassword()
		}
		
		try:
			buff = self.request("/account/check_auth.xml", args, post_args)
			mdom = xml.etree.cElementTree.fromstring(buff)
			return {
				"result": True,
				"message": "",
				"status": self.nodeToDictionary(mdom)
			}
		except Exception, e:
			return {
				"result": False,
				"message": "Wrong username or password",
				"status": {}
			}
		
	def getCategories(self, parentid, withmeta):
		args = {
			"parent_id": parentid
		}
		if withmeta:
			args["withmeta"] = "true"
			
		try:
			buff = self.request("/packages/categories.xml", args)
			
			return {
				"result": True,
				"message": "",
				"categories": sorted(self.xmlToGenericList(buff, "packages-category"), key=lambda k: k['name']) 
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"categories": []
			}
		
	def getTopTen(self, sort="name"):
		args = {
			"order": sort,
			"limit": 10,
			"withmeta": "true"
		}
		if sort == "name":
			args["orientation"] = "asc"
		else:
			args["orientation"] = "desc"
			
		try:
			buff = self.request("/packages/items.xml", args)
			
			return {
				"result": True,
				"message": "",
				"packages": self.xmlToGenericList(buff, "package")
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"packages": []
			}
		
	def getPackages(self, parentid, sort="name", withmeta=False):
		args = {
			"fulltree": parentid,
			"order": sort
		}
		if withmeta:
			args["withmeta"] = "true"
			
		if sort == "name":
			args["orientation"] = "asc"
		else:
			args["orientation"] = "desc"
			
		try:
			buff = self.request("/packages/items.xml", args)
			
			return {
				"result": True,
				"message": "",
				"packages": self.xmlToGenericList(buff, "package")
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"packages": []
			}
			
	def getUsbDevice(self, vid, pid):
		args = {
			"idVendor": vid,
			"idProduct": pid
		}
		
		try:
			buff = self.request("/usb_devices.xml", args)
			return {
				"result": True,
				"message": "",
				"devices": self.xmlToGenericList(buff, "usb-device")
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"devices": []
			}
			
	def getUsbFirmwares(self, drivername):
		args = {
			"driver_name": drivername
		}
		
		try:
			buff = self.request("/usb_firmwares.xml", args)
			return {
				"result": True,
				"message": "",
				"firmwares": self.xmlToGenericList(buff, "usb-firmware")
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"firmwares": []
			}
			
	def getChannelsSettings(self):
		args = {}
		
		try:
			buff = self.request("/channels_settings.xml", args)
			return {
				"result": True,
				"message": "",
				"settings": self.xmlToGenericList(buff, "channels-setting")
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"settings": []
			}
			
	def getChannelsSetting(self, id):
		args = {}
		
		try:
			buff = self.request("/channels_settings/" + str(id), args)
			if self.filename == "" or buff == None:
				return {
					"result": False,
					"message": "Error retrieving file",
					"filename": ""
				}
				
			filename = "/tmp/" + self.filename
			
			open(filename, "w").write(buff)
				
			return {
				"result": True,
				"message": "",
				"filename": filename
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"filename": None
			}
			
	def rank(self, packageid, rank):
		args = {}
		
		post_args = {
			"packages_rating[package_id]": packageid,
			"packages_rating[rate]": rank
		}

		try:
			buff = self.request("/packages/ratings.xml", args, post_args)
			if not buff:
				return {
					"result": False,
					"message": "You already ranked this package!",
					"status": {}
				}
				
			mdom = xml.etree.cElementTree.fromstring(buff)
			return {
				"result": True,
				"message": "",
				"status": self.nodeToDictionary(mdom)
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"status": {}
			}
	
	def download(self, packageid):
		args = {}
		
		post_args = {
			"packages_download[package_id]": packageid
		}

		try:
			buff = self.request("/packages/downloads.xml", args, post_args)
			mdom = xml.etree.cElementTree.fromstring(buff)
			return {
				"result": True,
				"message": "",
				"status": self.nodeToDictionary(mdom)
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"status": {}
			}
			
	def downloadByPackageName(self, packagename):
		args = {}
		
		try:
			buff = self.request("/packages/items/download/%s/%s/%s.xml" % (self.getBranch(), self.getMachine(), packagename), args)
			mdom = xml.etree.cElementTree.fromstring(buff)
			return {
				"result": True,
				"message": "",
				"status": self.nodeToDictionary(mdom)
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"status": {}
			}
	
	def install(self, packageid):
		args = {}
		
		post_args = {
			"packages_install[package_id]": packageid
		}

		try:
			buff = self.request("/packages/installs.xml", args, post_args)
			mdom = xml.etree.cElementTree.fromstring(buff)
			return {
				"result": True,
				"message": "",
				"status": self.nodeToDictionary(mdom)
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"status": {}
			}
	
	def installByPackageName(self, packagename):
		args = {}
		
		try:
			buff = self.request("/packages/items/install/%s/%s/%s.xml" % (self.getBranch(), self.getMachine(), packagename), args)
			mdom = xml.etree.cElementTree.fromstring(buff)
			return {
				"result": True,
				"message": "",
				"status": self.nodeToDictionary(mdom)
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"status": {}
			}
		
	
	def uninstall(self, packageid):
		args = {}
		
		post_args = {
			"packages_uninstall[package_id]": packageid
		}

		try:
			buff = self.request("/packages/uninstalls.xml", args, post_args)
			mdom = xml.etree.cElementTree.fromstring(buff)
			return {
				"result": True,
				"message": "",
				"status": self.nodeToDictionary(mdom)
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"status": {}
			}
			
	def uninstallByPackageName(self, packagename):
		args = {}
		
		try:
			buff = self.request("/packages/items/uninstall/%s/%s/%s.xml" % (self.getBranch(), self.getMachine(), packagename), args)
			mdom = xml.etree.cElementTree.fromstring(buff)
			return {
				"result": True,
				"message": "",
				"status": self.nodeToDictionary(mdom)
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
				"status": {}
			}
			
	def sendCrashLog(self, data):
		args = {}
		
		post_args = {
			"crashlog[machine]": self.getMachine(),
			"crashlog[branch]": self.getBranch(),
			"crashlog[datalog]": data
		}

		try:
			self.request("/crashlogs.xml", args, post_args)
			return {
				"result": True,
				"message": "",
			}
		except Exception, e:
			return {
				"result": False,
				"message": str(e),
			}