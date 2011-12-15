from Components.config import config

from Stack import SMStack, smstack

def doAutomaticSoftwareUpdates():
	if len(smstack.upgradables) > 0:
		smstack.add(SMStack.UPGRADE, "auto")
	
def startAutomaticSoftwareUpdates(session, id, arg):
	if config.sifteam.cloud.softwareupdates.value:
		smstack.add(SMStack.UPDATE, "", doAutomaticSoftwareUpdates)