import sys
import os
import urllib

if not sys.platform == 'darwin':
	exit(1)

ScriptDir=os.path.dirname(os.path.realpath(__file__))

gtk=None
try:
	exec("import pygtk")
except ImportError:
	urllib.urlretrieve('http://sourceforge.net/projects/macpkg/files/PyGTK/2.24.0/PyGTK.pkg/download?use_mirror=kent', os.path.join(ScriptDir, "PyGTK.pkg"))
	os.system("open %s" % os.path.join(ScriptDir, "PyGTK.pkg"))
	exit(1)
else:
	exit(0)

