from java.util import *
from java.lang import *
import java.lang.System as sys

def MB(val):
	return int( val ) / ( 1024.0 * 1024.0 )

lineSeparator = sys.getProperty('line.separator')
cellname = AdminControl.getCell()
nodes = AdminConfig.list('Node').split(lineSeparator)
for node in nodes:
        nname = AdminConfig.showAttribute(node, 'name')
	tmpNode = String(nname.replace('\r',''))
	if tmpNode.indexOf("Node") > 0:
	        allServers = AdminConfig.list('Server',node).split(lineSeparator)
	        print "JVMs on " + nname
	        for server in allServers:
        	        tmp = String(server.replace('\r', ''))
                	srvName = tmp.substring(0, tmp.indexOf("(cells"))
                        key = "type=Server,node=" + nname + ",process=" + srvName + ",*"
			srvObjName = AdminControl.completeObjectName(key)
                        if len(srvObjName) != 0:
				jvm = AdminControl.queryNames('type=JVM,cell=' +  cellname + ',node=' + nname + ',process=' + srvName + ',*')
				used = AdminControl.getAttribute(jvm,'heapSize')
				free = AdminControl.getAttribute(jvm,'freeMemory')
				total = int( used ) + int( free );
				percent = float( used ) * 100.0 / float( total );
				print "Name=%s, Status=STARTED, PID=%s, Heap Size: used=%.1fMB(%.2f%%),free=%.1fMB" %(srvName, AdminControl.getAttribute(srvObjName, 'pid'),MB(used),percent,MB(free))
			else:
				print "Name=" + srvName + " Status=STOPPED"
