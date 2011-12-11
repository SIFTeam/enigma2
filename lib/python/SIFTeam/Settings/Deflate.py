import zipfile
import shutil
import os

from Common import TMP_SETTINGS_PWD

class STDeflate():
	def __init__(self):
		pass
		
	def deflateZip(self, filename):
		zip = zipfile.ZipFile(filename, "r")
		try:
			shutil.rmtree(TMP_SETTINGS_PWD)
		except:
			pass
			
		os.mkdir(TMP_SETTINGS_PWD)
		files = zip.namelist()
		for file in files:
			if file[-1:] == "/":
				continue
			buff = zip.read(file)
			tmp = file.split("/")
			file = tmp[len(tmp)-1]
			out = open(TMP_SETTINGS_PWD + "/" + file, "w")
			out.write(buff)
			out.close()
		
	def deflateTar(self, filename):
		try:
			shutil.rmtree(TMP_SETTINGS_PWD)
		except:
			pass
			
		os.mkdir(TMP_SETTINGS_PWD)
		os.system("tar zxf \"" + filename + "\" -C " + TMP_SETTINGS_PWD)
		os.system("cd " + TMP_SETTINGS_PWD + " && find -type f -exec mv {} . \\;")
	
	def deflateIpk(self, filename):
		try:
			shutil.rmtree(TMP_SETTINGS_PWD)
		except:
			pass
			
		os.mkdir(TMP_SETTINGS_PWD)
		os.system("cp " + filename + " " + TMP_SETTINGS_PWD + "/tmp.ipk")
		os.system("cd " + TMP_SETTINGS_PWD + " && ar -x tmp.ipk")
		os.system("tar zxf " + TMP_SETTINGS_PWD + "/data.tar.gz -C " + TMP_SETTINGS_PWD)
		os.system("cd " + TMP_SETTINGS_PWD + " && find -type f -exec mv {} . \\;")
	
	def deflate(self, filename):
		if filename[-4:] == ".zip":
			self.deflateZip(filename)
		elif filename[-7:] == ".tar.gz" or filename[-8:] == ".tgz":
			self.deflateTar(filename)
		elif filename[-4:] == ".ipk":
			self.deflateIpk(filename)