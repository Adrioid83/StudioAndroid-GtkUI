import SourceCrespo, SourceMaguro, SourceStock, SourceP500, SourceDesire

def MakeVal(DeviceFile):
	exec("from %s import *" % DeviceFile)
	return Sources, URL
