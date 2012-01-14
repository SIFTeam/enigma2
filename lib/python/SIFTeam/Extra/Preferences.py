from Components.config import config, ConfigSlider, ConfigSelection, ConfigYesNo, \
	ConfigEnableDisable, ConfigSubsection, ConfigBoolean, ConfigNumber, ConfigText, \
	ConfigTime
	
pclockcb = []

def InitPreferences():
	config.sifteam = ConfigSubsection()
	config.sifteam.infobar = ConfigSelection(choices={
			"light": _("Light"),
			"full": _("Full"), 
			"light_and_full": _("Light and Full")}, 
			default = "light")
	config.sifteam.permanentclock = ConfigYesNo(False)
	config.sifteam.animatedpicon = ConfigYesNo(True)
	config.sifteam.animatedprovicon = ConfigYesNo(True)
	config.sifteam.animatedsaticon = ConfigYesNo(True)
	config.sifteam.emudelay = ConfigSelection(choices={
			"0": _("Enigma2 boot"),
			"015": _("After 15 seconds"), 
			"030": _("After 30 seconds"), 
			"045": _("After 45 seconds"), 
			"060": _("After 1 minute"), 
			"120": _("After 2 minutes")}, 
			default = "0")
	config.sifteam.autoupdates = ConfigSelection(choices={
			"disabled": _("Disabled"),
			"ask": _("Ask before install"), 
			"auto": _("Automatically install all updates")}, 
			default = "ask")
	config.sifteam.crashlogs = ConfigSelection(choices={
			"disabled": _("Disabled"),
			"ask": _("Ask before send"), 
			"auto": _("Automatically send all")}, 
			default = "ask")
	
	config.sifteam.switch_4_3_letterbox = ConfigYesNo(True)
	config.sifteam.switch_4_3_panscan = ConfigYesNo(True)
	config.sifteam.switch_16_9 = ConfigYesNo(False)
	config.sifteam.switch_16_9_always = ConfigYesNo(True)
	config.sifteam.switch_16_10_letterbox = ConfigYesNo(False)
	config.sifteam.switch_16_10_panscan = ConfigYesNo(False)
	config.sifteam.switch_16_9_letterbox = ConfigYesNo(True)
	
	config.sifteam.addons_packages_sort = ConfigSelection(choices={
			"name": _("Name"),
			"rank": _("Rank"),
			"ratings": _("Ratings"),
			"downloads": _("Downloads")
			}, 
			default = 0)

	config.sifteam.skindevelopermode = ConfigYesNo(False)
	
	config.sifteam.cloud = ConfigSubsection()
	config.sifteam.cloud.username = ConfigText(fixed_size = False)
	config.sifteam.cloud.password = ConfigText(fixed_size = False)
	config.sifteam.cloud.softwareupdates = ConfigYesNo(False)
	config.sifteam.cloud.settingsupdates = ConfigYesNo(False)
	config.sifteam.cloud.crashlogs = ConfigYesNo(False)
	config.sifteam.cloud.timeautoupdates = ConfigTime(default = 18000)
	
	config.sifteam.settings = ConfigSubsection()
	config.sifteam.settings.keepterrestrial = ConfigYesNo(False)
	config.sifteam.settings.keepsatellitesxml = ConfigYesNo(False)
	config.sifteam.settings.keepcablesxml = ConfigYesNo(False)
	config.sifteam.settings.keepterrestrialxml = ConfigYesNo(False)
	config.sifteam.settings.keepbouquets = ConfigText("", False)
	config.sifteam.settings.currentsettings = ConfigNumber(default = -1)
	config.sifteam.settings.currentsettingsdate = ConfigText(fixed_size = False)
	
def RegPClockCallback(callback):
	global pclockcb
	pclockcb.append(callback)
	
def CallPClockCallback():
	global pclockcb
	for x in pclockcb:
		x()
