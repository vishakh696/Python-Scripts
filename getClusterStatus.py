from java.util import *
from java.lang import *
#import java.lang.System as sys

#cellName = AdminControl.getCell()
clustername = sys.argv[0] 

key="/ServerCluster:" + clustername + "/"
clusterID=AdminConfig.getid(key)
clusterList=AdminConfig.list('ClusterMember',clusterID)
servers=clusterList.split("\n")
for serverID in servers:
#	print "serverID=" + serverID
	serverName=AdminConfig.showAttribute(serverID, 'memberName')
	nodeName=AdminConfig.showAttribute(serverID, 'nodeName')
	key = "type=Server,node=" + nodeName + ",process=" + serverName + ",*"
	server = AdminControl.completeObjectName(key)
	temp=String(nodeName)
	nodeHost=temp.substring(0, temp.indexOf("Node"))
	if len(server) != 0:
		print "Status jvm " + nodeHost + ":" + serverName + " Started"
	else:
		print "Status jvm " + nodeHost + ":" + serverName + " Stopped"

