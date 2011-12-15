from Components.config import config
from SIFTeam.Settings.Settings import installSettings
from SIFTeam.Extra.SAPCL import SAPCL

def startAutomaticSettingsUpdates(session, id, arg):
	if config.sifteam.cloud.settingsupdates.value and config.sifteam.settings.currentsettings.value != -1:
		api = SAPCL()
		settings = api.getChannelsSettings()
		for setting in settings["settings"]:
			if setting["id"] == config.sifteam.settings.currentsettings.value:
				if setting["published"] != config.sifteam.settings.currentsettingsdate.value:
					config.sifteam.settings.currentsettingsdate.value = setting["published"]
					installSettings(config.sifteam.settings.currentsettings.value)
					
				break
