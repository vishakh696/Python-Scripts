#-------------------------------------------------------------------#
# Author: Vishakh                      								#
#
# Description:                                                      #
# This JYTHON script is used to bounce cluster member. Following    #
# are the args passed to it:                                        #
#       1. clustername - name of cluster		            #
#       2. action - start/stop/restart              		    #
#-------------------------------------------------------------------#

from java.lang import *
import os
import time

def stopCluster(cluster):
	AdminControl.invoke(cluster, 'stop')
	print "STOP process for cluster initiated"  
	i=0
	bTimeout=0
	while 'true':
		state = AdminControl.getAttribute(cluster, 'state')
		print "\tnew state = " + state
		if state == "websphere.cluster.stopped":
			break
		if i == 30:
			key="/ServerCluster:" + clustername + "/"
			clusterID=AdminConfig.getid(key)
			clusterList=AdminConfig.list('ClusterMember',clusterID)
			servers=clusterList.split("\n")
			for serverID in servers:
				serverName=AdminConfig.showAttribute(serverID, 'memberName')
				nodeName=AdminConfig.showAttribute(serverID, 'nodeName')
				key = "type=Server,node=" + nodeName + ",process=" + serverName + ",*"
                	        server = AdminControl.completeObjectName(key)
                        	if len(server) == 0:
					print "\n" + serverName + "/" + nodeName + " stopped"
				else:
					raise SystemExit("\nProcess timed out while stopping " + serverName + "/" + nodeName)
					bTimeout=1
			break
		else:
			print "\tcluster stopping...please wait"
			time.sleep(10)
		i = i + 1
	if bTimeout == 0:
		print "Cluster has been stopped.\n"
	
def forceStopCluster(cluster):
	AdminControl.invoke(cluster, 'stopImmediate')
	print "FORCE STOP process for cluster initiated" 
	i=0
	bTimeout=0 
        while 'true':
                state = AdminControl.getAttribute(cluster, 'state')
                print "\tnew state = " + state
                if state == "websphere.cluster.stopped":
                        break
                if i == 30:
                        key="/ServerCluster:" + clustername + "/"
                        clusterID=AdminConfig.getid(key)
                        clusterList=AdminConfig.list('ClusterMember',clusterID)
                        servers=clusterList.split("\n")
                        for serverID in servers:
                                serverName=AdminConfig.showAttribute(serverID, 'memberName')
                                nodeName=AdminConfig.showAttribute(serverID, 'nodeName')
                                key = "type=Server,node=" + nodeName + ",process=" + serverName + ",*"
                                server = AdminControl.completeObjectName(key)
                                if len(server) == 0:
                                        print "\n" + serverName + "/" + nodeName + " stopped"
                                else:
                                        raise SystemExit("\nProcess timed out while stopping " + serverName + "/" + nodeName)
                                        bTimeout=1
                        break
                else:
                        print "\tcluster stopping...please wait"
                        time.sleep(10)
                i = i + 1
        if bTimeout == 0:
                print "Cluster has been stopped.\n"
	
def startCluster(cluster):
	AdminControl.invoke(cluster, 'start')
	print "START process for cluster initiated"  
	i=0
	bTimeout=0
	while 'true':
		state = AdminControl.getAttribute(cluster, 'state')
		print "\tnew state = " + state
		if state == "websphere.cluster.running":
			break
                if i == 40:
                        key="/ServerCluster:" + clustername + "/"
                        clusterID=AdminConfig.getid(key)
                        clusterList=AdminConfig.list('ClusterMember',clusterID)
                        servers=clusterList.split("\n")
                        for serverID in servers:
                                serverName=AdminConfig.showAttribute(serverID, 'memberName')
                                nodeName=AdminConfig.showAttribute(serverID, 'nodeName')
                                key = "type=Server,node=" + nodeName + ",process=" + serverName + ",*"
                                server = AdminControl.completeObjectName(key)
                                if len(server) != 0:
                                        print "\n" + serverName + "/" + nodeName + " started"
                                else:
                                        raise SystemExit("\nProcess timed out while starting " + serverName + "/" + nodeName)
					bTimeout=1
                        break
		else:
			print "\tcluster starting...please wait"
			time.sleep(15)
		i = i + 1
	if bTimeout == 0:
		print "Cluster has been started.\n"

	
def restartCluster(cluster):
	AdminControl.invoke(cluster, 'rippleStart')
	print "RESTART process for cluster initiated"
	while 'true':
		state = AdminControl.getAttribute(cluster, 'state')
		print "\tnew state = " + state
		if state == "websphere.cluster.running":
			break
		else:
			print "\tcluster restarting...please wait"
			time.sleep(15)
	print "Cluster has been restarted.\n"

def StopNode():
        startCmd = installRoot + "/bin/stopNode.sh"
	hostName = nodeName1[:nodeName1.find("Node")]
        rmCmd = "ssh " + hostName + " " + startCmd

        key = "type=AdminOperations,node=" + nodeName1 + ",*"
        na = AdminControl.completeObjectName(key)
        if len(na) != 0:
                print "\tStopping " + nodeName1 + "...please wait"
                print "command=" + rmCmd
                if os.system(rmCmd) != 0:
                        print "Error running cmd"
                i=0
                bTimeout=0
                while 'true':
                        nagt = AdminControl.completeObjectName(key)
                        if len(nagt) == 0:
                                break
                        else:
                                print "\tserver starting...please wait"
                                time.sleep(5)
                        if i == 72:#wait for 6 mins
				raise SystemExit("Process timed out while stopping " + nodeName1)
                                break
                        i = i + 1
                        print "Nodeagent has been stopped.\n"
        else:
                print nodeName1 + " is already stopped."

                
def StopServer(server,node):
	key = "type=Server,node=" + node + ",process=" + server + ",*"
	srvObj = AdminControl.completeObjectName(key)
	print "stop " + srvObj
	if len(srvObj) != 0:
		print "\tserver stopping...please wait"
		AdminControl.invoke(srvObj, 'stop')
		i=0
		bTimeout=0
		while 'true':
			srvObj = AdminControl.completeObjectName(key)
			if len(srvObj) == 0:
				break
			else:
				print "\tserver stopping...please wait"
				time.sleep(10)
			if i == 30:
				raise SystemExit("\nProcess timed out while stopping " + server)
				bTimeout=1
				break
			i = i + 1
		if bTimeout == 0:
			print "Server has been stopped.\n"
	else:
		print server + " is already stopped..."

def StartServer(server,node):
        key = "type=Server,node=" + node + ",process=" + server + ",*"
        srvObj = AdminControl.completeObjectName(key)
	if len(srvObj) == 0:
		print "\tStarting " + node + ":" + server + "...please wait"
		AdminControl.startServer(server, node)
		i=0
		bTimeout=0
		while 'true':
			srvObj = AdminControl.completeObjectName(key)
			if len(srvObj) != 0:
				break
			else:
				print "\tserver starting...please wait"
				time.sleep(15)
			if i == 40:
				raise SystemExit("Process timed out while starting  " + server + " on node " + node)
				bTimeout=1
				break
			i = i + 1
		if bTimeout == 0:
			print "Server has been started.\n"
	else:
		print server + " is already running"

def StartNode():
        startCmd = installRoot + "/bin/startNode.sh"
        rmCmd = "ssh " + hostName + " " + startCmd

        key = "type=AdminOperations,node=" + nodeName + ",*"
        na = AdminControl.completeObjectName(key)
        if len(na) == 0:
                print "\tStarting " + nodeName + "...please wait"
                print "command=" + rmCmd
                if os.system(rmCmd) != 0:
                        print "Error running cmd"
                i=0
                bTimeout=0
                while 'true':
                        nagt = AdminControl.completeObjectName(key)
                        if len(nagt) != 0:
                                break
                        else:
                                print "\tserver starting...please wait"
                                time.sleep(5)
                        if i == 40:
                                raise SystemExit("\nProcess timed out while starting " + nodeName)
                                bTimeout=1
                                break
                        i = i + 1
                if bTimeout == 0:
                        print "Nodeagent has been started.\n"
        else:
                print nodeName + " is already running"

#--- script start --------------#
clustername = sys.argv[0]
action = sys.argv[1]
bounceType = sys.argv[2]
deployPath = sys.argv[3]

cell = String(AdminConfig.list('Cell'))
cellname = cell.substring(0, cell.indexOf("(cells"))
key = "cell=" + cellname + ",type=Cluster,name=" + clustername + ",*"
cluster = AdminControl.completeObjectName(key)

if bounceType == 'full':
	print "\nStarting script to " + action + " cluster '" + clustername + "'\n"

	if action == 'start':
		state = AdminControl.getAttribute(cluster, 'state')
		print "\tstate = " + state
		if state == "websphere.cluster.running":
			print "Cluster " + clustername + " already started"
			sys.exit(0)
		if state == "websphere.cluster.stopped":
			startCluster(cluster)
			sys.exit(0)
		if state == "websphere.cluster.partial.stop":
			print "Cluster " + clustername + " is in PARTIAL STOP state"
			print "Cluster needs to be stopped first and then started"
			forceStopCluster(cluster)
			startCluster(cluster)
			sys.exit(0)
		if state == "websphere.cluster.partial.start":
			print "Cluster " + clustername + " is in PARTIAL START state"
			print "Cluster needs to be stopped first and then started"
			forceStopCluster(cluster)
			startCluster(cluster)
			sys.exit(0)
	
	if action == 'stop':
		state = AdminControl.getAttribute(cluster, 'state')
		print "\ncurrent state = " + state
		if state == "websphere.cluster.stopped":
			print "Cluster " + clustername + " already stopped"
			sys.exit(0)
		if state == "websphere.cluster.running":
			stopCluster(cluster)
			sys.exit(0)
		if state == "websphere.cluster.partial.stop":
			print "Cluster " + clustername + " is in PARTIAL STOP state"
			print "Cluster needs to be FORCE stopped"
			forceStopCluster(cluster)
			sys.exit(0)
		if state == "websphere.cluster.partial.start":
			print "Cluster " + clustername + " is in PARTIAL START state"
			print "Cluster needs to be FORCE stopped"
			forceStopCluster(cluster)
			sys.exit(0)
	
	if action == 'restart':
		state = AdminControl.getAttribute(cluster, 'state')
		if state == "websphere.cluster.running":
			AdminControl.invoke(cluster, 'rippleStart')
			print "RESTART process for cluster " + clustername + " initiated"
			while 'true':
				state = AdminControl.getAttribute(cluster, 'state')
				print "\tnew state = " + state
				if state == "websphere.cluster.running":
					break
				else:
					print "\tcluster restarting...please wait"
					time.sleep(15)
			print "Cluster '" + clustername + "' has been restarted.\n"
		else:
			print "Cluster " + clustername + " is in a PARTIAL STOP/START state. Use START/STOP action"

if bounceType == "partial":
	key = "/ServerCluster:" + clustername + "/"
	clusterID=AdminConfig.getid(key)
	clusterList=AdminConfig.list('ClusterMember',clusterID)
	servers=clusterList.split("\n")
	nodeName1 = AdminConfig.showAttribute(servers[0], 'nodeName')
	serverName1 = AdminConfig.showAttribute(servers[0], 'memberName')
	nodeName2 = AdminConfig.showAttribute(servers[1], 'nodeName')
	serverName2 = AdminConfig.showAttribute(servers[1], 'memberName')

	if action == 'start':
		StartServer(serverName2,nodeName2)
	if action == 'stop':
		state = AdminControl.getAttribute(cluster, 'state')
		print "\ncurrent state = " + state
		if state == "websphere.cluster.running":
			key="type=AdminOperations,node=" + nodeName1 + ",*"
			AdminOperations = AdminControl.completeObjectName(key)
			installRoot=AdminControl.invoke(AdminOperations, 'expandVariable', '${USER_INSTALL_ROOT}')
			filename = deployPath + "/" + clustername + ".dep"
			fileh = open(filename,'w')
			fileh.write(serverName1 + "," + nodeName1 + "," + installRoot)
			fileh.close()
			print "Stopping node=" + nodeName1 + ". Code will be deployed to " + nodeName2 + ":" + serverName2 + " first"
			StopNode()
			print "Stopping " + nodeName2 + ":" + serverName2
			StopServer(serverName2,nodeName2)
		else:
			raise SystemExit("Cluster " + clustername + " is not fully started. Partial deployment can't proceed.")

if bounceType == "sync":
        tempFile = deployPath + "/" + clustername + ".dep"
        fileh = open(tempFile)
        line = fileh.readline().split(',')
        serverName = line[0]
	nodeName = line[1]
        installRoot = line[2]
        hostName = nodeName[:nodeName.find("Node")]
        fileh.close()
	if action == 'stop':
	        StartNode()
	        key = "type=NodeSync,node=" + nodeName + ",*"
	        syncObjName = "AdminControl.completeObjectName('" + key + "')"
	        syncCommand = "AdminControl.invoke(" + syncObjName + ",'sync')"
		print "Synchronizing " + nodeName
	        exec syncCommand
		StopServer(serverName,nodeName)
	if action == 'start':
		StartServer(serverName,nodeName)
		os.unlink(tempFile)
