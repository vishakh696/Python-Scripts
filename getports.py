import java
lineSeparator = java.lang.System.getProperty('line.separator')

TCS = AdminConfig.getid('/Cell:' + AdminControl.getCell() + '/Node:pitdl-vswas01Node01/Server:DV1Vision/TransportChannelService:/')

chains = AdminTask.listChains(TCS,'[-acceptorFilter WebContainerInboundChannel]').split(lineSeparator)

for chain in chains:
#	print AdminConfig.showAttribute(chain,'Port')
	cStr = AdminConfig.showAttribute(chain,'transportChannels')
	channelList = cStr[1:len(cStr)-1].split(" ")
	for channel in channelList:
		if (channel.find('TCP') != -1):
			print "channel=" + channel
			endpoint = AdminTask.listTCPEndPoints(channel,'[-excludeDistinguished true -unusedOnly true]')
			print AdminConfig.showAttribute(endpoint,'Port')
#nodes = AdminConfig.list('Node').split(lineSeparator)
#for node in nodes:
#	serverEntries = AdminConfig.list('Server',node).split(lineSeparator)
#	for serverEntry in serverEntries:
#		print "server=" + serverEntry
#		namedEndPts = AdminConfig.list('HTTPTransport',serverEntry)
#		print namedEndPts
