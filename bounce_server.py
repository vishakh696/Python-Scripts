#---------------------------------------------------------------#
# Author: Vishakh                                                   #
# Description:                                                      #
# This JYTHON script is used to bounce server member. Following     #
# are the args passed to it:                                        #
#       1. servername - name of app server			    #
#       2. nodename - node where app server belongs                 #
#       3. action - start/stop/restart                              #
#-------------------------------------------------------------------#

from java.lang import *
import time

servername = sys.argv[0]
nodename = sys.argv[1]
action = sys.argv[2]

cell = String(AdminConfig.list('Cell'))
cellname = cell.substring(0, cell.indexOf("(cells"))

key = "type=Server,node=" + nodename + ",process=" + servername + ",*"
server = AdminControl.completeObjectName(key)

if action == 'start':
	if len(server) == 0:
		print "\tStarting " + servername + "...please wait"
	        AdminControl.startServer(servername, nodename)
	        i=0
        	bTimeout=0
        	while 'true':
                	key = "type=Server,node=" + nodename + ",process=" + servername + ",*"
	                server = AdminControl.completeObjectName(key)
        	        if len(server) != 0:
                	        break
	                else:
        	                print "\tserver starting...please wait"
                	        time.sleep(15)
			if i == 40:
				raise SystemExit("\nProcess timed out while starting " + servername)
				bTimeout=1
				break
			i = i + 1
		if bTimeout == 0:
		        print "Server has been started.\n"
		sys.exit(0)
	else:
		print servername + " is already running"
		sys.exit(0)

if action == 'stop':
        if len(server) != 0:
		print "\tserver stopping...please wait"
                AdminControl.invoke(server, 'stop')
                i=0
                bTimeout=0
                while 'true':
			key = "type=Server,node=" + nodename + ",process=" + servername + ",*"
                        server = AdminControl.completeObjectName(key)
                        if len(server) == 0:
                                break
                        else:
                                print "\tserver stopping...please wait"
                                time.sleep(10)
                        if i == 30:
                                raise SystemExit("\nProcess timed out while stopping " + servername)
                                bTimeout=1
                                break
                        i = i + 1
                if bTimeout == 0:			
	                print "Server has been stopped.\n"
		sys.exit(0)
        else:
                print servername + " is already stopped..."
		sys.exit(0)

if action == 'restart':
        if len(server) != 0:
		print "\tserver restarting...please wait"
                AdminControl.invoke(server, 'restart')
		time.sleep(20)
                while 'true':
			key = "type=Server,node=" + nodename + ",process=" + servername + ",*"
                        server = AdminControl.completeObjectName(key)
                        if len(server) != 0:
                                break
                        else:
                                print "\tserver restarting...please wait"
                                time.sleep(10)
                print "Server has been restarted.\n"
		sys.exit(0)
        else:
                print servername + " is already stopped. Starting...please wait"
	        AdminControl.startServer(servername, nodename)
	        while 'true':
        	        key = "type=Server,node=" + nodename + ",process=" + servername + ",*"
                	server = AdminControl.completeObjectName(key)
	                if len(server) != 0:
        	                break
                	else:
                        	print "\tserver starting...please wait"
	                        time.sleep(10)
        	print "Server has been started.\n"
		sys.exit(0)
