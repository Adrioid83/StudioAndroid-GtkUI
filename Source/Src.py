import SourceCrespo, SourceMaguro, SourceStock, SourceP500, SourceDesire
import SourceStock

def MakeVal(DeviceFile):
	# Modifications in URL by given Source file
	reload(SourceStock)
	Sources = SourceStock.Sources
	URL = SourceStock.URL
	print "Importing %s Sources" %(DeviceFile.replace("Source", ""))
	exec("import %s as DeviceSrc" % DeviceFile)
	NewSource, NewURL = DeviceSrc.Sources, DeviceSrc.URL
	if not DeviceFile == "SourceStock":
		for x in NewSource:
			i = NewSource.index(x)
			# delete if exists in stock sources
			if x in Sources:
				loc = Sources.index(x)
				if len(NewURL) > i and NewURL[i] == '':
					print "Removing %s" % Sources[loc]
					Sources.remove(Sources[loc])
					URL.remove(URL[loc])
				else:
					print "Updating %s" % Sources[loc]
					Sources[loc] = x
					URL[loc] = NewURL[i]
			elif len(NewURL) > i and not NewURL[i] == '':
				# append if URL isn't empty
				Sources.append(x)
				URL.append(NewURL[i])
	Sources.sort()
	URL.sort()
	return Sources, URL
