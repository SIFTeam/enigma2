from enigma import eDVBDB
from Components.config import config

import os
import re
import shutil

TMP_SETTINGS_PWD = "/tmp/sl_settings_tmp"
TMP_IMPORT_PWD = "/tmp/sl_import_tmp"
ENIGMA2_SETTINGS_PWD = "/etc/enigma2"
ENIGMA2_TUXBOX_PWD = "/etc/tuxbox"

class SettingsLoader():
	def __init__(self):
		self.providers = []
		self.providersT = []
		self.services = []
		self.servicesT = []
		
	def read(self, pwd):
		self.providers = []
		self.services = []
		
		try:
			f = open(pwd + "/lamedb")
		except Exception, e:
			print e
			return
		
		while True:
			line = f.readline()
			if line == "":
				return
				
			line = line.strip()
			if line == "transponders":
				break
			
		while True:
			line = f.readline()
			if line == "":
				return

			line = line.strip()

			if line == "end":
				break
				
			line2 = f.readline().strip()
			line3 = f.readline().strip()
			
			self.providers.append([line.split(":"), line2.split(":"), line3.split(":")])

		while True:
			line = f.readline()
			if line == "":
				return
				
			line = line.strip()
			if line == "services":
				break

		while True:
			line = f.readline()
			if line == "":
				return

			line = line.strip()

			if line == "end":
				break
				
			line2 = f.readline().strip("\n")
			line3 = f.readline().strip("\n")
			
			self.services.append([line.split(":"), line2.split(":"), line3.split(":")])

		f.close()
		
	def write(self, pwd):
		try:
			f = open(pwd + "/lamedb", "w")
		except Exception, e:
			print e
			return
			
		f.write("eDVB services /4/\n")
		f.write("transponders\n")
		
		for provider in self.providers:
			f.write(":".join(provider[0]) + "\n")
			f.write("\t" + ":".join(provider[1]) + "\n")
			f.write(":".join(provider[2]) + "\n")
	
		f.write("end\n")
		f.write("services\n")
		
		for service in self.services:
			f.write(":".join(service[0]) + "\n")
			f.write(":".join(service[1]) + "\n")
			f.write(":".join(service[2]) + "\n")
			
		f.write("end\n")
		f.write("Have a lot of bugs!\n")
		f.close()
		
	def saveTerrestrial(self):
		providersT = []
		servicesT = []
		
		for provider in self.providers:
			if provider[1][0][:1] == "t":
				providersT.append(provider)

		for service in self.services:
			for provider in providersT:
				if service[0][1] == provider[0][0] and service[0][2] == provider[0][1] and service[0][3] == provider[0][2]:
					servicesT.append(service)

		self.providersT = providersT
		self.servicesT = servicesT

	def restoreTerrestrial(self):
		tmp = self.providersT

		for provider in self.providers:
			if provider[1][0][:1] != "t":
				tmp.append(provider)

		self.providers = tmp

		tmp = self.servicesT
		for service in self.services:
			if service[0][1][:4] != "eeee":
				tmp.append(service)
		
		self.services = tmp
		
	def readBouquetsTvList(self, pwd):
		return self.readBouquetsList(pwd, "bouquets.tv")

	def readBouquetsRadioList(self, pwd):
		return self.readBouquetsList(pwd, "bouquets.radio")

	def readBouquetsList(self, pwd, bouquetname):
		try:
			f = open(pwd + "/" + bouquetname)
		except Exception, e:
			print e
			return
		
		ret = []
		
		while True:
			line = f.readline()
			if line == "":
				break
				
			if line[:8] != "#SERVICE":
				continue
				
			tmp = line.strip().split(":")
			line = tmp[len(tmp)-1]
			
			filename = None
			if line[:12] == "FROM BOUQUET":
				tmp = line[13:].split(" ")
				filename = tmp[0].strip("\"")
			else:
				filename = line
			
			if filename:
				try:
					fb = open(pwd + "/" + filename)
				except Exception, e:
					print e
					continue
					
				tmp = fb.readline().strip()
				if tmp[:6] == "#NAME ":
					ret.append([filename, tmp[6:]])
				else:
					ret.append([filename, filename])
				fb.close()
				
		return ret

	def copyBouquetsTv(self, srcpwd, dstpwd, keeplist):
		return self.copyBouquets(srcpwd, dstpwd, "bouquets.tv", keeplist)

	def copyBouquetsRadio(self, srcpwd, dstpwd, keeplist):
		return self.copyBouquets(srcpwd, dstpwd, "bouquets.radio", keeplist)
		
	def copyBouquets(self, srcpwd, dstpwd, bouquetname, keeplist):
		srclist = self.readBouquetsList(srcpwd, bouquetname)
		dstlist = self.readBouquetsList(dstpwd, bouquetname)
		
		if srclist is None:
			srclist = []
			
		if dstlist is None:
			dstlist = []
			
		count = 0
		for item in dstlist:
			if item[0] in keeplist:
				found = False
				for x in srclist:
					if x[0] == item[0]:
						found = True
						break
				
				if not found:
					srclist.insert(count, item)
			else:
				os.remove(dstpwd + "/" + item[0])
				
			count += 1
			
		for x in srclist:
			if x[0] not in keeplist:
				try:
					shutil.copyfile(srcpwd + "/" + x[0], dstpwd + "/" + x[0])
				except:
					pass

		try:
			f = open(dstpwd + "/" + bouquetname, "w")
		except Exception, e:
			print e
			return
			
		if bouquetname[-3:] == ".tv":
			f.write("#NAME Bouquets (TV)\n")
		else:
			f.write("#NAME Bouquets (Radio)\n")
			
		for x in srclist:
			if bouquetname[-3:] == ".tv":
				f.write("#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"" + x[0] + "\" ORDER BY bouquet\n")
			else:
				f.write("#SERVICE 1:7:2:0:0:0:0:0:0:0:FROM BOUQUET \"" + x[0] + "\" ORDER BY bouquet\n")
 
	def apply(self):
		if config.sifteam.settings.keepterrestrial.value:
			self.read(ENIGMA2_SETTINGS_PWD)
			self.saveTerrestrial()
			self.read(TMP_SETTINGS_PWD)
			self.restoreTerrestrial()
			self.write(ENIGMA2_SETTINGS_PWD)
			keeplist = config.sifteam.settings.keepbouquets.value.split("|")
		else:
			self.read(TMP_SETTINGS_PWD)
			self.write(ENIGMA2_SETTINGS_PWD)
			keeplist = []

		self.copyBouquets(TMP_SETTINGS_PWD, ENIGMA2_SETTINGS_PWD, "bouquets.tv", keeplist)
		self.copyBouquets(TMP_SETTINGS_PWD, ENIGMA2_SETTINGS_PWD, "bouquets.radio", keeplist)
		
		if not config.sifteam.settings.keepsatellitesxml.value:
			try:
				shutil.copyfile(TMP_SETTINGS_PWD + "/satellites.xml", ENIGMA2_TUXBOX_PWD + "/satellites.xml")
			except Exception, e:
				pass
		
		if not config.sifteam.settings.keepcablesxml.value:
			try:
				shutil.copyfile(TMP_SETTINGS_PWD + "/cables.xml", ENIGMA2_TUXBOX_PWD + "/cables.xml")
			except Exception, e:
				pass

		if not config.sifteam.settings.keepterrestrialxml.value:
			try:
				shutil.copyfile(TMP_SETTINGS_PWD + "/terrestrial.xml", ENIGMA2_TUXBOX_PWD + "/terrestrial.xml")
			except Exception, e:
				pass

		try:
			shutil.copyfile(TMP_SETTINGS_PWD + "/whitelist", ENIGMA2_SETTINGS_PWD + "/whitelist")
		except Exception, e:
			pass

		try:
			shutil.copyfile(TMP_SETTINGS_PWD + "/blacklist", ENIGMA2_SETTINGS_PWD + "/blacklist")
		except Exception, e:
			pass

		eDVBDB.getInstance().reloadServicelist()
		eDVBDB.getInstance().reloadBouquets()
		