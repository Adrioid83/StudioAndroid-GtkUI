import SourceCrespo, SourceMaguro, SourceStock, SourceP500, SourceDesire

def MakeVal(DeviceFile):
	# Import stock sources
	exec("from SourceStock import *")
	if not DeviceFile == "SourceStock":
		exec("import %s as DeviceSrc" % DeviceFile)
		NewSource, NewURL = DeviceSrc.Sources, DeviceSrc.URL
		for x in NewSource:
			i = NewSource.index(x)
			
			# delete if exists in stock sources
			if x in Sources:
				loc = Sources.index(x)
				Sources.remove(Sources[loc])
				URL.remove(URL[loc])

			# append if URL isn't empty
			if not NewURL[i] == '':
				Sources.append(x)
				URL.append(NewURL[i])

	return Sources, URL
	
