def getHWType():
	try:
		return open("/etc/machine").read().strip()
	except Exception, e:
		return ""
		
def getHWClass():
	hwtype = getHWType()
	if hwtype == "dm800" or hwtype == "dm800se" or hwtype == "dm8000" or hwtype == "dm500hd" or hwtype == "dm7025hd":
		return "dmm"
	elif hwtype == "vuduo" or hwtype == "vusolo" or hwtype == "vuuno":
		return "vuplus"
	elif hwtype == "et9x00" or hwtype == "et6x00" or hwtype == "et5x00":
		return "xtrend-ctech"
	elif hwtype == "gb800solo" or hwtype == "gb800ue" or hwtype == "gb800solo" or hwtype == "quattro":
		return "gigablue"
	return "unknown"
		
def getHWTypeText():
	hwtype = getHWType()
	if hwtype == "dm800":
		return "DM 800"
	elif hwtype == "dm800se":
		return "DM 800se"
	elif hwtype == "dm8000":
		return "DM 8000"
	elif hwtype == "dm500hd":
		return "DM 500hd"
	elif hwtype == "dm7025hd":
		return "DM 7025hd"
	elif hwtype == "vuduo":
		return "Vu+ Duo"
	elif hwtype == "vusolo":
		return "Vu+ Solo"
	elif hwtype == "vuuno":
		return "Vu+ Uno"
	elif hwtype == "et9x00":
		return "Clark/Xtrend et9x00"
	elif hwtype == "et6x00":
		return "Clark/Xtrend et6x00"
	elif hwtype == "et5x00":
		return "Clark/XTrend et5x00"
	elif hwtype == "gb800se":
		return "GigaBlue HD 800se"
	elif hwtype == "gb800ue":
		return "GigaBlue HD 800ue"
	elif hwtype == "gb800solo":
		return "GigaBlue HD 800solo"
	elif hwtype == "quattro":
		return "GigaBlue HD Quattro"
	return hwtype
