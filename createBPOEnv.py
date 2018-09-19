#-------------------------------------------------------------------#
# Author: Vishakh
#
# Description:                                                      #
# This JYTHON script is used to create new BPO environment	    #
#-------------------------------------------------------------------#

from java.util import *
from java.lang import *
import os

def applyConfigs(nodename,membername):
	cellname = AdminControl.getCell()

	key = "/Cell:" + cellname + "/Node:" + nodename + "/Server:" + membername + "/"
	server = AdminConfig.getid(key)

	jvm = AdminConfig.list('JavaVirtualMachine', server)

	processDef = AdminConfig.list('JavaProcessDef', server)

	processExec = AdminConfig.list('ProcessExecution', server)

	umaskVal = ['umask', '002']
	runasusr = ['runAsUser', 'wasadmin']
	runasgrp = ['runAsGroup', 'wasgroup']

	attrs = []
	attrs.append(umaskVal)
	attrs.append(runasusr)
	attrs.append(runasgrp)

	AdminConfig.modify(processExec, attrs)


	key="type=AdminOperations,node=" + nodename + ",*"
	AdminOperations = AdminControl.completeObjectName(key)
	installRoot=AdminControl.invoke(AdminOperations, 'expandVariable', '${USER_INSTALL_ROOT}')

	genJVM = "-Djava.rmi.server.codebase=file:////" + installRoot + "/installedApps/" + AdminControl.getCell() + "/" + envName + "BPO.ear" + "/ExternalJars/eclipselink-2.0.2/eclipselink.jar"

	xms = ['initialHeapSize', '128']
	xmx = ['maximumHeapSize', '512']
	genJVMArg = ['genericJvmArguments', genJVM]

	attrs = []
	attrs.append(xms)
	attrs.append(xmx)
	attrs.append(genJVMArg)

	AdminConfig.modify(jvm,attrs)


def createNewCluster(clusterName, member1Name, node1Name, member2Name, node2Name):
	key = "[-clusterConfig [-clusterName " + clusterName + "]]"
	AdminTask.createCluster(key)

	key = "[-clusterName " + clusterName + " -memberConfig [-memberNode " + node1Name + " -memberName " + member1Name + " -memberWeight 2]]"
	AdminTask.createClusterMember(key)

	key = "[-clusterName " + clusterName + " -memberConfig [-memberNode " + node2Name + " -memberName " + member2Name + " -memberWeight 2]]"
	AdminTask.createClusterMember(key)

def createVHost():
        cell = AdminConfig.getid('/Cell:' + AdminControl.getCell() + '/')
        AdminConfig.create('VirtualHost', cell, [['name', envName + '_BPO_VH']])
        v_host = AdminConfig.getid('/VirtualHost:' + envName + '_BPO_VH/')
        bpo_h = ""
        bpo_h = envName.lower() + "bpouat.CCone.com"

        AdminConfig.modify(v_host, [['aliases', [[['port', '80'], ['hostname', bpo_h]]]]])

def createDataSource(nodename, key, prName):
        keyId = AdminConfig.getid(key)

        admOp="type=AdminOperations,node=" + nodename + ",*"

        AdminOperations = AdminControl.completeObjectName(admOp)
        oraclePath = AdminControl.invoke(AdminOperations, 'expandVariable', '${ORACLE_JDBC_DRIVER_PATH}')

        n1 = ['name', envName + prName + ' Oracle JDBC Provider']
        implCN = ['implementationClassName', 'oracle.jdbc.pool.OracleConnectionPoolDataSource']
        cpath = ['classpath', oraclePath + '/ojdbc14.jar']

        jdbcAttrs = [n1, implCN, cpath]

        AdminConfig.create('JDBCProvider', keyId, jdbcAttrs)

        newjdbc = AdminConfig.getid(key + 'JDBCProvider:' + envName + prName + ' Oracle JDBC Provider' + '/')

        name = ['name', 'VisionDataSource']
        jndi = ['jndiName', 'VisionDataSource']
        dsHelpClass = ['datasourceHelperClassname', 'com.ibm.websphere.rsadapter.Oracle10gDataStoreHelper']
        dsAuthAlias = ['authDataAlias', cellNode + '/' + envName + 'BPODBCreds']
        dsAttrs = [name, jndi, dsHelpClass, dsAuthAlias]

        newds = AdminConfig.create('DataSource', newjdbc, dsAttrs)     

        ds_props = AdminConfig.create('J2EEResourcePropertySet', newds, [])

        AdminConfig.create('J2EEResourceProperty', ds_props, [['name', 'URL'], ['value', 'jdbc:oracle:oci:@' + tnsName]])


def getVirtualHostToModulesMapArg(DEPLOY_APP_EAR):
    # Map virtual hosts for web modules
        i = 0
        j = 0
        k = 0
        mapVHModuleArgument = "'-MapWebModToVH', ["
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
                        mapVHModuleArgument = mapVHModuleArgument + "['" + modulename + "','" + uri + "','" + envName + "_BPO_VH'],"
        tmpstr = String(mapVHModuleArgument)
        mapVHModuleArgument = tmpstr.substring(0,tmpstr.lastIndexOf("'")+2)
        mapVHModuleArgument = mapVHModuleArgument + "]"
        return mapVHModuleArgument

def getModuleToServersMapArg(DEPLOY_APP_EAR):
        mapModuleArgument = "'-MapModulesToServers', ["
        deployto = ""
        modulename = ""
        lines = AdminApp.taskInfo(DEPLOY_APP_EAR,'MapModulesToServers').split("\n")

        for i in range(len(lines)):
                tmp = String(lines[i])
                if tmp.startsWith("Module: "):
                        modulename = tmp.substring(8,tmp.length())
                        #print "modulename = " + modulename
                if tmp.startsWith("URI: "):
                        uri = tmp.substring(5,tmp.length())
                        #print "uri = " + uri
                        if modulename == 'SVLOnlineWeb':
                                deployto = "WebSphere:cell=" + AdminControl.getCell() + ",cluster=" + onlineClusterName
                        mapModuleArgument = mapModuleArgument + "['" + modulename + "','" + uri + "','" + deployto + "'],"
                        #print "module added"
        #print mapModuleArgument
        tmpstr = String(mapModuleArgument)
        mapModuleArgument = tmpstr.substring(0,tmpstr.lastIndexOf("'")+2)
        #print "\n" + mapModuleArgument
        mapModuleArgument = mapModuleArgument + "]"
	return mapModuleArgument

def installEAR(DEPLOY_APP_EAR, APP_NAME):
	mapSharedLibArg = "'-MapSharedLibForMod', [['" + APP_NAME + "','META-INF/application.xml','" + envName + "BPOConfigs']]"

        arguments = "['-appname " + APP_NAME + "'," + getModuleToServersMapArg(DEPLOY_APP_EAR) + "," + getVirtualHostToModulesMapArg(DEPLOY_APP_EAR) + "," + mapSharedLibArg

        arguments = arguments + "]"
	command = "AdminApp.install('" + DEPLOY_APP_EAR + "', " + arguments + ")"
	command = command.replace('\r','')
	exec command
	# Execute wsadmin command

def createLibFolder(nodeName):
        temp=String(nodeName)
        hostName=temp.substring(0, temp.indexOf("Node"))

        folderCmd = "ssh " + hostName + " mkdir /opt/local/vision/" + envName.lower() + "bpo"
        if os.system(folderCmd) != 0:
                print "Error creating folder " + folderCmd
        folderCmd = "ssh " + hostName + " mkdir /opt/local/vision/" + envName.lower() + "bpo/resources"
        if os.system(folderCmd) != 0:
                print "Error creating folder " + folderCmd

def createSymLink(nodeName):
        temp=String(nodeName)
        hostName=temp.substring(0, temp.indexOf("Node"))
        rptTmpDir = envName + "_ReportPDFTemp"
        key="type=AdminOperations,node=" + nodeName + ",*"
        AdminOperations = AdminControl.completeObjectName(key)
        installRoot=AdminControl.invoke(AdminOperations, 'expandVariable', '${USER_INSTALL_ROOT}')
        symDir = installRoot + "/installedApps/" + AdminControl.getCell() + "/" + envName + "Vision.ear" + "/visionOnline.war/Vision/" + rptTmpDir

        symCmd = "ssh " + hostName + " ln -s /" + hostName + "/" + rptTmpDir + " " + symDir
        if os.system(symCmd) != 0:
                print "Error creating symbolic link " + symCmd

def createEDIFolders():
        temp=String(mcNode)
        hostName=temp.substring(0, temp.indexOf("Node"))

	print "Creating /VISION/" + envName.upper() + "_EDI folder structure..." 
	folderCmd = "scp -r JVM_EDI " + hostName + ":/VISION/" + envName.upper() + "_EDI"
	if os.system(folderCmd) != 0:
		print "Error creating folder " + folderCmd

	perCmd = "ssh " + hostName + " chmod -R 777 /VISION/" + envName.upper() + "_EDI"
	if os.system(perCmd) != 0:
		print "Error changing permission " + perCmd

	print "Creating /opt/IMAGING/" + envName.upper() + "_EDI folder structure..."
	folderCmd = "scp -r IMAGING/JVM_EDI " + hostName + ":/opt/IMAGING/" + envName.upper() + "_EDI"
	if os.system(folderCmd) != 0:
		print "Error creating folder " + folderCmd

	perCmd = "ssh " + hostName + " chmod -R 777 /opt/IMAGING/" + envName.upper() + "_EDI"
	if os.system(perCmd) != 0:
		print "Error changing permission " + perCmd

def saveSync(nodeList):
	AdminConfig.save()
	for j in range(nodeList.size()):
		node = nodeList.get(j)
		syncObjName = "AdminControl.completeObjectName('type=NodeSync,node=" + nodeList.get(j) + ",*')"
		key = "type=NodeSync,node=" + nodeList.get(j) + ",*"
		if len(AdminControl.completeObjectName(key)) != 0:
			syncCommand = "AdminControl.invoke(" + syncObjName + ",'sync')"
			syncCommand = syncCommand.replace('\r','')
			print "Synchronizing ",node
			exec syncCommand

#***************Main Body*****************
print "Enter environemt name (e.g. ATM): "
envName = raw_input()
envName = envName.upper()
nodeList = ArrayList()
nodes = AdminConfig.list('Node').split("\n")
cellNode = ""

for i in range(len(nodes)):
	temp = String(nodes[i])
	node = temp.substring(0, temp.indexOf("(cells"))
	tmpNode = String(node)
	if tmpNode.indexOf("Cell") > 0:
		cellNode = node
	x = node.count("dmgr")
	y = node.count("http")
        if x == 0:
                if y == 0:
			if tmpNode.indexOf("Node") > 0:
				nodeList.add(node)		

if cellNode == "":
        cellNode = AdminControl.getCell()

print "List of nodes: "
j=0
for j in range(nodeList.size()):
	print j+1,"-",nodeList.get(j)

print "Select node 1: "
was1 = raw_input()
print "Select node 2: "
was2 = raw_input()

was1Node = nodeList.get(int(was1)-1)
was2Node = nodeList.get(int(was2)-1)

onlineClusterName = envName + "BPO"
onlineMember1 = envName + "BPO1"
onlineMember2 = envName + "BPO2"

print "Creating shared lib folders: "
createLibFolder(was1Node)
createLibFolder(was2Node)

print "Creating BPO Cluster..."
createNewCluster(onlineClusterName, onlineMember1, was1Node, onlineMember2, was2Node)

print("Select Environment Type: \n1.\tDEV\n2.\tStaging or UAT\n3.\tProduction")
envType=raw_input()

print "Applying JVM configs..."
applyConfigs(was1Node,onlineMember1)
applyConfigs(was2Node,onlineMember2)

print "Creating Shared Library..."

library = AdminConfig.create('Library', AdminConfig.getid('/Cell:' + AdminControl.getCell() +'/'), [['name', envName + 'BPOConfigs'],['classPath','/opt/local/vision/' + envName.lower() + 'bpo/resources']])

print "Creating virtual host..."
createVHost()

print "Configuring JDBC..."
print "Enter vision DB user ID: "
vision_userId = raw_input()

print "Enter vision DB password:"
vision_pwd = raw_input()

print "Creating JAAS - J2C authentication alias..."
AdminConfig.create('JAASAuthData',AdminConfig.getid("/Security:/"),[["alias", cellNode + "/" + envName + "BPODBCreds"],["userId", vision_userId],["password", vision_pwd]])

print "Enter vision DB TNS Name (e.g. STATM):"
tnsName = raw_input()

print "Creating datasource..."
scope = '/ServerCluster:' + onlineClusterName + '/'
createDataSource(was1Node, scope, 'BPO')

print "Saving configuration...\n"
saveSync(nodeList)

print "Installing applications..."
print "Enter full path of EAR to deploy:"
earPath = raw_input()

print "Installing BPO EAR..."
installEAR(earPath, envName + 'BPO')

print "Saving configuration...\n"
saveSync(nodeList)
