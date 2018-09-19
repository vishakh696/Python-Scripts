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

print "Saving configuration and Synchronizing nodes:"
SaveSync()
