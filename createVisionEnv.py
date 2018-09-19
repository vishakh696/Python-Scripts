#---------------------------------------------------------------#
# Author: Vishakh                                            
# Description:                                                      #
# This JYTHON script is used to create new vision environment       #
#-------------------------------------------------------------------#

from java.util import *
from java.lang import *
import os

def applyConfigs(region,nodename,membername):
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

	genJVM = "-Djava.rmi.server.codebase=file:////" + installRoot + "/installedApps/" + AdminControl.getCell() + "/" + envName + "Vision.ear" + "/ExternalJars/eclipselink-2.0.2/eclipselink.jar"

	xms = ['initialHeapSize', '256']
	xmx = ['maximumHeapSize', '768']
	genJVMArg = ['genericJvmArguments', genJVM]

	attrs = []
	attrs.append(xms)
	attrs.append(xmx)
	attrs.append(genJVMArg)

	AdminConfig.modify(jvm,attrs)


	attrs = []
	attrs.append([['name','region'],['value',region]])

	AdminConfig.modify(jvm,[['systemProperties',attrs]])

	webcontainer = AdminConfig.list('WebContainer', server)
	attrs = []
	attrs.append([['name','com.ibm.ws.webcontainer.TolerateSymbolicLinks'],['value','true']])
	AdminConfig.modify(webcontainer,[['properties',attrs]])

def createNewCluster(clusterName, member1Name, node1Name, member2Name, node2Name):
	key = "[-clusterConfig [-clusterName " + clusterName + "]]"
	AdminTask.createCluster(key)

	key = "[-clusterName " + clusterName + " -memberConfig [-memberNode " + node1Name + " -memberName " + member1Name + " -memberWeight 2]]"
	AdminTask.createClusterMember(key)

	key = "[-clusterName " + clusterName + " -memberConfig [-memberNode " + node2Name + " -memberName " + member2Name + " -memberWeight 2]]"
	AdminTask.createClusterMember(key)

def applyJMSConfigs():
	queueDest = envName+"_OrderEvent_QueueDest"
	print "Creating SIB Destination.."

	busName="VisionIntegrationsBus"
	key = "[-bus " + busName + " -cluster MessageCluster -name " + queueDest + " -type queue]"
	AdminTask.createSIBDestination(key)

	me_scope = AdminConfig.getid('/ServerCluster:MessageCluster/')
	int_scope = AdminConfig.getid('/ServerCluster:' + envName + 'Integration/')

	print "Creating SIB JMS queue..."
	AdminTask.createSIBJMSQueue(me_scope, "-name " + envName + "_OutboundInternalQueue -queueName " + queueDest + " -jndiName jms/" + envName + "/OutboundInternalQueue -busName VisionIntegrationsBus")

	print "Creating JMS Activation Specs..."
	AdminTask.createSIBJMSActivationSpec(int_scope, "-name " + envName + "_OutboundInternalAS -jndiName jms/" + envName + "/OutboundInternalActivationSpec -destinationJndiName cell/clusters/MessageCluster/jms/" + envName + "/OutboundInternalQueue -busName VisionIntegrationsBus")

	print "Creating work manager..."
	key = "WorkManagerProvider(cells/" + AdminControl.getCell() + "|resources-pme.xml#WorkManagerProvider_1)"

	AdminConfig.create('WorkManagerInfo', key,[['isGrowable','true'],['jndiName', 'wm/' + envName + '/OutboundEventWorker'],['maxThreads','2'],['minThreads','0'],['numAlarmThreads','2'],['threadPriority','5'],['name',envName + '_OutboundEventWorker'],['serviceNames','']])

def createVHost():
        cell = AdminConfig.getid('/Cell:' + AdminControl.getCell() + '/')
        AdminConfig.create('VirtualHost', cell, [['name', envName + '_VH']])
        v_host = AdminConfig.getid('/VirtualHost:' + envName + '_VH/')
        console_h = ""
        vision_h = ""
        edi_h = ""
        if (envType == "1") | (envType == "3"):
                console_h = envName.lower() + "console.creditone.com"
                vision_h = envName.lower() + "vision.creditone.com"
                edi_h = envName.lower() + "edi.creditone.com"
        elif envType == "2":
                console_h = envName.lower() + "consoleaut.creditone.com"
                vision_h = envName.lower() + "visionuat.creditone.com"
                edi_h = envName.lower() + "ediuat.creditone.com"

        AdminConfig.modify(v_host, [['aliases', [[['port', '80'], ['hostname', console_h]], [['port','80'], ['hostname', vision_h]], [['port','80'], ['hostname', edi_h]]]]])

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
        dsAuthAlias = ['authDataAlias', cellNode + '/' + envName + 'VisionDBCreds']
        dsAttrs = [name, jndi, dsHelpClass, dsAuthAlias]

        newds = AdminConfig.create('DataSource', newjdbc, dsAttrs)     

        ds_props = AdminConfig.create('J2EEResourcePropertySet', newds, [])

        AdminConfig.create('J2EEResourceProperty', ds_props, [['name', 'URL'], ['value', 'jdbc:oracle:oci:@' + tnsName]])

def getEarName(EARType):
	for filename in os.listdir(earPath):
		tmpfile = filename.lower()
		if tmpfile.startswith(EARType):
			return filename

def bindJndiForEJB(DEPLOY_APP_EAR):
    # Map virtual hosts for web modules
        i = 0
        ejbmodule = ""
        uri = ""
        ejb = ""
        RES_JNDI = "jms/" + envName + "/OutboundInternalActivationSpec"
        DEST_JNDI = "cell/clusters/MessageCluster/jms/" + envName + "/OutboundInternalQueue"

        mapModuleArgument = "'-BindJndiForEJBMessageBinding',[["
        lines = AdminApp.taskInfo(DEPLOY_APP_EAR,'BindJndiForEJBMessageBinding').split("\n")
        for i in range(len(lines)):
                tmp = String(lines[i])
                if tmp.startsWith("EJB module: "):
                        ejbmodule = tmp.substring(12,tmp.length())
                if tmp.startsWith("EJB: "):
                        ejb = tmp.substring(5,tmp.length())
                if tmp.startsWith("URI: "):
                        uri = tmp.substring(5,tmp.length())

        mapModuleArgument = mapModuleArgument + "'" + ejbmodule + "','" + ejb + "','" + uri + "','','" + RES_JNDI + "','" + DEST_JNDI + "','']]"
        return (mapModuleArgument)

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
                        mapVHModuleArgument = mapVHModuleArgument + "['" + modulename + "','" + uri + "','" + envName + "_VH'],"
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
                        if modulename == 'SLVisionConsole':
                                deployto = "WebSphere:cell=" + AdminControl.getCell() + ",node=" + mcNode + ",server=" + mcMember
                        elif modulename == 'SLVisionOnline':
                                deployto = "WebSphere:cell=" + AdminControl.getCell() + ",cluster=" + onlineClusterName
                        else:
                                deployto = "WebSphere:cell=" + AdminControl.getCell() + ",cluster=" + intClusterName
                        mapModuleArgument = mapModuleArgument + "['" + modulename + "','" + uri + "','" + deployto + "'],"
                        #print "module added"
        #print mapModuleArgument
        tmpstr = String(mapModuleArgument)
        mapModuleArgument = tmpstr.substring(0,tmpstr.lastIndexOf("'")+2)
        #print "\n" + mapModuleArgument
        mapModuleArgument = mapModuleArgument + "]"
	return mapModuleArgument

def installEAR(DEPLOY_APP_EAR, APP_NAME):
	mapSharedLibArg = "'-MapSharedLibForMod', [['" + APP_NAME + "','META-INF/application.xml','" + envName + "Configs']]"

        arguments = "['-appname " + APP_NAME + "'," + getModuleToServersMapArg(DEPLOY_APP_EAR) + "," + getVirtualHostToModulesMapArg(DEPLOY_APP_EAR) + "," + mapSharedLibArg

        if String(APP_NAME).indexOf("Integrations") > 0:
                arguments = arguments + "," + bindJndiForEJB(DEPLOY_APP_EAR)

        arguments = arguments + "]"
	command = "AdminApp.install('" + DEPLOY_APP_EAR + "', " + arguments + ")"
	command = command.replace('\r','')
	exec command
	# Execute wsadmin command

def createLibRptFolder(nodeName):
        temp=String(nodeName)
        hostName=temp.substring(0, temp.indexOf("Node"))
        rptTmpDir = envName + "_ReportPDFTemp"

        folderCmd = "ssh " + hostName + " mkdir /opt/local/vision/" + envName.lower()
        if os.system(folderCmd) != 0:
                print "Error creating folder " + folderCmd
        folderCmd = "ssh " + hostName + " mkdir /opt/local/vision/" + envName.lower() + "/resources"
        if os.system(folderCmd) != 0:
                print "Error creating folder " + folderCmd
        folderCmd = "ssh " + hostName + " mkdir /" + hostName + "/" + rptTmpDir
        if os.system(folderCmd) != 0:
                print "Error creating folder " + folderCmd

def createSymLink(nodeName):
        temp=String(nodeName)
        hostName=temp.substring(0, temp.indexOf("Node"))
        rptTmpDir = envName + "_ReportPDFTemp"
        key="type=AdminOperations,node=" + nodeName + ",*"
        AdminOperations = AdminControl.completeObjectName(key)
        installRoot=AdminControl.invoke(AdminOperations, 'expandVariable', '${USER_INSTALL_ROOT}')
        symDir = installRoot + "/installedApps/" + AdminControl.getCell() + "/" + envName + "Vision.ear" + "/SLVisionOnline.war/Vision/" + rptTmpDir

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

print "Select Online node 1: "
was1 = raw_input()
print "Select Online node 2: "
was2 = raw_input()
print "Select Console node : "
mc = raw_input()
print "Select Edi1 node: "
edi1 = raw_input()
print "Select Edi2 node: "
edi2 = raw_input()

was1Node = nodeList.get(int(was1)-1)
was2Node = nodeList.get(int(was2)-1)
mcNode = nodeList.get(int(mc)-1)
edi1Node = nodeList.get(int(edi1)-1)
edi2Node = nodeList.get(int(edi2)-1)

onlineClusterName = envName + "Vision"
intClusterName = envName + "Integration"
onlineMember1 = envName + "Vision1"
onlineMember2 = envName + "Vision2"
mcMember = envName + "Console"
ediMember1 = envName + "Edi1"
ediMember2 = envName + "Edi2"

print "Creating report and shared lib folders: "
createLibRptFolder(was1Node)
createLibRptFolder(was2Node)
createLibRptFolder(mcNode)

print "Creating visionOnline Cluster..."
createNewCluster(onlineClusterName, onlineMember1, was1Node, onlineMember2, was2Node)

print "Creating Integration Cluster..."
createNewCluster(intClusterName, ediMember1, edi1Node, ediMember2, edi2Node)

print "Creating MC server..."
AdminTask.createApplicationServer(mcNode, ['-name', mcMember, '-templateName', 'default'])

print("Select Environment Type: \n1.\tDEV\n2.\tStaging or UAT\n3.\tProduction")
envType=raw_input()

env = ""

if envType == "1":
        env = "local"
elif envType == "2":
        env = "staging"
elif envType == "3":
        env = "production"

print "Applying JVM configs..."
applyConfigs(env,was1Node,onlineMember1)
applyConfigs(env,was2Node,onlineMember2)
applyConfigs(env,mcNode,mcMember)
applyConfigs(env,edi1Node,ediMember1)
applyConfigs(env,edi2Node,ediMember2)

applyJMSConfigs()

print "Creating Shared Library..."

library = AdminConfig.create('Library', AdminConfig.getid('/Cell:' + AdminControl.getCell() +'/'), [['name', envName + 'Configs'],['classPath','/opt/local/vision/' + envName.lower() + '/resources']])

print "Creating virtual host..."
createVHost()

print "Configuring JDBC..."
print "Enter vision DB user ID: "
vision_userId = raw_input()

print "Enter vision DB password:"
vision_pwd = raw_input()

print "Creating JAAS - J2C authentication alias..."
AdminConfig.create('JAASAuthData',AdminConfig.getid("/Security:/"),[["alias", cellNode + "/" + envName + "VisionDBCreds"],["userId", vision_userId],["password", vision_pwd]])

print "Enter vision DB TNS Name (e.g. STATM):"
tnsName = raw_input()

print "Creating console datasource..."
scope = '/Cell:' + AdminControl.getCell() + '/Node:' + mcNode + '/Server:' + mcMember + '/'
createDataSource(mcNode, scope, 'Console')

print "Creating vision datasource..."
scope = '/ServerCluster:' + onlineClusterName + '/'
createDataSource(was1Node, scope, 'Vision')

print "Creating Integrations datasource..."
scope = '/ServerCluster:' + intClusterName + '/'
createDataSource(edi1Node, scope, 'Integration')

print "Saving configuration...\n"
saveSync(nodeList)

print "Installing applications..."
print "Enter code stream to deploy (e.g. Vision_6.0):"
codeStream = raw_input()
print "Enter version (e.g. 6.0.0.10):"
deployVer = raw_input()

earPath = '/DeploymentPackets/Vision/' + codeStream + '/Vision/' + deployVer + '/'
visionEAR = getEarName('vision')
integrationEAR = getEarName('integration')

if (visionEAR == "")|(integrationEAR == ""):
	print "No EAR found in " + earPath + ". Aborting installation"

else:
	visionEAR = earPath + visionEAR
	integrationEAR = earPath + integrationEAR
	print "Installing Vision EAR..."
	installEAR(visionEAR, envName + 'Vision')
	print "Installing Integrations EAR..."
	installEAR(integrationEAR, envName + 'Integrations')

print "Saving configuration...\n"
saveSync(nodeList)

print "Creating symbolic link for ReportPDFTemp...:"
createSymLink(was1Node)
createSymLink(was2Node)
createSymLink(mcNode)

createEDIFolders()
