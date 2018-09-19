from java.util import *
from java.lang import *

servername = sys.argv[0]
nodename = sys.argv[1]

if (len(servername) != 0):
	key = "type=Server,node=" + nodename + ",process=" + servername + ",*"
	server = AdminControl.completeObjectName(key)
	temp=String(nodename)
	nodeHost=temp.substring(0, temp.indexOf("Node"))
	if len(server) == 0:
		print "Status jvm " + nodeHost + ":" + servername + " Stopped"
	else: 
		print "Status jvm " + nodeHost + ":" + servername + " Started"

#apps = AdminApp.list()
#print "apps=" + apps
