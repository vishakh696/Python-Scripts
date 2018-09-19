#-------------------------------------------------------------------#
# Author: Vishakh                                                   #
# Description:                                                      #
# This JYTHON script is used to deploy an EAR file to a WebSphere   #
# Application Server ND. Following are the args                     #
# that are passed to it:                                            #
#       1. DEPLOY_APP_NAME - application name                       #
#       2. DEPLOY_APP_EAR - path to the ear file                    #
#       3. DEPLOY_VHOST - virtual host name                    	    #
#-------------------------------------------------------------------#

from java.util import *
from java.lang import *

def mapVHostToModules():
    # Map virtual hosts for web modules
	i = 0
	modulename = ""
	uri = ""
	mapModuleArgument = "['-MapWebModToVH', ["
	vhostname = ""
	lines = AdminApp.taskInfo(DEPLOY_APP_EAR,'MapWebModToVH').split("\n")
	for i in range(len(lines)):
		tmp = String(lines[i])
		if tmp.startsWith("Web module: "):
			modulename = tmp.substring(12,tmp.length())
		if tmp.startsWith("URI: "):
			uri = tmp.substring(5,tmp.length())
		if tmp.startsWith("Virtual host: "):
			vhost = tmp.substring(14,tmp.length())
			mapModuleArgument = mapModuleArgument + "['" + modulename + "','" + uri + "','" + DEPLOY_VHOST + "'],"
	tmpstr = String(mapModuleArgument)
	mapModuleArgument = tmpstr.substring(0,tmpstr.lastIndexOf("'")+2)
	mapModuleArgument = mapModuleArgument + "]]"
	return mapModuleArgument

def SaveSync():
	saveCommand = "AdminConfig.save()"
	exec saveCommand

	nodeList = ArrayList()
	nodes = AdminConfig.list('Node').split("\n")

	for i in range(len(nodes)):
		temp = String(nodes[i])
		nodeList.add(temp.substring(0, temp.indexOf("(cells")))
	# outside for 1st loop
	for j in range(nodeList.size()):
		node = nodeList.get(j)
		x = node.count("dmgr")
		y = node.count("http")
		if x == 0:
			if y == 0:
			    tmpNode = String(node)
			    if tmpNode.indexOf("Node") > 0:
    				syncObjName = "AdminControl.completeObjectName('type=NodeSync,node=" + nodeList.get(j) + ",*')"
    				key = "type=NodeSync,node=" + nodeList.get(j) + ",*"
				if len(AdminControl.completeObjectName(key)) != 0:
	    				syncCommand = "AdminControl.invoke(" + syncObjName + ",'sync')"
    					syncCommand = syncCommand.replace('\r','')
    					print node
					exec syncCommand


# ------ Script start ------- #

DEPLOY_APP_NAME = sys.argv[0]
DEPLOY_APP_EAR = sys.argv[1]
DEPLOY_VHOST = sys.argv[2]

updateCmd = "AdminApp.update('" + DEPLOY_APP_NAME + "', 'app', '[ -operation update -contents " + DEPLOY_APP_EAR + " -nopreCompileJSPs]')"
exec updateCmd

vhostMapping = mapVHostToModules()

editCommand = "AdminApp.edit('" + DEPLOY_APP_NAME + "', " + vhostMapping + ")"
editCommand = editCommand.replace('\r', '')
print "Mapping Virtual Hosts"
exec editCommand
print "Saving configuration and Synchronizing nodes:"
SaveSync()
