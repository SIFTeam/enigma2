from Components.config import config

from Stack import SMStack, smstack

def doAutomaticUpdates():
	if len(smstack.upgradables) > 0:
		smstack.add(SMStack.UPGRADE, "auto")
	
def startAutomatiUpdates(session, id, arg):
	if config.sifteam.cloud.softwareupdates.value:
		smstack.add(SMStack.UPDATE, "", doAutomaticUpdates)