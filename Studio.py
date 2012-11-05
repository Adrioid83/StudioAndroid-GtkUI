
#############
## IMPORTS ##
#############
from __future__ import division
# BASE IMPORTS
import os, sys, platform, commands
from distutils.sysconfig import get_python_lib
# GUI
import gtk, pygtk, gobject
pygtk.require('2.0')
# UTILITIES
import shutil
import fnmatch
import webbrowser, urllib, urllib2 # BROWSER
from HTMLParser import HTMLParser
# REST
import string
from itertools import izip
import array
import random
import time
import zipfile, tarfile # ARCHIVE
# THREADING
import threading, multiprocessing, subprocess
# TRANSLATION
import gettext,locale
import Source.Src
_ = gettext.gettext



# TRY TO IMPORT PIL FOR INTERNAL IMAGE MODIFICATION
try: 
	from PIL import Image as PILImage
	from PIL import ImageOps as PILImageOps
	from PIL import ImageEnhance as PILImageEnhance
	from PIL import ImageColor as PILImageColor
	from PIL import ImageDraw as PILImageDraw
	from PIL import ImageFont as PILImageFont
except: Pil = False
else:	Pil = True

def TogglePil(widget):
	global Pil  # So the user can toggle PIL usage
	if widget.get_active():Pil = True
	else: Pil = False
	print("PIL = %s" % ["Disabled", "Enabled"][widget.get_active()])


# VARIABLES
ScriptDir=os.path.dirname(os.path.realpath(__file__))
Home=os.path.expanduser('~')
ConfDir = os.path.join(Home, ".STUDIO")
OmegaDir = os.path.join(ScriptDir, "Omega")
ImageDir = os.path.join(ScriptDir, "Image")
MyFile = os.path.basename(__file__)
FullFile = os.path.abspath(os.path.realpath(__file__))
Cores = str(multiprocessing.cpu_count())
Python = os.path.abspath(sys.executable)
PythonDir = os.path.dirname(Python)
ThemeDir = os.path.join(ScriptDir, "Utils", "Themes", "Theme")

if os.path.exists(ThemeDir): # IF ANY THEME IS EXTRACTED, APPLY IT
	try:
		gtk.rc_parse(os.path.join(ThemeDir, "gtk-2.0", "gtkrc"))
	except:pass

Trees = ["Omega", ["Working", "Templates", "Download", "Build"], "ADB", "Advance", ["ODEX", ["IN", "OUT", "WORKING", "CURRENT"], "PORT", ["ROM", "TO", "WORKING"], "Smali", ["IN", "OUT", "Smali"]], "APK", ["IN", "DEC", "EX", "OUT"], "Image", ["Resized", "Theme"]]


# TO FIX OTS <-> SA DEPENDENCIES
class ToolAttr:
	if not os.path.exists(ConfDir): os.makedirs(ConfDir)
	VersionFile = os.path.join(ConfDir, "Custom")
	Changelog = os.path.join(ScriptDir, "changelog")
	with open(Changelog, "r") as f:
		versionNo = f.readlines()[-1].replace("\n", "")
	if os.path.exists(VersionFile):
		with open(VersionFile, "r") as f:
			toggledVersion = f.readline()
		if "omega" in toggledVersion:
			OmegaVersion = True
		else: OmegaVersion = False
	else: OmegaVersion = False

	# Debug
	if os.path.exists(os.path.join(ConfDir, "debug")):Debug = True
	else:Debug = False


	GitLink = "http://github.com/mDroidd/StudioAndroid-GtkUI/"
	DropboxLink = "http://dl.dropbox.com/u/61466577/"
	if OmegaVersion == True:
		ToolName = "OmegaThemeStudio"
		Name = "OTS"
		StableBranch = "tags"
		UnstableBranch = "zipball/master"
	else:
		ToolName = "StudioAndroid"
		Name = "SA"
		StableBranch = "tags"
		UnstableBranch = "zipball/master"



# OS Determination

if sys.platform == 'linux2':
	OS = 'Lin'
elif sys.platform == 'win32':
	OS = 'Win'
elif sys.platform == 'win64':
	OS = 'Win'
elif sys.platform == 'darwin':
	OS = 'Mac'
else:
	OS = 'Default'

if (sys.maxsize > 2**32) == True: bit = 64
else: bit = 32

PATH = []
if OS == "Win": sep = ";"
else: sep = ":"
for x in str(os.environ["PATH"]).split(sep): PATH.append(x)



# APPLY LANGUAGE

if not os.path.exists(os.path.join(ConfDir, "Language")):
	with open(os.path.join(ConfDir, "Language"), "w") as f:
		f.write("en_US")

DIR = os.path.join(ScriptDir, "lang")
APP = 'Studio'
gettext.textdomain(APP)
gettext.bindtextdomain(APP, DIR)
#gettext.bind_textdomain_codeset("default", 'UTF-8')
locale.setlocale(locale.LC_ALL, "")
Language = open(os.path.join(ConfDir, "Language"), "r").read()
LANG = Language

lang = gettext.translation(APP, DIR, languages=[LANG], fallback = True)
_ = lang.gettext
	


# Double output
class Logger(object):
    OldStdout = sys.stdout
    OldStderr = sys.stderr
    def __init__(self):
        self.terminal = sys.stdout

    def write(self, message):
        self.terminal.write(message)
	with open(os.path.join(ScriptDir, "log"), "a") as log:
		log.write(message)  
		log.flush()

sys.stdout = Logger()
sys.stderr = Logger()

# External Output redirection

def SystemLog(cmd, Debug=ToolAttr.Debug):
	if ToolAttr.Debug == True:
		print(cmd)
		pr = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
		while True:
			line = pr.stdout.readline()
			if not line: break
			print line.replace("\n", "")
	elif ToolAttr.Debug == False:
		os.system(cmd)


# GTK TOOLS

def delete_event(self, widget, event, data=None):
	gtk.main_quit()
	return False

def destroy(self, widget, data=None):
	gtk.main_quit()

def Restart(cmd):
	python = sys.executable
	os.execl(python, python, * sys.argv)

def FileChoose(FileChooser, filtern=None, multiple=False):
	if not filtern == None:
		filter = gtk.FileFilter()
		filter.set_name(filtern)
		filter.add_mime_type(filtern)
		filter.add_pattern("*" + filtern)
		FileChooser.add_filter(filter)
	FileChooser.set_select_multiple(multiple)
	FileChooser.set_current_folder(ScriptDir)
	response = FileChooser.run()
	FileChooser.hide()
	if response == gtk.RESPONSE_OK:
		Chosen = FileChooser.get_filename()
		return Chosen

def GetFile(cmd, FileChooser, BtnChange=False, Multi=False, filtern=None):
	Returned = FileChoose(FileChooser, filtern, Multi)
	if not BtnChange == False:
		Btn = BtnChange[0]
		label = str(Btn.get_label()).split(" :")[0]
		Btn.set_label("%s : %s" %(label, Returned))
	MainApp.Out = Returned

class FileChooserD:
	out = None
	def openFile(self, widget, FileChooser, filters=[], multiple=False, SetTo=False):
		self.out = self.run(FileChooser, filters, multiple) # run FileChooserD with the given arguments
		print self.out
		if not self.out == None:
			if not SetTo == False:
				SetTo(self.out) # set button label to OUT if Btn is given
		return self.out

	def run(self, FileChooser, filters=[], multiple=False):
		# Set dependencies
		if isinstance(filters, str): filters=[filters]
		for filtern in filters:
			filter = gtk.FileFilter()
			filter.set_name(filtern)
			filter.add_mime_type(filtern)
			filter.add_pattern("*" + filtern)
			FileChooser.add_filter(filter)
		FileChooser.set_select_multiple(multiple)
		FileChooser.set_current_folder(ScriptDir)
		response = FileChooser.run()
		FileChooser.hide()
		Chosen = None
		if response == gtk.RESPONSE_OK:
			if multiple == False:Chosen = FileChooser.get_filenames()[0]
			else:Chosen = FileChooser.get_filenames()
		return Chosen

class FileChooserFile(FileChooserD):
	def openFile(self, widget, title="Open...", filters=[], multiple=False, SetTo=False):
		FileChooser = gtk.FileChooserDialog(title, None, gtk.FILE_CHOOSER_ACTION_OPEN, 
						(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		self.out = self.run(FileChooser, filters, multiple) # run FileChooserDialog with the given arguments
		if self.out == None and SetTo:
			SetTo(self.out) # set button label to OUT if Btn is given
		return self.out

class FileChooserDir(FileChooserD):
	def openFile(self, widget, title="Open...", filters=[], multiple=False, SetTo=False):
		FileChooser = gtk.FileChooserDialog(title,action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                  	buttons=(gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		self.out = self.run(FileChooser, filters, multiple) # run FileChooserDialog with the given arguments
		if self.out == None and SetTo:
			SetTo(self.out) # set button label to OUT if Btn is given
		return self.out

def NewDialog(Title, Text):
	dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK)
	dialog.set_markup("<b>%s</b>" % Title)
	dialog.format_secondary_markup("%s" % Text)
	dialog.run()
	dialog.destroy()

def ChooseDialog(Title, Text, Btns=[]):
	BtnTup = ()
	for x in Btns:
		BtnTup += (x, range(0,10)[Btns.index(x)])
	dialog = gtk.Dialog(Title, None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,BtnTup)
	label = gtk.Label(Text)
	dialog.vbox.pack_start(label)
	label.show()
	dialog.show_all()
	response = dialog.run()
	dialog.hide_all()
	dialog.destroy()
	return response

def KillPage(widget, child, notebook=False, Destroy=True):
	if notebook == False: notebook=MainApp.notebook
	current = notebook.get_current_page()

	page = notebook.page_num(child)
	if page == -1:
		page = notebook.get_n_pages() - 1
	notebook.remove_page(page)
	if Destroy:
		child.destroy()

	if current == page:
		notebook.set_current_page(notebook.get_n_pages() - 1)

def NewPage(Label, parent):
	box = gtk.HBox()
	closebtn = gtk.Button()
	image = gtk.Image()
	image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
	closebtn.connect("clicked", KillPage, parent)
	closebtn.set_image(image)
	image.set_size_request(10, 10)
	closebtn.set_relief(gtk.RELIEF_NONE)
	box.pack_start(gtk.Label(Label), False, False)
	box.pack_end(closebtn, False, False)
	box.show_all()
	return box

def NewPageBox():
	vbox = gtk.VBox()
	box = gtk.HBox()
	vbox.pack_start(box, False, False)
	closebtn = gtk.Button()
	image = gtk.Image()
	image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
	closebtn.connect("clicked", KillPage, vbox)
	closebtn.set_image(image)
	image.set_size_request(10, 10)
	closebtn.set_relief(gtk.RELIEF_NONE)
	box.pack_end(closebtn, False, False)
	vbox.show_all()
	return vbox

def CurrentPageText(notebook, data):
	TabName = notebook.get_tab_label_text(notebook.get_nth_page(data))
	return TabName

# Shotcuts 
sz = os.path.join(ScriptDir, "Utils", "7za")
UtilDir = os.path.join(ScriptDir, "Utils")
SourceDir = os.path.join(ScriptDir, "Source")
ApkJar = os.path.join(ScriptDir, "Utils", "apktool.jar")
adb = os.path.join(ScriptDir, "Utils", "adb")
SignJar = os.path.join(ScriptDir, "Utils", "signapk.jar")
ZipalignFile = os.path.join(ScriptDir, "Utils", "zipalign")
SmaliJar = os.path.join(ScriptDir, "Utils", "smali-1.3.2.jar")
BaksmaliJar = os.path.join(ScriptDir, "Utils", "baksmali-1.3.2.jar")
OptPng = os.path.join(ScriptDir, "Utils", "optipng")
Web = webbrowser.get()
GovDir = os.path.join(UtilDir, "Gov")

# MAC OSX Fix
def ExZip(zipf, expath, type='zip', pattern='*', Overwrite=True):
	if not os.path.exists(expath): os.makedirs(expath)
	if type == 'zip':
		Zip = zipfile.ZipFile(zipf, "r")
		namelist = Zip.namelist()
	else:
		Zip = tarfile.open(zipf, "r")
		namelist = Zip.getnames()
	for f in namelist:
		if f.endswith(os.sep):
			if not os.path.exists(os.path.join(expath, f)):os.makedirs(os.path.join(expath, f))
		else: 
			if fnmatch.fnmatch(f, pattern):
				filename = os.path.join(expath, f)
				if Overwrite == True and os.path.exists(filename): os.remove(filename)
				if not os.path.exists(filename):
					Zip.extract(f, path=expath)

def ExTo(zipf, expath, type='zip', pattern="*", ign=[]):
	if isinstance(ign, str): ign=[ign]
	zip_file = zipfile.ZipFile(zipf, 'r')
	for member in zip_file.namelist():
		filename = os.path.basename(member)
		# skip directories
		if not filename:continue
		# copy file (taken from zipfile's extract)
		source = zip_file.open(member)
		if fnmatch.fnmatch(filename, pattern) and [match for match in ign if fnmatch.fnmatch(filename, match)] == []: 
			target = file(os.path.join(expath, filename), "wb")
			shutil.copyfileobj(source, target)
			target.close()
		source.close()
	zip_file.close()

try:
	for x in ["", "-" + OS]:
		if not os.path.exists(os.path.join(ScriptDir, "Utils%s.zip" %(x))):
			print _("Downloading Utils%s.zip" %(x))
			urllib.urlretrieve(ToolAttr.DropboxLink + "Utils%s.zip" %(x), os.path.join(ScriptDir, "Utils%s.zip" %(x)))
		ExZip(os.path.join(ScriptDir, "Utils%s.zip" %(x)), ScriptDir, Overwrite=False)
	# FIX PERMISSIONS
	if not OS == "Win":
		for filen in os.listdir(UtilDir):
			filen = os.path.join(UtilDir, filen)
			os.chmod(filen, 0755)
		os.chmod(os.path.join(SourceDir, "Build.sh"), 0755)
except:
	print _("Downloading Utils.zip failed...")


def callback(widget, option):
	if not option == None:
		# REDIRECTS THE BUTTON OPTION TO A FUNCTION
		try: globals()[option]
		except KeyError: 
			try:
				option()
			except:
				print _("%s is not defined yet, SORRY!" % option)
		else:
			#threading.Thread(None, globals()[option]).start()
			globals()[option]()


def StartThread(widget, function, args=(), merge=True):
	if merge == True: arg = (widget,)+args
	else: arg = args
	thread = threading.Thread(None, function, args=arg)
	thread.start()
	return thread

# Basic AddToList
def AddToList(widget, List, name):
	if widget.get_active():
		List.append(name)
	else:
		List.remove(name)
	return List

def SetXml(File, list):
	file = open(File, "r")
	newLines = []
	i = 0
	for line in file.readlines():
		line = line.replace("\n", "")
		if "<" and '">' in line and not i == 0:
			value = line.split('"')[1]
			set = str(line.rsplit("<", 1)[0]).split(">", 2)[1]
			for x in list:
				if x[0] == value: break
			newLines.append(line.split(">", 1)[0]  + ">%s<" %(str(x[1])) + line.rsplit("<", 1)[-1])
		else:
			newLines.append(line)
		i += 1	
	file.close()
	writeFile = open(File, "w")
	writeFile.write('\n'.join(newLines))
	writeFile.close()

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def remove_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# IMAGE TOOLS
def RGBToHTMLColor(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple
    # that's it! '%02x' means zero-padded, 2-digit hex values
    return hexcolor
# (C) ActivateState


def pallette_convert(image):
	pb = gtk.gdk.pixbuf_new_from_file(image)
	pb.save(image, image.rsplit('.', 1)[-1])
	im = PILImage.open(image) #pixbuf2image(pb) not working
	return im

def image2pixbuf(im):
	arr = array.array('B', im.tostring())
	width, height = im.size
	return gtk.gdk.pixbuf_new_from_data(arr, gtk.gdk.COLORSPACE_RGB, True, 8, width, height, width * 4)

def pixbuf2image(pb):
	width,height = pb.get_width(),pb.get_height()
	return PILImage.fromstring("RGB",(width,height),pb.get_pixels())
#

def strip_esc(s):
	delete = ""
	i=1
	while (i<0x20):
		delete += chr(i)
		i += 1
	return s.translate(None, delete)


def find_files(directory, pattern):
    names = []
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                names.append(filename)
    names.sort()
    return names
# FindFiles (C) StackOverflow



def CopyTree(src, dst, overwrite=True, filter="*"):
	src = os.path.join(src, '')
	dst = os.path.join(dst, '')
	if not os.path.exists(dst):
		os.makedirs(dst)
	for file in find_files(src, filter):
		dir = os.path.dirname(file).replace(src, dst)
		if not os.path.exists(dir):
			os.makedirs(dir)
		if not os.path.exists(file.replace(src, dst)):
			shutil.copy(file, str(file).replace(src, dst))
		if os.path.exists(file.replace(src, dst)) and overwrite == True:
			os.remove(file.replace(src, dst))
			shutil.copy(file, file.replace(src, dst))
			
		
def ParseTree(base, tree, start=[]):
	for x in tree:
		if isinstance(x, str):
			start.append(os.path.join(base, x, ''))
		else:
			ParseTree(os.path.join(base, tree[tree.index(x) - 1], ''), x, start)
	return start

for Dir in ParseTree(ScriptDir, Trees):
	if not os.path.isdir(Dir):
		try:
			os.makedirs(Dir)
		except: print Dir

if " " in ScriptDir:
	print _("You extracted %s in a path with spaces!\nI'm not responsible for your errors now!" % ToolAttr.ToolName)

# DEFINE WINDOW
window = gtk.Window(gtk.WINDOW_TOPLEVEL)
window.set_title("%s" %(ToolAttr.ToolName,))
window.connect("delete_event", delete_event, 0)
window.set_border_width(15)
window.set_size_request(750,500)
window.set_resizable(True)
window.set_position(gtk.WIN_POS_CENTER)



vbox = gtk.VBox(False, 5)
hbox = gtk.HBox(False, 5)



# PRINT INFO

Weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
Months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
Weekday = Weekdays[time.localtime()[6]]
Month = Months[time.localtime()[1]]

def date():
	date = "%s-%s-%s--%s.%s.%s" %(time.localtime()[0], time.localtime()[1], time.localtime()[2], time.localtime()[3], time.localtime()[4], time.localtime()[5])
	return date


print("### %s %s %s - %s:%s:%s ###" %(Weekday, time.localtime()[2], Month, time.localtime()[3], time.localtime()[4], time.localtime()[5]) )
print ("OS = %s %s-bit" %(OS, bit))
print _("PythonDir = %s" %(PythonDir))
print _("Cores = %s" %(Cores))
print _("Home = %s" %(Home))
print _("ScriptDir = %s" %(ScriptDir))
on = _("Enabled")
off = _("Disabled")
print ("Debug = %s, PIL = %s, Omega = %s" %([on, off][ToolAttr.Debug], [on, off][Pil], [on, off][ToolAttr.OmegaVersion]))
print _("Language = %s" %(Language))



class MainApp:
	# MAIN APP
	placeIcon = gtk.gdk.pixbuf_new_from_file(os.path.join(ScriptDir, "images", "icon.png"))
	window.set_icon(placeIcon)
	DevelopMenu = False

	#
	# OPTION BAR
	#

	global menu

	vbox = gtk.VBox()

	menu = gtk.MenuBar()
	OptionsMenu = gtk.MenuItem( _("Options") )
	Options = gtk.Menu()
	menu.append(OptionsMenu)
	OptionsMenu.set_submenu(Options)

	MainOptCl = gtk.MenuItem( _("Reset"))
	MainOptCl.connect("activate", callback, "Clean")
	Options.append(MainOptCl)

	LogOption = gtk.MenuItem( _("Check the log") )
	LogOption.connect("activate", callback, "Log")
	Options.append(LogOption)

	ReportBug = gtk.MenuItem( _("Report a bug") )
	ReportBug.connect("activate", callback, "Bug")
	Options.append(ReportBug)

	sep = gtk.SeparatorMenuItem()
	Options.append(sep)


	ChangelogOption = gtk.MenuItem( _("Changelog"))
	ChangelogOption.connect("activate", callback, "Changelog")
	Options.append(ChangelogOption)

	UpdateOption = gtk.MenuItem( _("Update"))
	UpdateOption.connect("activate", callback, "Update")
	Options.append(UpdateOption)


	RestartOption = gtk.MenuItem( _("Restart"))
	RestartOption.connect("activate", Restart)
	Options.append(RestartOption)

	sep = gtk.SeparatorMenuItem()
	Options.append(sep)

	AboutOption = gtk.MenuItem("About")
	Options.append(AboutOption)
	AboutOption.connect("activate", callback, "About")

	sep = gtk.SeparatorMenuItem()
	Options.append(sep)

	CstToggle = gtk.MenuItem("Customize!")
	Options.append(CstToggle)
	CstToggle.connect("activate", callback, "Customize")



	menu.show_all()

	vbox.pack_start(menu, False, False, 0)

	notebook = gtk.Notebook()
	notebook.popup_enable()
	notebook.set_tab_pos(gtk.POS_TOP)
	vbox.pack_start(notebook)
	notebook.set_scrollable(True)

	notebook.show()

	# IMAGE TAB

	UtilVBox = gtk.VBox()

	UtilLabel = gtk.Label( _("Images"))

	image = gtk.Image()
	image.set_from_file(os.path.join(ScriptDir, "images", "Images.png"))
	image.show()
	UtilVBox.pack_start(image, False, False, 10)

	for Opt in [[_("Install Image Tools"), "Utils"], [_("Convert Image"), "ConvertImage"], [_("Resize"), "Resize"], [_("Batch Theme"), "Theme"], [_("Batch Rename"), "Rename"], [_("CopieFrom"), "CopyFrom"], [_("Optimize Images"), "OptimizeImage"]]:
		Btn = gtk.Button(Opt[0])
		Btn.connect("clicked", callback, Opt[1])
		UtilVBox.pack_start(Btn, True, False, 10)

	notebook.insert_page(UtilVBox, UtilLabel, 1)

	# DEVELOP TAB

	DevelopLabel = gtk.Label( _("Development") )
	DevelopVBox = gtk.VBox()

	image = gtk.Image()
	image.set_from_file(os.path.join(ScriptDir, "images", "Develop.png"))
	image.show()
	DevelopVBox.pack_start(image, False, False, 10)

	if not OS == 'Win':
		MainOpt6 = gtk.Button( _("Prepare Building") )
		MainOpt6.connect("clicked", callback, "PrepareBuilding")
		DevelopVBox.pack_start(MainOpt6, True, False)

		MainOpt7 = gtk.Button( _("Build from Source") )
		MainOpt7.connect("clicked", callback, "BuildSource")
		DevelopVBox.pack_start(MainOpt7, True, False)

		MainOpt9 = gtk.Button( _("Add Governor") )
		MainOpt9.connect("clicked", callback, "AddGovernor")
		DevelopVBox.pack_start(MainOpt9, True, False)

	for opt in [[_("Install Android-SDK"), "SDK"], [("Install Java JDK"), "JDK"], [_("Install Eclipse"), "Eclipse"], [_("Port a ROM (DO NOT USE)"), "BinaryPort"]]:
		OptBtn = gtk.Button(opt[0])
		OptBtn.connect("clicked", callback, opt[1])
		DevelopVBox.pack_start(OptBtn, True, False)

	notebook.insert_page(DevelopVBox, DevelopLabel, 2)

	# APK TAB

	ApkLabel = gtk.Label("APK")
	APKVBox = gtk.VBox(False, 10)

	image = gtk.Image()
	image.set_from_file(os.path.join(ScriptDir, "images", "APK.png"))
	image.show()
	APKVBox.pack_start(image, False, False, 10)

	for opt in [[_("(De)Compile"), "DeCompile"], [_("Extract/Repackage"), "ExPackage"], [_("Sign / Create signature"), "Sign"], [_("Zipalign APK"), "Zipalign"], [_("Install APK"), "Install"], [_("Optimize Image Inside APK"), "OptimizeInside"]]:
		OptBtn = gtk.Button(opt[0])
		OptBtn.connect("clicked", callback, opt[1])
		APKVBox.pack_start(OptBtn, True, False, 10)

	notebook.insert_page(APKVBox, ApkLabel, 3)

	# ADVANCE TAB

	AdvanceVBox = gtk.VBox()
	AdvanceLabel = gtk.Label( _("Advanced") )

	image = gtk.Image()
	image.set_from_file(os.path.join(ScriptDir, "images", "Advanced.png"))
	image.show()
	AdvanceVBox.pack_start(image, False, False, 10)

	for opt in [[_("(Bak)Smali"), "BakSmali"], [_("ODEX"), "Odex"], [_("DE-ODEX"), "Deodex"], [_("Aroma Menu"), "Aroma"], [_("Compile to an exe"), "Compile"]]:
		OptBtn = gtk.Button(opt[0])
		OptBtn.connect("clicked", callback, opt[1])
		AdvanceVBox.pack_start(OptBtn, True, False, 10)

	if not ToolAttr.OmegaVersion == True:
		notebook.insert_page(AdvanceVBox, AdvanceLabel, 4)

	# ANDROID TAB

	AndroidVBox = gtk.VBox()
	AndroidLabel = gtk.Label( _("Android") )

	image = gtk.Image()
	image.set_from_file(os.path.join(ScriptDir, "images", "Android.png"))
	image.show()
	AndroidVBox.pack_start(image, False, False, 10)

	ADBBtn = gtk.Button(_("Configure ADB"))
	ADBBtn.connect("clicked", callback, 'ADBConfig')
	AndroidVBox.pack_start(ADBBtn, True, False, 10)

	LogcatBtn = gtk.Button(_("Logcat"))
	LogcatBtn.connect("clicked", callback, 'LogCat')
	AndroidVBox.pack_start(LogcatBtn, True, False, 10)

	BuildPropBtn = gtk.Button(_("Build.prop ADB"))
	BuildPropBtn.connect("clicked", callback, 'BuildProp')
	AndroidVBox.pack_start(BuildPropBtn, True, False, 10)

	BackUpBtn = gtk.Button(_("Backup / Restore"))
	BackUpBtn.connect("clicked", callback, "BackupRestore")
	AndroidVBox.pack_start(BackUpBtn, True, False, 10)

	AdbFEBtn = gtk.Button(_("ADB File Explorer"))
	AdbFEBtn.connect("clicked", callback, "AdbFE")
	AndroidVBox.pack_start(AdbFEBtn, True, False, 10)

	if not ToolAttr.OmegaVersion == True:
		notebook.insert_page(AndroidVBox, AndroidLabel, 5)

	# OMEGA TAB

	OmegaVbox = gtk.VBox()
	OmegaLabel = gtk.Label(_("Omega"))

	for x in [[_("Omega Statusbar"), "OmegaSB"], [_("Compile to an exe"), "Compile"]]:
		OmegaBtn = gtk.Button(x[0])
		OmegaBtn.connect("clicked", callback, x[1])
		OmegaVbox.pack_start(OmegaBtn, True, False)

	if ToolAttr.OmegaVersion == True:
		notebook.insert_page(OmegaVbox, OmegaLabel)

	# END, show main tab
	window.add(vbox)

	vbox.show_all()
	window.show_all()

class GlobalData():
	AdbOpts = ''

# FROM HERE, ALL FUNCTIONS USED IN MAINAPP WILL BE DEFINED

def Clean():
	for tree in ParseTree(ScriptDir, Trees):
		shutil.rmtree(tree, True)
	shutil.rmtree(os.path.join(ConfDir), True)
	os.remove(os.path.join(ScriptDir, "log"))
	shutil.rmtree(UtilDir)
	try:
		os.remove(os.path.join(ScriptDir, 'Source', 'syncswitches'))
		os.remove(os.path.join(ScriptDir, 'Source', 'repocmd'))
	except OSError:pass

	for x in find_files(ScriptDir, "*.pyc"):
		try:os.remove(x)
		except:pass

class Utils:
	LabelText = _("ImageMagick is needed for all image tools I included.\nIn future releases I will use PIL more. So install PIL too!")
	PageTitle = _("Install Image Tools")
	Java = False
	PyWin = False
	PIL = True
	IM = True
	def __init__(self):
		notebook = MainApp.notebook
		vbox = gtk.VBox()
		hbox = gtk.HBox(True)

		label = gtk.Label(self.LabelText)
		label.set_justify(gtk.JUSTIFY_CENTER)
		vbox.pack_start(label, False, False, 0)

		ImageVbox = gtk.VBox()
		hbox.pack_start(ImageVbox)
		vbox.pack_start(hbox)

		self.ImageBtn = gtk.CheckButton("ImageMagick")
		if self.IM == True:
			ImageVbox.pack_start(self.ImageBtn)
		self.PILBtn = gtk.CheckButton("Python Image Library")
		if self.PIL == True:
			ImageVbox.pack_start(self.PILBtn)
			if Pil == False: self.PILBtn.set_active(True)

		OtherVbox = gtk.VBox()
		hbox.pack_start(OtherVbox)
		self.JavaBtn = gtk.CheckButton("JAVA")
		if self.Java == True:
			self.JavaBtn.set_active(True)
			OtherVbox.pack_start(self.JavaBtn)
		self.PyWin32Btn = gtk.CheckButton("PyWin32")
		if self.PyWin == True:
			self.PyWin32Btn.set_active(True)
			OtherVbox.pack_start(self.PyWin32Btn)

		buttonInstall = gtk.Button( _("Install") )
		buttonInstall.connect("clicked", StartThread, self.Install)
		vbox.pack_start(buttonInstall, False, False, 0)

		UtilsLabel = NewPage( self.PageTitle , vbox)
		UtilsLabel.show_all()

		notebook.insert_page(vbox, UtilsLabel)
		window.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)

	def Install(self, widget):
		if OS == 'Lin' or OS == 'Mac':
			if not UtilDir in PATH:
				SystemLog('echo "PATH=%s:$PATH" >> %s' %(UtilDir, os.path.join(Home, ".profile")))
			if self.ImageBtn.get_active():
				if OS == 'Lin': SystemLog("sudo apt-get install imagemagick")
				elif OS == 'Mac':
					if not os.path.exists(os.path.join(ConfDir, "IM.tar.gz")):
						thread = StartThread(widget, urllib.urlretrieve, ('http://www.imagemagick.org/download/binaries/ImageMagick-x86_64-apple-darwin12.1.0.tar.gz', os.path.join(ConfDir, "IM.tar.gz"),), merge=False)
					ExZip(os.path.join(ConfDir, "IM.tar.gz"), Home, 'tar')
					if not os.path.join(Home, "ImageMagick-6.7.8", "bin") in PATH:
						HOME = os.environ['HOME']
						MAGICK_HOME=os.path.join(HOME, "ImageMagick-6.7.8")
						msg = "#\nMAGICK_HOME=%s\nPATH=%s/bin/:$PATH\nDYLD_LIBRARY_PATH=%s/lib/" %(MAGICK_HOME, MAGICK_HOME, MAGICK_HOME)
						SystemLog('echo "%s" >> %s' %(msg, os.path.join(Home, ".profile")))
			if self.PILBtn.get_active():
				SystemLog("sudo easy_install pip")
				SystemLog("sudo sh %s 1" % os.path.join(ScriptDir, "Source", "PIL.sh"))
			if self.JavaBtn.get_active():
				Web.open("http://www.oracle.com/technetwork/java/javase/downloads/index.html")
			if self.PyWin32Bt.get_active():
				urllib.urlretrieve("http://sourceforge.net/projects/pywin32/files/pywin32/Build%20217/pywin32-217.win32-py2.7.exe/download", os.path.join(ConfDir, "PyWin32.exe"))
				os.system("start %s" % os.path.join(ConfDir, "PyWin32.exe"))

		if OS == 'Win':
			if self.ImageBtn.get_active():
				urllib.urlretrieve("http://www.imagemagick.org/download/binaries/", os.path.join(ConfDir, "index.html"))
				ln = open(os.path.join(ConfDir, "index.html"), "r").readlines()[10]
				version = str(str(remove_tags(ln)).split('.exe')[0]).replace('Q8', 'Q16') + ".exe"
				wait = NewDialog(_("ImageMagick"), _("You will now download and run ImageMagick. Proceed the installation."))
				if os.path.exists(os.path.join(ConfDir, "IM.exe")):
					os.remove(os.path.join(ConfDir, "IM.exe"))
				urllib.urlretrieve("http://www.imagemagick.org/download/binaries/%s" % version, os.path.join(ConfDir, "IM.exe"))
				SystemLog("start %s" % os.path.join(ConfDir, "IM.exe"))
			if self.PILBtn.get_active():
				urllib.urlretrieve("https://www.dropbox.com/s/x7okd0u4e8uk5po/PIL-fork-1.1.7.win32-py2.7.exe", os.path.join(ConfDir, "PIL.exe"))
				SystemLog("start %s" % os.path.join(ConfDir, "PIL.exe"))
	
def ConvertImage():
	class ConvertFC(FileChooserD):pass
	def StartConvert(widget, ExtBtn):
		if ConvertDialog.out == None:
			NewDialog(_("ERROR"), _("Please select a directory first!"))
		else:
			if not os.path.exists(os.path.join(ImageDir, "Convert")): os.makedirs(os.path.join(ImageDir, "Convert"))
			ext = [r for r in ExtBtn.get_group() if r.get_active()][0].get_label()
			if Pil == True:
				for x in find_files(ConvertDialog.out, "*"):
					Dst = os.path.splitext(x.replace(ConvertDialog.out, os.path.join(ImageDir, "Convert")))[0] + ext
					if os.path.splitext(x)[1] in [".png", ".jpg", ".gif", ".bmp", ".jpeg"] and not os.path.splitext(x)[1] == ext.replace(".", ""):
						try:
							im = PILImage.open(x)
							im.load()
						except: pass
						else:
							png_info = im.info
							if not os.path.exists(os.path.dirname(Dst)): os.makedirs(os.path.dirname(Dst))
							if os.path.exists(Dst): os.remove(Dst)
							if ext == ".jpg" or ".jpeg": im = im.convert(im.mode.replace("A", ""))
							else: im.convert("RGBA")
							im.save(Dst, **png_info)

	vbox = gtk.VBox()
	notebook = MainApp.notebook

	ConvertLabel = NewPage( _("Convert Image") , vbox)
	ConvertLabel.show_all()


	locLabel = gtk.Label(" ")

	SelectBtn = gtk.Button(_("Open the directory with the images you want to convert") )
	ConvertImageDial = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                  	buttons=(gtk.STOCK_OPEN,gtk.RESPONSE_OK))

	ConvertDialog = ConvertFC()
	SelectBtn.connect("clicked", ConvertDialog.openFile, ConvertImageDial, [], False, locLabel.set_text)

	vbox.pack_start(SelectBtn, False)
	vbox.pack_start(locLabel, False, False, 15)

	ChooseLabel = gtk.Label(_("Choose the extension you want to convert the images to:"))
	vbox.pack_start(ChooseLabel, False, False, 0)

	ExtBtn = None
	for x in [".png", ".jpg", ".gif", ".bmp", ".jpeg"]:
		ExtBtn = gtk.RadioButton(ExtBtn, x)
		vbox.pack_start(ExtBtn, False, False, 0)

	StartBtn = gtk.Button("Convert to selected extension")
	StartBtn.connect("clicked", StartConvert, ExtBtn)
	vbox.pack_end(StartBtn, False, False, 0)

	notebook.insert_page(vbox, ConvertLabel)
	window.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)

class CopyFrom():
	class ToFC(FileChooserD):pass
	class FromFC(FileChooserD):pass
	ToDialog = ToFC()
	FromDialog = FromFC()

	def StartCopy(self, cmd, Conf="Std"):	
		if Conf == "Std":
			FromDir = self.FromDialog.out
			ToDir = self.ToDialog.out
			Ext = self.ExtBox.get_text()
		else: FromDir, ToDir, Ext = Conf
		print _("Copying files FROM " + FromDir + " to " + ToDir + " With extension " + Ext)
		for ToFile in find_files(ToDir, "*" + Ext):
			filename = ToFile.replace(ToDir, FromDir)
			if os.path.exists(filename):
				print _("Copying %s to %s" %(filename, ToFile))
				shutil.copy(filename, ToFile)

	def __init__(self):
		CopyFromWindow = window
		CopyFromLabel = gtk.Label( _("CopyFrom"))

		vbox = gtk.VBox()
		notebook = MainApp.notebook

		label = gtk.Label( _("""This tool copies files existing in a directory FROM an other directory.
				Can be handy for porting themes and such\n\nMake sure both directories have the same structure!\n\n\n""") )

		vbox.pack_start(label, False, False, 0)

		ToDirBtn = gtk.Button(_("Open the directory you want to copy the files TO") )
		ToDirDial = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
		                          	buttons=(gtk.STOCK_OPEN,gtk.RESPONSE_OK))

		ToDirBtn.connect("clicked", self.ToDialog.openFile, ToDirDial, [], False, ToDirBtn.set_label)
		vbox.pack_start(ToDirBtn, False, False, 0)

		FromDirBtn = gtk.Button(_("Open the directory you want to copy the files FROM") )
		FromDirDial = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
		                          	buttons=(gtk.STOCK_OPEN,gtk.RESPONSE_OK))

		FromDirBtn.connect("clicked", self.FromDialog.openFile, FromDirDial, [], False, FromDirBtn.set_label)
		vbox.pack_start(FromDirBtn, False, False, 0)

		hbox = gtk.HBox()

		self.ExtBox = gtk.Entry()
		self.ExtBox.set_size_request(80, 25)
		self.ExtBox.set_text(".")
		ExtLabel = gtk.Label( _("Enter the extension of the files you want to copy") )
		hbox.pack_start(self.ExtBox, False, False, 3)
		hbox.pack_start(ExtLabel, False, False, 45)

		vbox.pack_start(hbox, False, False, 0)

		StartButton = gtk.Button("CopyFrom!")
		StartButton.connect("clicked", self.StartCopy)

		vbox.pack_start(StartButton, False, False, 30)

		CopyFromLabel = NewPage( _("CopyFrom"), vbox )
		CopyFromLabel.show_all()
	
		notebook.insert_page(vbox, CopyFromLabel)
		CopyFromWindow.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)

class Resize:
	SrcDir = None
	class ResizeFC(FileChooserD):pass
	ResizeDialog = ResizeFC()
	def StartResize(self, widget):
			self.ResizeDialog.out
			DstDir = os.path.join(ImageDir, "Resized", '')
			if self.NormalResize.get_active():
				Perc = self.ResizePercentageBox.get_text()
				if not Perc.endswith("%"):
					Perc = Perc + "%"
			if self.EasyResize.get_active():
				InDPI = self.InDPIBox.get_text()
				OutDPI = self.OutDPIBox.get_text()
				if InDPI == 'XHDPI':
					InRes = 720
				elif InDPI == 'HDPI':
					InRes = 480
				elif InDPI == 'MDPI':
					InRes = 320
				elif InDPI == 'LDPI':
					InRes = 240
				else:
					InRes = int(InDPI)
				if OutDPI == 'XHDPI':
					OutRes = 720
				elif OutDPI == 'HDPI':
					OutRes = 480
				elif OutDPI == 'MDPI':
					OutRes = 320
				elif OutDPI == 'LDPI':
					OutRes = 240
				else:
					OutRes = int(OutDPI)

			if self.ApkResize.get_active():
				InDPI = self.ApkInDPIBox.get_text()
				OutDPI = self.ApkOutDPIBox.get_text()
				if InDPI == 'XHDPI':
					InRes = 720
					InDir1 = 'xhdpi'
				elif InDPI == 'HDPI':
					InRes = 480
					InDir1 = 'hdpi'
				elif InDPI == 'MDPI':
					InRes = 320
					InDir1 = 'mdpi'
				elif InDPI == 'LDPI':
					InRes = 240
					InDir1 = 'ldpi'
				else:
					InRes = int(InDPI)
					InDir1 = 'hdpi'
				if OutDPI == 'XHDPI':
					OutRes = 720
					OutDir1 = 'xhdpi'
				elif OutDPI == 'HDPI':
					OutRes = 480
					OutDir1 = 'hdpi'
				elif OutDPI == 'MDPI':
					OutRes = 320
					OutDir1 = 'mdpi'
				elif OutDPI == 'LDPI':
					OutRes = 240
					OutDir1 = 'ldpi'
				else:
					OutRes = int(OutDPI)
					OutDir1 = 'hdpi'
				FullZipDir = os.path.join(ScriptDir, "Resizing")
				if os.path.exists(FullZipDir):
					shutil.rmtree(FullZipDir)
				ExZip(self.ResizeDialog.out, FullZipDir)
				Apk = self.ResizeDialog.out
				self.ResizeFC.ResizeAPK = self.ResizeDialog.out
				self.ResizeDialog.out = os.path.join(ScriptDir, "Resizing", "res", "drawable-" + InDir1)
				DstDir = os.path.join(ScriptDir, "Resizing", "res", "drawable-" + OutDir1, '')

			if self.ApkResize.get_active() or self.EasyResize.get_active():
				Perc = round(OutRes * 100 / InRes, 2)

			print _("Resize percentage is %s" % str(Perc))
			if os.path.exists(DstDir):
				shutil.rmtree(DstDir)
			os.makedirs(DstDir)

			SrcDir = os.path.join(self.ResizeDialog.out, '')

			print("SrcDir = %s\nDstDir = %s" %(SrcDir, DstDir))

			for x in find_files(SrcDir, ".png"): print x
			for image in find_files(SrcDir, "*.png"):
				DstFile = image.replace(SrcDir, DstDir)
				Name = os.path.basename(image)
				Sub = image.replace(SrcDir, '')
				Sub = Sub.replace(Name, '')
				if not os.path.exists(os.path.join(DstDir, Sub)):
					os.makedirs(os.path.join(DstDir, Sub))
				print("%s -> %s" %(image, DstFile))
				if image.endswith("9.png"):
					print("%s has 9patch" % image)
					shutil.copy(image, DstFile)
					continue
				if r"%" in str(Perc):
					Perc = round(float(str(Perc).replace(r'%', '')), 2)
				pixbuf = gtk.gdk.pixbuf_new_from_file(image)
				w = pixbuf.get_width()
				h = pixbuf.get_height()
				if not w <= 1 and not h <= 1:
					w = int(int(Perc * w) / 100)
					h = int(int(Perc * h)  / 100)
					pixbuf = pixbuf.scale_simple(w,h,gtk.gdk.INTERP_HYPER)
				pixbuf.save(DstFile, os.path.splitext(image)[1].replace(".", ""))
			if self.ApkResize.get_active():
				FinDstDir = os.path.join(ImageDir, "Resized")
				if os.path.exists(FinDstDir):
					shutil.rmtree(FinDstDir)
				os.makedirs(FinDstDir)
				shutil.copy(self.ResizeFC.ResizeAPK, FinDstDir)
				DstApk = os.path.join(FinDstDir, os.path.basename(self.ResizeFC.ResizeAPK))
				zipf = zipfile.ZipFile(DstApk, "a")
				for file in os.listdir(DstDir):
					fullfile = os.path.join(DstDir, file)
					zipf.write(fullfile, os.path.join("res", "drawable-%s" % OutDir1, file))
				zipf.close()
				shutil.copy(DstApk, os.path.join(ScriptDir, "APK", "IN", "Unsigned-%s-%s.apk" %(os.path.basename(DstApk).replace(".apk", ""),OutDir1)))
				callback(widget, "Sign")
			else:
				if os.path.exists(os.path.join(ScriptDir, "Resizing")) and not ToolAttr.Debug == True:
					shutil.rmtree(os.path.join(ScriptDir, "Resizing"))
				NewDialog( _("Resized") , _("You can find the resized images in %s" % os.path.join(os.path.basename(ImageDir), "Resized")) )
		
	def __init__(self):
		ResizeWindow = window
		ResizeLabel = gtk.Label("Resize")
		vbox = gtk.VBox()
		sw = gtk.ScrolledWindow()
		notebook = MainApp.notebook

		self.NormalResize = gtk.RadioButton(None, "Normal resizing using resize percentage")
		vbox.pack_start(self.NormalResize, False, False, 2)

		NormalResizeTable = gtk.Table(2, 2, True)
		NormalResizeTable.set_col_spacings(2)
		NormalResizeTable.set_row_spacings(2)

		self.ResizePercentageBox = gtk.Entry()
		self.ResizePercentageBox.set_text("%")
		self.ResizePercentageBox.set_size_request(0, 30)

		ResizePercentageLabel = gtk.Label( _("Enter the resize percentage 0-100 %") )

		ResizeDirDial = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
		                          	buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		ResizeDirBtn = gtk.Button("Select the directory")

		ResizeDirLabel = gtk.Label( _("Choose the directory containing the images"))
		ResizeDirBtn.connect("clicked", self.ResizeDialog.openFile, ResizeDirDial, [], False, False)

		NormalResizeTable.attach(self.ResizePercentageBox, 0, 1, 0, 1, xpadding=20)
		NormalResizeTable.attach(ResizePercentageLabel, 1, 2, 0, 1)
		NormalResizeTable.attach(ResizeDirBtn, 0, 1, 1, 2, xpadding=20)
		NormalResizeTable.attach(ResizeDirLabel, 1, 2, 1, 2)
		vbox.pack_start(NormalResizeTable, False, False, 0)

		self.EasyResize = gtk.RadioButton(self.NormalResize, _("Easy resizing using ..DPI values"))
		vbox.pack_start(self.EasyResize, False, False, 2)

		EasyResizeTable = gtk.Table(2, 2, True)
	
		self.InDPIBox = gtk.Entry()
		self.InDPIBox.set_text("..DPI")
		EasyResizeTable.attach(self.InDPIBox, 0, 1, 0, 1, xpadding=20)
		InDPILabel = gtk.Label( _("Give the DPI of the images"))
		EasyResizeTable.attach(InDPILabel, 1, 2, 0, 1)

		self.OutDPIBox = gtk.Entry()
		self.OutDPIBox.set_text("..DPI")
		EasyResizeTable.attach(self.OutDPIBox, 0, 1, 1, 2, xpadding=20)
		OutDPILabel = gtk.Label( _("Give the Resized DPI"))
		EasyResizeTable.attach(OutDPILabel, 1, 2, 1, 2)

		EasyResizeDirDial = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
		                          	buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		EasyResizeDirBtn = gtk.Button("Select the directory")

		EasyResizeTable.attach(EasyResizeDirBtn, 0, 1, 2, 3, xpadding=20)
		ResizeDirLabel = gtk.Label(_("Choose the directory containing the images"))
		EasyResizeDirBtn.connect("clicked", self.ResizeDialog.openFile, ResizeDirDial, [], False, False)
		EasyResizeTable.attach(ResizeDirLabel, 1, 2, 2, 3)

		vbox.pack_start(EasyResizeTable, False, False, 0)

		self.ApkResize = gtk.RadioButton(self.NormalResize, _("Resize an APK using DPI values"))
		vbox.pack_start(self.ApkResize, False, False, 10)

		APKResizeTable = gtk.Table(3, 2, True)
	
		self.ApkInDPIBox = gtk.Entry()
		self.ApkInDPIBox.set_text("..DPI")
		APKResizeTable.attach(self.ApkInDPIBox, 0, 1, 0, 1, xpadding=20)
		ApkInDPILabel = gtk.Label(_("Give the DPI of the images"))
		APKResizeTable.attach(ApkInDPILabel, 1, 2, 0, 1)

		self.ApkOutDPIBox = gtk.Entry()
		self.ApkOutDPIBox.set_text("..DPI")
		APKResizeTable.attach(self.ApkOutDPIBox, 0, 1, 1, 2, xpadding=20)
		ApkOutDPILabel = gtk.Label("Give the Resized DPI")
		APKResizeTable.attach(ApkOutDPILabel, 1, 2, 1, 2)

		ApkResizeDirBox = gtk.Entry()
		ApkResizeDirBox.set_text(os.path.join(ScriptDir, ''))
		ApkResizeDirBox.set_size_request(0, 30)
	
		ApkResizeApk = gtk.FileChooserDialog("Open..",  None, gtk.FILE_CHOOSER_ACTION_OPEN, 
						(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		ApkResizeBtn = gtk.Button(_("Choose the APK"))
		APKResizeTable.attach(ApkResizeBtn, 0, 1, 2, 3, xpadding=20)
		ApkResizeBtn.connect("clicked", self.ResizeDialog.openFile, ApkResizeApk, [".apk"], False, False)

		ResizeDirLabel = gtk.Label(_("Choose the APK"))
		APKResizeTable.attach(ResizeDirLabel, 1, 2, 2, 3)

		vbox.pack_start(APKResizeTable, False, False, 0)

		ResizeStartButton = gtk.Button(_("Start resizing"))
		ResizeStartButton.connect("clicked", self.StartResize)
		vbox.pack_end(ResizeStartButton, False, False, 15)

		ResizeLabel = NewPage("Resize", vbox)
		ResizeLabel.show_all()

		notebook.insert_page(vbox, ResizeLabel)
		ResizeWindow.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)

class Theme:
	SrcDir =  os.path.join(ScriptDir, "Image", "Theme")
	msg = _("Place the images you want to theme inside %s" % SrcDir)
		

	# (C) MARTINEAU @ StackOverflow
	def image_tint(self, im, tint="#33b5e5"):
		if isinstance(im, str):  # file path?
			src = PILImage.open(im)
		else: src = im
		if src.mode == "P": src = pallette_convert(im)
		if src.mode not in ['RGB', 'RGBA']:
			print _("Converting %s to RGBA" % src.mode)
			src = src.convert("RGBA")
		src.load()

		tr, tg, tb = PILImageColor.getrgb(tint)
		tl = PILImageColor.getcolor(tint, "L")  # tint color's overall luminosity
		if not tl: tl = 1  # avoid division by zero
		tl = float(tl)  # compute luminosity preserving tint factors
		sr, sg, sb = map(lambda tv: tv/tl, (tr, tg, tb))  # per component adjustments

		# create look-up tables to map luminosity to adjusted tint
		# (using floating-point math only to compute table)
		luts = (map(lambda lr: int(lr*sr + 0.5), range(256)) +
		    map(lambda lg: int(lg*sg + 0.5), range(256)) +
		    map(lambda lb: int(lb*sb + 0.5), range(256)))
		l = PILImageOps.grayscale(src)  # 8-bit luminosity version of whole image
		if PILImage.getmodebands(src.mode) < 4:
			merge_args = (src.mode, (l, l, l))  # for RGB verion of grayscale
		else:  # include copy of src image's alpha layer
			a = PILImage.new("L", src.size)
			a.putdata(src.getdata(3))
			merge_args = (src.mode, (l, l, l, a))  # for RGBA verion of grayscale
			luts += range(256)  # for 1:1 mapping of copied alpha values

		return PILImage.merge(*merge_args).point(luts)
	def ParseColor(self):
		CurCol = str(self.colorsel.get_current_color())
		ColCode = CurCol.replace("#", '')
		PerLen = int(len(ColCode) / 3)
		hexc = []
		for x in ColCode: hexc.append(x)
		Red = int(''.join(hexc[0:PerLen]), 16)
		Green = int(''.join(hexc[PerLen:PerLen*2]), 16)
		Blue = int(''.join(hexc[PerLen*2:]), 16)


		Red = int(Red * 255 / int(''.join(['f', 'f', 'f', 'f'][0:PerLen]), 16))
		Green = int(Green * 255 / int(''.join(['f', 'f', 'f', 'f'][0:PerLen]), 16))
		Blue = int(Blue * 255 / int(''.join(['f', 'f', 'f', 'f'][0:PerLen]), 16))

		Clr = RGBToHTMLColor((Red, Green, Blue))
		return Clr	
	def StartTheming(self, widget):
		Clr = self.ParseColor()
		if not os.path.exists(self.SrcDir):
			os.makedirs(self.SrcDir)
		print(Clr)
		for image in find_files(self.SrcDir, "*.png"):
			Image1 = str(image)
			if Pil == True:
				img = self.image_tint(Image1, Clr)
				img.save("%s" % Image1)
			else:
				SystemLog('convert %s -colorspace gray %s' %(Image1, Image1) )
				SystemLog('mogrify -fill "%s" -tint 100 %s' %(Clr, Image1))
		self.EndTheming()

	def EndTheming(self):
		NewDialog("Themed", "You can find the themed images inside Theme")

	def __init__(self):
		ThemeWindow = window
		ThemeLabel = gtk.Label(self.msg)
		notebook = MainApp.notebook

		self.colorsel = gtk.ColorSelection()
		self.colorsel.set_current_color(gtk.gdk.Color("#33b5e5"))

		if not os.path.exists(self.SrcDir):
			os.makedirs(self.SrcDir)

		vbox = gtk.VBox()
		vbox.pack_start(ThemeLabel, False, False, 10)

		vbox.pack_start(self.colorsel, False, False, 0)

		StartButton = gtk.Button( _("Start theming!") )
		StartButton.connect("clicked", self.StartTheming)
		vbox.pack_start(StartButton, False, False, 15)

		ThemeLabel = NewPage("Theme", vbox)
		ThemeLabel.show_all()

		notebook.insert_page(vbox, ThemeLabel)

		ThemeWindow.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)

class Rename:
	class FileChooserRename(FileChooserD):pass
	RenameDialog = FileChooserRename()

	def __init__(self):
		notebook = MainApp.notebook
		vbox = gtk.VBox()
		RenameLabel = NewPage("Rename", vbox)

		label = gtk.Label(_("This tool is used to batch-rename files found in a directory\nusing a pattern to find them"))
		label.set_justify(gtk.JUSTIFY_CENTER)
		vbox.pack_start(label, False, False, 10)

		RenameDirBtn = gtk.Button(_("Open the directory in wich you want to rename files") )
		RenameDirDial = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
		                          	buttons=(gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		RenameDirBtn.connect("clicked", self.RenameDialog.openFile, RenameDirDial, [], False, RenameDirBtn.set_label)
		vbox.pack_start(RenameDirBtn, False, False)

		hbox = gtk.HBox()
		self.Pattern = gtk.Entry()
		self.Pattern.set_text("*")
		label = gtk.Label("Enter a pattern (e.g. '*.xml' or 'btn*.png') to find files with")
		hbox.pack_start(self.Pattern, False, True, 10)
		hbox.pack_start(label)

		vbox.pack_start(hbox)

		hbox2 = gtk.HBox()

		self.AddFront = gtk.Entry()
		self.AddFront.set_text("[Add to beginning]")
		self.AddFront.connect("changed", self.UpdateLabel)
		self.AddBack = gtk.Entry()
		self.AddBack.set_text("[Add to the end]")
		self.AddBack.connect("changed", self.UpdateLabel)
		self.AddExt = gtk.Entry()
		self.AddExt.set_text("[Add to ext]")
		self.AddExt.connect("changed", self.UpdateLabel)
		self.FileName = gtk.Label("[FILENAME]")
		for widg in [self.AddFront, self.FileName, self.AddBack, self.AddExt]: hbox2.pack_start(widg)
		vbox.pack_start(hbox2)

		self.reviewLabel = gtk.Label("btn_checked.png")
		vbox.pack_start(self.reviewLabel)

		hbox = gtk.HBox()

		startBtn = gtk.Button(_("Rename"))
		startBtn.connect("clicked", self.StartRename)
		hbox.pack_start(startBtn)
		ReverseBtn = gtk.Button(_("Undo Rename"))
		ReverseBtn.connect("clicked", self.UndoName)
		hbox.pack_start(ReverseBtn)
	
		vbox.pack_start(hbox, False, False)


		notebook.insert_page(vbox, RenameLabel)
		window.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)

	def UpdateLabel(self, widget):
		fr = self.AddFront.get_text()
		ba = self.AddBack.get_text()
		ex = self.AddExt.get_text()
		text = "btn_checked.png"
		if not fr.startswith("[") and not fr.endswith("]"):text = fr + text
		if not ba.startswith("[") and not ba.endswith("]"):text = str(ba + ".").join(text.split("."))
		if not ex.startswith("[") and not ex.endswith("]"):text = text + ex
		self.reviewLabel.set_text("btn_checked.png  -->>  %s" % text.replace(' ', ''))
		self.reviewLabel.show()

	def StartRename(self, widget):
		searchDirectory = self.RenameDialog.out
		pattern = self.Pattern.get_text()
		i = 0
		for file in find_files(searchDirectory, pattern):
			fr = self.AddFront.get_text()
			ba = self.AddBack.get_text()
			ex = self.AddExt.get_text()
			originalFile = os.path.basename(file)
			fileName = originalFile
			if not fr.startswith("[") and not fr.endswith("]"):fileName = fr + fileName
			if not ba.startswith("[") and not ba.endswith("]"):fileName = str(ba + ".").join(fileName.split("."))
			if not ex.startswith("[") and not ex.endswith("]"):fileName = fileName + ex
			fullRenamed = os.path.join(os.path.dirname(file), fileName)
			os.rename(file, fullRenamed)
			if not originalFile == fileName:
				i = i+1
		NewDialog(_("Rename"), _("Renamed %d files" % i))

	def UndoName(self, widget):
		searchDirectory = self.RenameDialog.out
		pattern = self.Pattern.get_text()
		fr = self.AddFront.get_text()
		ba = self.AddBack.get_text()
		ex = self.AddExt.get_text()
		i = 0
		for file in find_files(searchDirectory, pattern):
			originalFile = os.path.basename(file)
			fileName = originalFile
			if not fr.startswith("[") and not fr.endswith("]") and not fr == '':fileName = ''.join(fileName.split(fr)[1:])
			if not ba.startswith("[") and not ba.endswith("]") and not ba == '':fileName = ''.join(os.path.splitext(fileName)[0].rsplit(ba)[:-1]) + os.path.splitext(fileName)[1]
			if not ex.startswith("[") and not ex.endswith("]") and not ex == '':fileName = os.path.splitext(fileName)[0] + ''.join(os.path.splitext(fileName)[1].rsplit(ex)[:-1])
			fullRenamed = os.path.join(os.path.dirname(file), fileName)
			if not originalFile == fileName:
				os.rename(file, fullRenamed)
				i = i+1

		NewDialog(_("Undo Rename"), _("Un-named %d files" % i))	
	

def PrepareBuilding():
	def Prepare(cmd):
		NewDialog("Info", _("Please check the terminal for further progress."))
		SystemLog("""sudo add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update &
sudo apt-get upgrade &
sudo apt-get install python2.5 &
sudo add-apt-repository "deb http://archive.canonical.com/ lucid partner"
sudo add-apt-repository "deb-src http://archive.canonical.com/ubuntu lucid partner"
sudo apt-get update &
sudo apt-get install sun-java6-jdk &
sudo apt-get update &
sudo apt-get upgrade &
sudo apt-get install git-core &
sudo apt-get install valgrind &
sudo apt-get install git-core gnupg flex bison gperf build-essential \
zip curl zlib1g-dev libc6-dev lib64ncurses5-dev \
x11proto-core-dev libx11-dev lib64readline-gplv2-dev lib64z1-dev \
libgl1-mesa-dev g++-multilib tofrodos &
mkdir -p ~/bin
mkdir -p ~/android/system
curl https://dl-ssl.google.com/dl/googlesource/git-repo/repo > ~/bin/repo
chmod a+x ~/bin/repo
sudo echo '#Acer
SUBSYSTEM==usb, SYSFS{idVendor}==0502, MODE=0666

#ASUS
SUBSYSTEM==usb, SYSFS{idVendor}==0b05, MODE=0666

#Dell
SUBSYSTEM==usb, SYSFS{idVendor}==413c, MODE=0666

#Foxconn
SUBSYSTEM==usb, SYSFS{idVendor}==0489, MODE=0666

#Garmin-Asus
SUBSYSTEM==usb, SYSFS{idVendor}==091E, MODE=0666

#Google
SUBSYSTEM==usb, SYSFS{idVendor}==18d1, MODE=0666

#HTC
SUBSYSTEM=="usb", SYSFS{idVendor}=="0bb4", MODE="0666"

#Huawei
SUBSYSTEM==usb, SYSFS{idVendor}==12d1, MODE=0666

#K-Touch
SUBSYSTEM==usb, SYSFS{idVendor}==24e3, MODE=0666

#KT Tech
SUBSYSTEM==usb, SYSFS{idVendor}==2116, MODE=0666

#Kyocera
SUBSYSTEM==usb, SYSFS{idVendor}==0482, MODE=0666

#Lenevo
SUBSYSTEM==usb, SYSFS{idVendor}==17EF, MODE=0666

#LG
SUBSYSTEM==usb, SYSFS{idVendor}==1004, MODE=0666

#Motorola
SUBSYSTEM==usb, SYSFS{idVendor}==22b8, MODE=0666

#NEC
SUBSYSTEM==usb, SYSFS{idVendor}==0409, MODE=0666

#Nook
SUBSYSTEM==usb, SYSFS{idVendor}==2080, MODE=0666

#Nvidia
SUBSYSTEM==usb, SYSFS{idVendor}==0955, MODE=0666

#OTGV
SUBSYSTEM==usb, SYSFS{idVendor}==2257, MODE=0666

#Pantech
SUBSYSTEM==usb, SYSFS{idVendor}==10A9, MODE=0666

#Philips
SUBSYSTEM==usb, SYSFS{idVendor}==0471, MODE=0666

#PMC-Sierra
SUBSYSTEM==usb, SYSFS{idVendor}==04da, MODE=0666

#Qualcomm
SUBSYSTEM==usb, SYSFS{idVendor}==05c6, MODE=0666

#SK Telesys
SUBSYSTEM==usb, SYSFS{idVendor}==1f53, MODE=0666

#Samsung
SUBSYSTEM==usb, SYSFS{idVendor}==04e8, MODE=0666

#Sharp
SUBSYSTEM==usb, SYSFS{idVendor}==04dd, MODE=0666

#Sony Ericsson
SUBSYSTEM==usb, SYSFS{idVendor}==0fce, MODE=0666

#Toshiba
SUBSYSTEM==usb, SYSFS{idVendor}==0930, MODE=0666

#ZTE
SUBSYSTEM==usb, SYSFS{idVendor}==19D2, MODE=0666' > /etc/udev/rules.d/51-android.rules
sudo chmod a+r /etc/udev/rules.d/51-android.rules

echo '-----BEGIN PGP PUBLIC KEY BLOCK-----
    Version: GnuPG v1.4.2.2 (GNU/Linux)  
    mQGiBEnnWD4RBACt9/h4v9xnnGDou13y3dvOx6/t43LPPIxeJ8eX9WB+8LLuROSV
    lFhpHawsVAcFlmi7f7jdSRF+OvtZL9ShPKdLfwBJMNkU66/TZmPewS4m782ndtw7
    8tR1cXb197Ob8kOfQB3A9yk2XZ4ei4ZC3i6wVdqHLRxABdncwu5hOF9KXwCgkxMD
    u4PVgChaAJzTYJ1EG+UYBIUEAJmfearb0qRAN7dEoff0FeXsEaUA6U90sEoVks0Z
    wNj96SA8BL+a1OoEUUfpMhiHyLuQSftxisJxTh+2QclzDviDyaTrkANjdYY7p2cq
    /HMdOY7LJlHaqtXmZxXjjtw5Uc2QG8UY8aziU3IE9nTjSwCXeJnuyvoizl9/I1S5
    jU5SA/9WwIps4SC84ielIXiGWEqq6i6/sk4I9q1YemZF2XVVKnmI1F4iCMtNKsR4
    MGSa1gA8s4iQbsKNWPgp7M3a51JCVCu6l/8zTpA+uUGapw4tWCp4o0dpIvDPBEa9
    b/aF/ygcR8mh5hgUfpF9IpXdknOsbKCvM9lSSfRciETykZc4wrRCVGhlIEFuZHJv
    aWQgT3BlbiBTb3VyY2UgUHJvamVjdCA8aW5pdGlhbC1jb250cmlidXRpb25AYW5k
    cm9pZC5jb20+iGAEExECACAFAknnWD4CGwMGCwkIBwMCBBUCCAMEFgIDAQIeAQIX
    gAAKCRDorT+BmrEOeNr+AJ42Xy6tEW7r3KzrJxnRX8mij9z8tgCdFfQYiHpYngkI
    2t09Ed+9Bm4gmEO5Ag0ESedYRBAIAKVW1JcMBWvV/0Bo9WiByJ9WJ5swMN36/vAl
    QN4mWRhfzDOk/Rosdb0csAO/l8Kz0gKQPOfObtyYjvI8JMC3rmi+LIvSUT9806Up
    hisyEmmHv6U8gUb/xHLIanXGxwhYzjgeuAXVCsv+EvoPIHbY4L/KvP5x+oCJIDbk
    C2b1TvVk9PryzmE4BPIQL/NtgR1oLWm/uWR9zRUFtBnE411aMAN3qnAHBBMZzKMX
    LWBGWE0znfRrnczI5p49i2YZJAjyX1P2WzmScK49CV82dzLo71MnrF6fj+Udtb5+
    OgTg7Cow+8PRaTkJEW5Y2JIZpnRUq0CYxAmHYX79EMKHDSThf/8AAwUIAJPWsB/M
    pK+KMs/s3r6nJrnYLTfdZhtmQXimpoDMJg1zxmL8UfNUKiQZ6esoAWtDgpqt7Y7s
    KZ8laHRARonte394hidZzM5nb6hQvpPjt2OlPRsyqVxw4c/KsjADtAuKW9/d8phb
    N8bTyOJo856qg4oOEzKG9eeF7oaZTYBy33BTL0408sEBxiMior6b8LrZrAhkqDjA
    vUXRwm/fFKgpsOysxC6xi553CxBUCH2omNV6Ka1LNMwzSp9ILz8jEGqmUtkBszwo
    G1S8fXgE0Lq3cdDM/GJ4QXP/p6LiwNF99faDMTV3+2SAOGvytOX6KjKVzKOSsfJQ
    hN0DlsIw8hqJc0WISQQYEQIACQUCSedYRAIbDAAKCRDorT+BmrEOeCUOAJ9qmR0l
    EXzeoxcdoafxqf6gZlJZlACgkWF7wi2YLW3Oa+jv2QSTlrx4KLM=
    =Wi5D 
    -----END PGP PUBLIC KEY BLOCK-----' > ~/gpgimport
gpg --import ~/gpgimport
rm ~/gpgimport""")
		SystemLog("""sudo apt-get install git-core gnupg flex bison gperf build-essential \
zip curl zlib1g-dev libc6-dev tofrodos python-markdown \
libxml2-utils xsltproc x11proto-core-dev libgl1-mesa-dev libx11-dev""")
		if Button64.get_active():
			SystemLog("""sudo apt-get install lib32ncurses5-dev ia32-libs lib32readline5-dev lib32z-dev g++-multilib mingw32""")
		if Button32.get_active():
			SystemLog("sudo apt-get install libncurses5-dev libreadline6-dev")
		if Button1010.get_active():
			SystemLog("sudo ln -s /usr/lib32/mesa/libGL.so.1 /usr/lib32/mesa/libGL.so")
		if Button1110.get_active():
			SystemLog("sudo apt-get install libx11-dev:i386")
		if Button1204.get_active():
			SystemLog("""sudo apt-get install libncurses5-dev:i386 libx11-dev:i386 libreadline6-dev:i386 libgl1-mesa-dev:i386 \
g++-multilib mingw32 openjdk-6-jdk tofrodos libxml2-utils xsltproc zlib1g-dev:i386""")
		KillPage("cmd", box)

	PrepareWindow = window
	notebook = MainApp.notebook

	box = gtk.VBox()

	

	label=gtk.Label( _("You need this option before you can build.\nPlease select your OS..."))
	box.pack_start(label, False, False, 10)

	Button1004 = gtk.RadioButton(None, "Ubuntu 10.04")
	box.pack_start(Button1004, False, False, 10)
	Button1010 = gtk.RadioButton(Button1004, "Ubuntu 10.10")
	box.pack_start(Button1010, False, False, 10)
	Button1110 = gtk.RadioButton(Button1004, "Ubuntu 11.10")
	box.pack_start(Button1110, False, False, 10)
	Button1204 = gtk.RadioButton(Button1004, "Ubuntu 12.04")
	box.pack_start(Button1204, False, False, 10)
	separator = gtk.HSeparator()
	box.pack_start(separator, False, True, 0)
	Button32 = gtk.RadioButton(None, "32-bits")
	box.pack_start(Button32, False, False, 10)
	Button64 = gtk.RadioButton(Button32, "64-bits")	
	Button64.set_active(True)
	def SetButton64(cmd):
		Button64.set_active(True)
	Button1204.connect("toggled", SetButton64)
	if (sys.maxsize > 2**32) == True:
		Button64.set_active(True)
	if platform.dist()[1] == 12.04: Button1204.set_active(True)
	elif platform.dist()[1] == 11.10: Button1110.set_active(True)
	elif platform.dist()[1] == 10.10: Button1010.set_active(True)
	elif platform.dist()[1] == 10.04: Button1004.set_active(True)
	box.pack_start(Button64, False, False, 10)
	ButtonPrepare = gtk.Button("Prepare to Build")
	ButtonPrepare.connect("clicked", Prepare)
	box.pack_start(ButtonPrepare, False, False, 20)
	PrepareLabel = NewPage("Prepare", box)
	PrepareLabel.show_all()
	notebook.insert_page(box, PrepareLabel)
	PrepareWindow.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)

def SDK():
	print _("Retrieving SDK")
	if OS == 'Win':
		urllib.urlretrieve('http://dl.google.com/android/installer_r20.0.3-windows.exe', os.path.join(Home, 'SDK.exe'))
		SystemLog("start %s" % os.path.join(Home, 'SDK.exe'))
	else:
		if OS == 'Mac':
			urllib.urlretrieve('http://dl.google.com/android/android-sdk_r20.0.1-macosx.zip', os.path.join(Home, 'SDK.zip'))
			print _("Extracting SDK")
			ExZip(os.path.join(Home, 'SDK.zip'), Home)
		elif OS == 'Lin':
			urllib.urlretrieve('http://dl.google.com/android/android-sdk_r20.0.1-linux.tgz', os.path.join(Home, 'SDK.tgz'))
			print _("Extracting SDK")
			tar = tarfile.open(os.path.join(Home, "SDK.tgz"))
			tar.extractall(path=Home)
		for x in os.listdir(Home): 
			if "android-sdk-" in x: sdkdir = os.path.join(Home, x)
		print _("Setting permissions")
		for file in find_files(sdkdir, "*"):
			if not os.path.isdir(file):
				os.chmod(file, 0755)
		os.chdir(os.path.join(sdkdir, "tools"))
		SystemLog(os.path.join(".", "android") + " &")



def JDK():
	if OS == 'Lin':
		SystemLog('gksudo "apt-get -y install openjdk-7-jdk"')
	else:
		Web.open('http://www.oracle.com/technetwork/java/javase/downloads/jdk-7u4-downloads-1591156.html')

def Eclipse():
	if OS == "Lin": 
		if bit == 32:Web.open('http://www.eclipse.org/downloads/download.php?file=/eclipse/downloads/drops4/R-4.2-201206081400/eclipse-SDK-4.2-linux-gtk.tar.gz')
		elif bit == 64:Web.open('http://www.eclipse.org/downloads/download.php?file=/eclipse/downloads/drops4/R-4.2-201206081400/eclipse-SDK-4.2-linux-gtk-x86_64.tar.gz')
	elif OS == "Win": 
		if bit == 64:Web.open("http://www.eclipse.org/downloads/download.php?file=/eclipse/downloads/drops4/R-4.2-201206081400/eclipse-SDK-4.2-win32-x86_64.zip")
		elif bit == 32: Web.open("http://www.eclipse.org/downloads/download.php?file=/eclipse/downloads/drops4/R-4.2-201206081400/eclipse-SDK-4.2-win32.zip")

class BuildSource:
	class WorkingFolderFC(FileChooserD):pass
	WorkingFolderDialog = WorkingFolderFC()

	build_switches = ' '
	sync_switches = ' '
	def __init__(self):
		self.notebook = MainApp.notebook	
		vbox = gtk.VBox()
		sw = gtk.ScrolledWindow()

		if os.path.exists(os.path.join(ConfDir, "Device")):
			Text = open(os.path.join(ConfDir, "Device"), "r")
			Text = Text.readline()
			Device = str(Text.replace('.py', '')).replace('\n', '')
		else:	Device = "SourceStock"

		self.Sources, self.URL = Source.Src.MakeVal(Device)

		hbox = gtk.HBox()

		label = gtk.Label( _("Choose the OS you want to build:"))
		vbox.pack_start(label, False, False, 10)


		self.deviceVbox = gtk.VBox()
		vbox.pack_start(self.deviceVbox, False, False, 0)

		self.SetPage()

		hbox = gtk.HBox(False)
		vbox1 = gtk.VBox()
		hbox.pack_start(vbox1)
		vbox5 = gtk.VBox()
		hbox.pack_start(vbox5)

		SyncButton = gtk.Button(_("Sync"))
		SyncButton.connect("clicked", StartThread, self.StartSync)
		vbox1.pack_start(SyncButton, False, False, 0)

		Force = gtk.CheckButton( _("Force sync"))
		Force.connect("clicked", self.set_sync_switch, "-f ")
		vbox1.pack_start(Force, False, False, 0)

		Quiet = gtk.CheckButton( _("Be quiet!"))
		Quiet.connect("clicked", self.set_sync_switch, "-q ")
		vbox1.pack_start(Quiet, False, False, 0)

		Local = gtk.CheckButton( _("Sync local only"))
		Local.connect("clicked", self.set_sync_switch, "-l ")
		vbox1.pack_start(Local, False, False, 0)

		Jobs = gtk.CheckButton(_("Custom number of parallel jobs: %s" % Cores ))
		Jobs.connect("clicked", self.set_sync_switch, "-j%s " % Cores)
		vbox1.pack_start(Jobs, False, False, 0)

		SkipButton = gtk.Button( _("Build (Only when synced)"))
		SkipButton.connect("clicked", self.StartBuild)
		vbox5.pack_start(SkipButton, False, False, 0)

		Force2 = gtk.CheckButton( _("Force build"))
		Force2.connect("clicked", self.set_build_switch, "-f ")
		vbox5.pack_start(Force2, False, False, 0)

		Quiet2 = gtk.CheckButton( _("Be quiet!"))
		Quiet2.connect("clicked", self.set_build_switch, "-q ")
		vbox5.pack_start(Quiet2, False, False, 0)

		Jobs2 = gtk.CheckButton(_("Custom number of parallel jobs: %s" % Cores ))
		Jobs2.connect("clicked", self.set_build_switch, "-j%s " % Cores)
		vbox5.pack_start(Jobs2, False, False, 0)

		vbox.pack_end(hbox, False, False, 10)


		BuildLabel = NewPage(_("Build from Source"), vbox)
		BuildLabel.show_all()

		sw.add_with_viewport(vbox)

		self.notebook.insert_page(sw, BuildLabel)
		window.show_all()
		self.notebook.set_current_page(self.notebook.get_n_pages() - 1)

		if MainApp.DevelopMenu ==  False:
			SourceMenu = gtk.MenuItem(_("Development"))
			menu.append(SourceMenu)
			DevelopmentMenu = gtk.Menu()
			SourceMenu.set_submenu(DevelopmentMenu)

			DeviceOption = gtk.MenuItem(_("Device"))
			DeviceMenu = gtk.Menu()
			DevelopmentMenu.append(DeviceOption)
			DeviceOption.set_submenu(DeviceMenu)

			SourceDirOption = gtk.MenuItem(_("Set Working Folder"))
			SourceDirOption.connect("activate", self.SetWorkingDir)
			DevelopmentMenu.append(SourceDirOption)

			for SourceFile in find_files(os.path.join(ScriptDir, "Source"), "Source*.py"):
				SourceFile = os.path.basename(SourceFile)
				Name = str(SourceFile.replace("Source", '')).replace('.py', '')
				MenuItem = gtk.MenuItem(Name)
				DeviceMenu.append(MenuItem)
				MenuItem.connect("activate", self.NewSources, SourceFile)
				MenuItem.show()
			menu.show_all()
			MainApp.DevelopMenu = True

		if not os.path.exists(os.path.join(ConfDir, "Device")):
			NewDialog(_("Device"), _("You can choose the device you want to build for in the top bar."))

	def set_sync_switch(self, widget, switch):
		if widget.get_active(): self.sync_switches += switch
		else: self.sync_switches = self.sync_switches.replace(switch, '')
	def set_build_switch(self, widget, switch):
		if widget.get_active(): self.build_switches += switch
		else: self.build_switches = self.build_switches.replace(switch, '')

	def SetPage(self):
		hbox = gtk.HBox(True)
		vbox1 = gtk.VBox()
		vbox2 = gtk.VBox()
		vbox3 = gtk.VBox()
		hbox.pack_start(vbox1)
		hbox.pack_start(vbox2)
		hbox.pack_start(vbox3)
		self.deviceVbox.pack_start(hbox, False, False, 0)
		Number = len(self.Sources)
		NameBtn = None
		for num in range(0, Number):
			Name = self.Sources[num]
			if Name == 'divide':
				vbox3.pack_start(gtk.HSeparator(), False)
			else:
				NameBtn = gtk.RadioButton(NameBtn, Name)
				NameBtn.connect("toggled", self.SetURL, num)
				NameBtn.get_group()[-1].set_active(True)
				if range(0, Number)[num] < (Number /  3): vbox1.pack_start(NameBtn, False, False, 0)
				elif Number / 3 <= range(0, Number)[num] < (Number /  3) * 2: vbox2.pack_start(NameBtn, False, False, 0)
				elif range(0, Number)[num] > Number /  3: vbox3.pack_start(NameBtn, False, False, 0)
				else: print num
		self.SetURL(NameBtn.get_group()[-1], 0)
		window.show_all()

	def SetWorkingDir(self, widget):
		WorkingDial = gtk.FileChooserDialog(title=_("Select your working folder"),action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
					  	buttons=(gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		self.SourceDir = self.WorkingFolderDialog.openFile(widget, WorkingDial, [], False, False)
		self.repocmd = ''
		print _("Working folder set to %s" % self.SourceDir)

	def StartSync(self, widget):
		if not os.path.exists(self.SourceDir):
			os.makedirs(self.SourceDir)
		os.chdir(self.SourceDir)
		with open(os.path.join(ScriptDir, "Source", "repocmd"), "w") as f:
			f.write(self.repocmd)
		with open(os.path.join(ScriptDir, "Source", "syncswitches"), "w") as f:
			f.write(self.sync_switches)
		if self.repocmd == '': init = "done"
		else: init = "init"
		BuildScript = os.path.join(ScriptDir, "Source", "Build.sh")
		os.system(BuildScript + ' sync' + init)
		self.StartBuild(widget)

	def StartBuild(self, widget):
		if not os.path.exists(os.path.join(self.SourceDir, ".repo")):
			NewDialog("ERROR", _(SourceDir + " does not exist!\nPress SYNC instead."))
		else:
			self.notebook.remove_page(self.notebook.get_n_pages() -1)
			sw = gtk.ScrolledWindow()
			BuildLabel = NewPage("Build", sw)
			BuildLabel.show_all()
			vbox = gtk.VBox()
			NameBtn = None

			for devi in find_files(os.path.join(SourceDir, "device"), "vendorsetup.sh"):
				for line in open(devi).readlines():
					if not line.startswith('#') and 'add_lunch_combo' in line:
						Text = line.replace('\n', '')
						Text = Text.replace('add_lunch_combo', '')
						Text = Text.replace('_', '--')
						if NameBtn == None:
							NameBtn = gtk.RadioButton(NameBtn, Text)
							NameBtn.set_active(True)
						else:NameBtn = gtk.RadioButton(NameBtn, Text)
						vbox.pack_start(NameBtn)
			for devi in find_files(os.path.join(SourceDir, "vendor"), "vendorsetup.sh"):
				for line in open(devi).readlines():
					if not line.startswith('#') and 'add_lunch_combo' in line:
						Text = line.replace('\n', '')
						Text = Text.replace('add_lunch_combo', '')
						Text = Text.replace('_', '--')
						NameBtn = gtk.RadioButton(NameBtn, Text)
						vbox.pack_start(NameBtn)

			StartButton = gtk.Button("Build!")
			vbox.pack_start(StartButton)
			StartButton.connect("clicked", self.Make, NameBtn)

			sw.add_with_viewport(vbox)
			self.notebook.insert_page(sw, BuildLabel, 4)
			window.show_all()
			self.notebook.set_current_page(4)
	def Make(self, widget, Group):
		os.chdir(SourceDir)
		active = str([r for r in GroupStandard.get_group() if r.get_active()][0].get_label().replace('--', '_')).replace(' ', '')
		print >>open(os.path.join(ScriptDir, "Source", "makeswitches"), "w"), self.build_switches
		SystemLog("%s make %s&" %(os.path.join(ScriptDir, "Source", "Build.sh"), active))			


	def NewSources(self, widget, SourceFile):
		with open(os.path.join(ConfDir, "Device"), "w") as f: f.write(SourceFile)
		SourceFile = SourceFile.replace('.py', '')
		SourceFile = SourceFile.replace('\n', '')
		self.Sources, self.URL = Source.Src.MakeVal(SourceFile)
		children = self.deviceVbox.get_children()
		children[0].destroy()
        	self.notebook.queue_draw_area(0,0,-1,-1)
		self.SetPage()

	def SetURL(self, widget, num):
		if widget.get_active():
			self.repocmd = self.URL[num]
			self.SourceName = self.Sources[num]
			self.SourceDir = os.path.join(Home, "WORKING_" + self.SourceName)


def AddGovernor():
	class GovernorFC(FileChooserD):pass
	GovernorDialog = GovernorFC()

	def Start(widget):
		dialog = gtk.FileChooserDialog("Open..",  None, gtk.FILE_CHOOSER_ACTION_OPEN, 
									   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		KConfig = self.GovernorDialog.openFile(widget, dialog, ["Kconfig"], False, False)

		if KConfig:
			Dirs = str(Kconfig).split("/")
			DirNum = len(Dirs)
			KernelDirs = Dirs[1:DirNum - 3]
			KernelRoot = '/'
			for d in KernelDirs:
				KernelRoot = os.path.join(KernelRoot, d)
			cpufreqdir = os.path.dirname(Kconfig)
			cpufreq = os.path.join(KernelRoot, "include", "linux", "cpufreq.h")
			NewKC = os.path.join(ScriptDir, "Kconfig")
			NewKCFile = open(NewKC, "a")
			MakeFile = os.path.join(cpufreqdir, "Makefile")
			NewMakeFile = os.path.join(ScriptDir, "Makefile")
			NewMake = open(NewMakeFile, "a")
			NewCpuFreq = os.path.join(ScriptDir, "cpufreq.h")
			NewCpu = open(NewCpuFreq, "a")

			for x in [NewKC, NewMakeFile, NewCpuFreq]:
				if os.path.exists(x):
					os.remove(x)
			for x in [NewKCFile, NewMake, NewCpu]:
				x.flush()
			for x in [MakeFile, Kconfig, cpufreq]:
				if os.path.exists(os.path.join(ConfDir, os.path.basename(x))):
					os.remove(os.path.join(ConfDir, os.path.basename(x)))
				shutil.copy(x, os.path.join(ConfDir, os.path.basename(x)))

			Set = False

			for GovBtn in BtnLst:
				if GovBtn.get_active():
					GovName = GovBtn.get_label()
					GovFile = os.path.join(GovDir, "cpufreq_%s.c" % GovName)
					with open(os.path.join(GovDir, GovName + "1"), "r") as f: one = f.read()
					with open(os.path.join(GovDir, GovName + "2"), "r") as f: two = f.read()
					with open(os.path.join(GovDir, GovName + "3"), "r") as f: three = f.read()
					with open(os.path.join(GovDir, GovName + "4"), "r") as f: four = f.read()
					for line in open(Kconfig, "r").readlines():
						if 'config CPU_FREQ_DEFAULT_GOV_' in line:
							Set = True
						if Set == True:
							NewKCFile.write("\n%s\n\n" % one)
							Set = False
						NewKCFile.write(line)

					for line in open(Kconfig, "r").readlines():
						if 'config CPU_FREQ_GOV_' in line:
							Set = True
						if Set == True:
							NewKCFile.write("\n%s\n\n" % two)
							Set = False
						NewKCFile.write(line)

					for line in open(MakeFile, "r").readlines():
						if "obj-$(CONFIG_CPU_FREQ_GOV_" in line:
							Set = True
						if Set == True:
							NewMake.write(three)
							Set = False
						NewMake.write(line)
					for line in open(cpufreq, "r"):
						if 'defined(CONFIG_CPU_FREQ_DEFAULT_GOV_' in line:
							Set = True
						if Set == True and '#endif' in line:
							NewCpu.write(four)
						NewCpu.write(line)

					for x in [MakeFile, Kconfig, cpufreq]:
						os.remove(x)
					shutil.copy(NewMakeFile, MakeFile)
					shutil.copy(NewKC, Kconfig)
					shutil.copy(NewCpuFreq, cpufreq)
					NewDialog(_("Added"), _("Added governors") )
	
	AddGovWindow = window
	notebook = MainApp.notebook
	sw = gtk.ScrolledWindow()
	
	vbox = gtk.VBox()
	label = gtk.Label( _("Ofcourse you need the kernel SOURCE, not the update.zip ;P") )

	SmartAssBtn = gtk.CheckButton("smartass")
	SmartAss2Btn = gtk.CheckButton("smartass2")
	LazyBtn = gtk.CheckButton("lazy")
	LulzActiveBtn = gtk.CheckButton("lulzactive")
	LagFreeBtn = gtk.CheckButton("lagfree")
	BtnLst = [SmartAssBtn, SmartAss2Btn, LazyBtn, LulzActiveBtn, LagFreeBtn]
	for Btn in BtnLst:
		vbox.pack_start(Btn, False, False, 0)
		Btn.show()

	ChooseKCButton = gtk.Button(None, _("Pick your drivers/cpufreq/Kconfig and start!"))
	vbox.pack_start(ChooseKCButton, True, False, 5)
	ChooseKCButton.connect("clicked", Start)
	
	GovLabel = NewPage(_("Add Governor"), sw)
	GovLabel.show_all()
	sw.add_with_viewport(vbox)
	notebook.insert_page(sw, GovLabel)
	AddGovWindow.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)

class DeCompile:
	InDir = os.path.join(ScriptDir, "APK", "IN")
	DecDir = os.path.join(ScriptDir, "APK", "DEC")
	OutDir = os.path.join(ScriptDir, "APK", "OUT")
	text = _("Place APKs inside %s to select them." % InDir)
	name = "(De)Compile"
	firstText = _("Decompile")
	secondText = _("Compile")
	startBtnText = _("Start (De)Compiling")
	chainFunc = "Sign"
	Dual = True

	def StartDeCompile(self, widget, firstnames, secnames):
		First = self.FirstButton.get_active()
		Second = self.SecondButton.get_active()
		if First:
			Number = len(firstnames)
			if Number == 0:
				NewDialog(_("ERROR"), _("No APKs selected!"))
			for num in range(0, Number):
				APK = firstnames[num]
				for apk in find_files(self.InDir, '*.apk'):
					name = os.path.basename(apk)
					if APK == name :
						ApkDir = APK.replace('.apk', '')
						APK = os.path.join(self.InDir, APK)
						OutDir = os.path.join(self.DecDir, ApkDir)
						SystemLog("java -jar %s d -f '%s' '%s'" %(ApkJar, APK, OutDir))
						print _("Decompiled %s" % APK)
			self.Refresh(widget, self.vbox)
		if Second:
			Number = len(secnames)
			if Number == 0:
				NewDialog(_("ERROR"), _("No APKs selected!" % os.path.join("APK", "IN") ))
			for num in range(0, Number):
				Dec = secnames[num]
				for dec in os.listdir(self.DecDir):
					if dec == Dec:
						ApkFolder = os.path.join(self.DecDir, dec)
						ApkName = os.path.join(self.OutDir, "Unsigned-" + Dec + ".apk")
						os.chdir(UtilDir)
						SystemLog("java -jar '%s' b -f '%s' '%s'" %(ApkJar, ApkFolder, ApkName))
						print _("Compiled %s" % ApkName)
			callback(widget, self.chainFunc)

	def Refresh(self, widget, vbox):
		KillPage(widget, vbox)
		self.__init__()

	def __init__(self):
		DeCompileWindow = window
		notebook = MainApp.notebook
		sw = gtk.ScrolledWindow()
	
		self.vbox = gtk.VBox()

		InfoLabel = gtk.Label(self.text)
		self.vbox.pack_start(InfoLabel, False, False, 0)

		self.FirstButton = gtk.RadioButton(None, self.firstText)
		self.vbox.pack_start(self.FirstButton, False, False, 10)
		decname = []
		comname = []
		for apk in find_files(self.InDir, '*.apk'):
			name = os.path.basename(apk)
			NameBtn = gtk.CheckButton(name)
			NameBtn.connect("toggled", AddToList, decname, name)
			self.vbox.pack_start(NameBtn, False, False, 0)

		if self.Dual == True:
			self.SecondButton = gtk.RadioButton(self.FirstButton, self.secondText)
			self.vbox.pack_start(self.SecondButton, False, False, 10)
			for dec in os.listdir(self.DecDir):
				name = os.path.join(self.DecDir, dec)
				NameBtn = gtk.CheckButton(dec)
				NameBtn.connect("toggled", AddToList, comname, dec)
				self.vbox.pack_start(NameBtn, False, False, 0)

		self.StartButton = gtk.Button(self.startBtnText)
		self.StartButton.connect("clicked", self.StartDeCompile, decname, comname)
		#self.StartButton.connect("clicked", StartThread, self.StartDeCompile, (comname, decname,))
		self.vbox.pack_start(self.StartButton, False, False, 15)


		RefreshBtn = gtk.Button(_("Refresh") )
		RefreshBtn.connect("clicked", self.Refresh, vbox)
		self.vbox.pack_end(RefreshBtn, False, False, 10)

		DeComLabel = NewPage(self.name, sw)
		DeComLabel.show_all()
		sw.add_with_viewport(self.vbox)
		notebook.insert_page(sw, DeComLabel)
		DeCompileWindow.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)
	
	
class OptimizeImage:
	class OptimizeFC(FileChooserD):pass
	OptimizeDialog = OptimizeFC()

	def Start(self, widget):
		Selected = self.OptimizeDialog.out
		if Selected:
			for file in Selected:
				SystemLog('"%s" -o99 "%s"' %(OptPng, file))
			NewDialog(_("Optimize Images"),  _("Successfully optimized images"))

	def __init__(self):
		OptimizeImageWindow = window
		notebook = MainApp.notebook
		sw = gtk.ScrolledWindow()
	
		vbox = gtk.VBox()


		ChooseImageButton = gtk.Button(_("Choose Images"))
		OptimizeImDial = gtk.FileChooserDialog("Open..",  None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		ChooseImageButton.connect("clicked", self.OptimizeDialog.openFile, OptimizeImDial, ["*.png"], True, False)
		vbox.pack_start(ChooseImageButton, True, False)


		StartButton = gtk.Button(_("Start"))
		vbox.pack_start(StartButton, True, False, 5)
		StartButton.connect("clicked", Start)
	
		OptimizeLabel = NewPage(_("Optimize Images"), sw)
		OptimizeLabel.show_all()
		sw.add_with_viewport(vbox)
		notebook.insert_page(sw, OptimizeLabel)
		OptimizeImageWindow.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)

#TODO: Verify if this method are 100% running for all APK and reuse optimize function!
def OptimizeInside():
	def Start(cmd):
		Number = len(apkname)
		if Number == 0:
			NewDialog(_("ERROR"), _("No images inside %s. exit." % os.path.join("APK", "IN")))
		for num in range(0, Number):
			#Extract APK
			APK = apkname[num]
			APKPath = os.path.join(ScriptDir, "APK", "IN", APK)
			DstDir = os.path.join(ScriptDir, "APK", "EX", APK.replace('.apk', ''))
			print APKPath
			ExZip(APKPath, DstDir)
			
			#Do Optimize
			for apk_img in find_files(os.path.join(ScriptDir, "APK", "EX", APK.replace('.apk', '')), "*.png"):
				name = os.path.abspath(apk_img)	
				print ("%s -o99 \"%s\"" %(OptPng, name))		
				SystemLog("%s -o99 \"%s\"" %(OptPng, name))
				
			#Repackage APK
			DirPath = os.path.join(ScriptDir, "APK", "EX", APK.replace('.apk', ''))
			DstFile = zipfile.ZipFile(os.path.join(ScriptDir, "APK", "OUT", "Unsigned-" + APK), "w")
			for fpath in find_files(DirPath, "*"):
				f = fpath.replace(DirPath, '')
				DstFile.write(fpath, f)
			DstFile.close()
			#Do a CLEAN
			tree = os.path.join(ScriptDir, "APK", "EX", APK.replace('.apk', ''))
			shutil.rmtree(tree, True)

	notebook = MainApp.notebook
	OptInsideWindow = window
	vbox = gtk.VBox()
	sw = gtk.ScrolledWindow()

	apkname = []

	for apk in find_files(os.path.join(ScriptDir , "APK", "IN"), "*.apk"):
		name = os.path.basename(apk)
		NameBtn = gtk.CheckButton(name)
		NameBtn.connect("toggled", AddToList, apkname, name)
		vbox.pack_start(NameBtn, False, False, 0)

	StartButton = gtk.Button(_("Do Optimize Inside APK"))
	StartButton.connect("clicked", Start)
	vbox.pack_start(StartButton, False, False, 10)

	OptInsideLabel = NewPage(_("Optimize Inside APK"), sw)
	OptInsideLabel.show_all()
	sw.add_with_viewport(vbox)
	notebook.insert_page(sw, OptInsideLabel)
	OptInsideWindow.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)

class ExPackage(DeCompile):
	InDir = os.path.join(ScriptDir, "APK", "IN")
	DecDir = os.path.join(ScriptDir, "APK", "EX")
	OutDir = os.path.join(ScriptDir, "APK", "OUT")
	text = _("Place APKs inside %s to select them." % InDir)
	name = "Extract / Repackage"
	firstText = "Extract"
	secondText = "Repackage"
	startBtnText = "Extract / Repackage"
	chainFunc = "Sign"
	Dual = True

	def StartDeCompile(self, widget, firstnames, secnames):
		First = self.FirstButton.get_active()
		Second = self.SecondButton.get_active()
		if First:
			Number = len(firstnames)
			for num in range(0, Number):
				APK = firstnames[num]
				APKPath = os.path.join(ScriptDir, "APK", "IN", APK)
				DstDir = os.path.join(ScriptDir, "APK", "EX", APK.replace('.apk', ''))
				ExZip(APKPath, DstDir)
			self.Refresh(widget, self.vbox)
		elif Second:
			Number = len(secnames)
			for num in range(0, Number):
				Ex = secnames[num]
				DirPath = os.path.join(ScriptDir, "APK", "EX", Ex)
				DstFile = zipfile.ZipFile(os.path.join(ScriptDir, "APK", "OUT", "Unsigned-" + Ex + ".apk"), "w")
				for fpath in find_files(DirPath, "*"):
					f = fpath.replace(DirPath, '')
					DstFile.write(fpath, f)
				DstFile.close()
			callback(widget, self.chainFunc)


class Sign:
	InDir = os.path.join(ScriptDir, "APK")
	text = _("Place APKs inside %s to select them.\n\n\n" % os.path.join("APK", "IN"))
	chain = "Install"
	def __init__(self, widget=None):
		self.alias = None
		hbox = gtk.HBox()
		notebook = MainApp.notebook
		sw = gtk.ScrolledWindow()
		vbox = gtk.VBox()
		sw.add_with_viewport(vbox)
		vbox2 = gtk.VBox()
		hbox.pack_start(sw)
		sep = gtk.VSeparator()
		hbox.pack_start(sep, False, False, 0)
		hbox.pack_start(vbox2, False, False, 0)

		InfoLabel = gtk.Label(self.text)
		vbox.pack_start(InfoLabel, False, False, 0)

		label = gtk.Label(_("Choose the key you want to sign with:"))
		vbox.pack_start(label, False, False)
		Std = gtk.RadioButton(None, "None")
		for key in find_files(UtilDir, "*.pk8"):
			name = str(os.path.basename(key)).replace(".pk8", '')
			NameBtn = gtk.RadioButton(Std, name)
			vbox.pack_start(NameBtn, False, False, 2)
		for key in find_files(UtilDir, "*.keystore"):
			name = str(os.path.basename(key))
			NameBtn = gtk.RadioButton(Std, name)
			vbox.pack_start(NameBtn, False, False, 2)
		[r for r in Std.get_group() if r.get_label() == "testkey"][0].set_active(True)

		label = gtk.Label("Choose the APK you want to sign:")
		vbox.pack_start(label, False, False)

		self.sign = []

		NameBtn = None
		for apk in find_files(self.InDir, "*.apk"):
			NameBtn = gtk.CheckButton(os.path.join(apk.split(os.sep)[-2], apk.split(os.sep)[-1]))
			NameBtn.APKpath = apk
			NameBtn.connect("clicked", AddToList, self.sign, apk)
			vbox.pack_start(NameBtn, False, False, 0)

		if NameBtn == None: label.set_text(InfoLabel.get_text())

		self.StartBtn = gtk.Button("Sign")
		self.StartBtn.connect("clicked", self.StartSign, Std)
		vbox.pack_start(self.StartBtn, False, False, 5)

		RefreshBtn = gtk.Button(_("Refresh") )
		RefreshBtn.connect("clicked", self.Refresh)
		vbox.pack_end(RefreshBtn, False, False, 10)

		targetF = gtk.Frame(_("Key file"))
		self.targetE = gtk.Entry()

		passF = gtk.Frame(_("Password"))
		self.passE = gtk.Entry()
		self.passE.set_visibility(False)

		aliasF = gtk.Frame(_("Alias"))
		self.aliasE = gtk.Entry()

		validityF = gtk.Frame(_("Validity (years)"))
		self.validityE = gtk.Entry()

		nameF = gtk.Frame(_("First and last name"))
		self.nameE = gtk.Entry()

		for x in [[targetF, self.targetE], [passF, self.passE], [aliasF, self.aliasE], [validityF, self.validityE], [nameF, self.nameE]]:
			x[0].add(x[1])
			vbox2.pack_start(x[0], False, False)

		localF = gtk.Frame(_("Country (XX) | State / Province | City / Locality"))
		localHBox = gtk.HBox()
		self.countryE = gtk.Entry()
		self.stateE = gtk.Entry()
		self.cityE = gtk.Entry()
		for x in [self.countryE, self.stateE, self.cityE]:
			x.set_size_request(8, 30)
			localHBox.pack_start(x)
		localF.add(localHBox)
		vbox2.pack_start(localF, False, False)

		CreateBtn = gtk.Button(_("Create keyfile"))
		CreateBtn.connect("clicked", self.CreateKey)
		vbox2.pack_start(CreateBtn, False, False)
	
	

		SignLabel = NewPage("Sign", hbox)
		notebook.insert_page(hbox, SignLabel)
		window.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)


	def Refresh(self, vbox):
		KillPage("cmd", vbox)
		self.__init__()

	def StartSign(self, widget, Std):
		name = [r for r in Std.get_group() if r.get_active()][0].get_label()
		if name.endswith(".keystore"):
			self.KeyStore(widget, name)
		else:self.NormalSign(widget, Std)

	def KeyStore(self, widget, active):
		vbox = gtk.VBox()
		KeystoreLabel = NewPage("Sign", vbox)
		frame = gtk.Frame("Enter your keystore alias:")
		self.alias = gtk.Entry()
		frame.add(self.alias)
		vbox.pack_start(frame, True, False, 0)
		frame = gtk.Frame("Enter your keystore password:")
		self.KeyPass = gtk.Entry()
		self.KeyPass.set_visibility(False)
		frame.add(self.KeyPass)
		vbox.pack_start(frame, True, False, 0)
		frame = gtk.Frame("Enter your private key pass:")
		self.StorePass = gtk.Entry()
		self.StorePass.set_visibility(False)
		frame.add(self.StorePass)
		vbox.pack_start(frame, True, False, 0)
		StartBtn = gtk.Button(_("Start signing"))
		StartBtn.connect("clicked", self.SignKeystore, active)
		vbox.pack_start(StartBtn, True, False)
		MainApp.notebook.insert_page(vbox, KeystoreLabel)
		window.show_all()
		MainApp.notebook.set_current_page(MainApp.notebook.get_n_pages() - 1)

	def SignKeystore(self, widget, key):
		alias = self.alias.get_text()
		storepass = self.StorePass.get_text()
		keypass = self.KeyPass.get_text()
		for APK in self.sign:
			OUT = os.path.join(ScriptDir, "APK", "OUT", "Signed-" + os.path.basename(APK).replace("Unsigned-", ""))
			if os.path.exists(OUT):os.remove(OUT)
			shutil.copy(APK, OUT)
			os.system("jarsigner -verbose -keystore %s -storepass %s -keypass %s %s %s" %(key, storepass, keypass, OUT, alias))
		callback(widget, self.chain)

	def NormalSign(self, widget, Std):
		name = [r for r in Std.get_group() if r.get_active()][0].get_label()
		key1 = os.path.join(UtilDir, name + ".x509.pem")
		key2 = os.path.join(UtilDir, name + ".pk8")
		Number = len(self.sign)
		for num in range(0, Number):
			APK = self.sign[num]
			APKName = APK.replace('Unsigned-', '')
			APKName = os.path.basename(APKName)
			APKName = os.path.join(ScriptDir, "APK", "OUT", "Signed-" + APKName)
			SystemLog("java -jar %s -w %s %s %s %s" %(SignJar, key1, key2, APK, APKName))
		callback(widget, self.chain)

	def CreateKey(self, widget):
		target = self.targetE.get_text()
		alias = self.aliasE.get_text()
		passw = self.passE.get_text()
		validity = self.validityE.get_text()
		name = self.nameE.get_text()
		country = self.countryE.get_text()
		state = self.stateE.get_text()
		city = self.cityE.get_text()
		SystemLog('keytool -genkey -alias %s -keypass %s -validity %s -keystore %s.keystore -storepass %s -genkeypair -dname "CN=%s, OU=JavaSoft, O=Sun, L=%s, S=%s C=%s"' %(alias, passw, validity, os.path.join(ScriptDir, "Utils", target), passw, name, city, state, country))


def Zipalign():
	def StartZip(cmd):
		Numbers = len(zipapk)
		for num in range(0, Numbers):
			APK = zipapk[num]
			FullAPK = os.path.join(ScriptDir, "APK", APK)
			Name = os.path.basename(FullAPK)
			OutFile = os.path.join(ScriptDir, "APK", "OUT", "Aligned-" + Name)
			SystemLog("%s -fv 4 %s %s" %(ZipalignFile, FullAPK, OutFile))
	notebook = MainApp.notebook
	vbox = gtk.VBox()

	InfoLabel = gtk.Label(_("Place APKs inside %s to select them." % os.path.join("APK", "IN")))
	vbox.pack_start(InfoLabel, False, False, 10)
	
	zipapk = []

	for APK in find_files(os.path.join(ScriptDir, "APK"), "*.apk"):
		Name = APK.replace(os.path.join(ScriptDir, "APK", ''), '')
		NameBtn = gtk.CheckButton(Name)
		NameBtn.connect("toggled", AddToList, zipapk, Name)
		vbox.pack_start(NameBtn, False, False, 0)

	StartBtn = gtk.Button(_("Zipalign"))
	StartBtn.connect("clicked", StartZip)
	vbox.pack_start(StartBtn, False, False, 5)
	
	
	ZipLabel = NewPage("Zipalign", vbox)
	ZipLabel.show_all()
	
	notebook.insert_page(vbox, ZipLabel)
	window.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)

def Install():
	def StartInst(cmd):
		SystemLog("%s start-server" % adb)
		print _("\n Waiting for device to connect via ADB...\n\n")
		SystemLog("adb wait-for-device")
		print _("Connected")
		for num in range(0, len(apk)):
			APK = apk[num]
			SystemLog("%s install -r %s" % (adb, APK))

	notebook = MainApp.notebook
	
	vbox = gtk.VBox()
	InfoLabel = gtk.Label(_("Place APKs inside %s to select them." % os.path.join("APK", "IN")))
	vbox.pack_start(InfoLabel, False, False, 0)
	
	apk = []

	for APK in find_files(os.path.join(ScriptDir, "APK"), "*.apk"):
		Name = APK
		NameBtn = gtk.CheckButton(Name)
		NameBtn.connect("toggled", AddToList, apk, Name)
		vbox.pack_start(NameBtn, False, False, 0)

	StartBtn = gtk.Button(_("Install"))
	StartBtn.connect("clicked", StartInst)
	vbox.pack_start(StartBtn, False, False, 5)
	
	
	InstLabel = NewPage("Install", vbox)
	InstLabel.show_all()
	
	notebook.insert_page(vbox, InstLabel)
	window.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)

class BakSmali:
	class BaksmaliFC(FileChooserD):pass
	BaksmaliDialog = BaksmaliFC()

	def StartSmali(self, widget, Group):
		if not self.CstApi.get_text() == '':
			Api = "-a %s" % self.CstApi.get_text()
		else:
			Api = ''
		smali = [r for r in Group.get_group() if r.get_active()][0].get_label()
		OutputText = self.Output.get_text()
		if not OutputText.endswith(".dex"):
			OutputText = Output + ".dex"
		Out = os.path.join(ScriptDir, "Advance", "Smali", "OUT", OutputText)
		print _("Smaling %s into %s with %s" %(os.path.join(ScriptDir, "Advance", "Smali", "Smali", smali), Out, Api))
		SystemLog("java -jar %s %s -o %s %s" %(SmaliJar, os.path.join(ScriptDir, "Advance", "Smali", "Smali", smali), Out, Api))

	def StartBakSmali(self, widget):
		dialog = gtk.FileChooserDialog("Open..",  None, gtk.FILE_CHOOSER_ACTION_OPEN, 
									   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		DexFiles = self.BaksmaliDialog.openFile(widget, dialog, ["*dex"], True, False)
		if DexFiles:
			if self.CstApi.get_text():
				Api = "-a %s" % self.CstApi.get_text()
			else:
				Api = ''

			for dexfile in DexFiles:
				dexfilebase = os.path.basename(dexfile)
				dexname = dexfilebase.replace('.dex', '')
				dexname = dexname.replace('.odex', '')
				outdir = os.path.join(ScriptDir, "Advance", "Smali", "Smali", dexname)
				print _("Baksmaling %s to %s with %s" %(dexfile, outdir, Api))
				SystemLog("java -jar %s %s -o %s %s" %(BaksmaliJar, dexfile, outdir, Api))
			NewDialog(_("BakSmali"),  _("Successfully finished BakSmali"))
		else:
			print _('Closed, no files selected')
				
	def __init__(self):
		notebook = MainApp.notebook
		vbox = gtk.VBox()

		BakSmaliBtn = gtk.Button(_("Choose file(s) to Baksmali"))
		BakSmaliBtn.connect("clicked", self.StartBakSmali)
		vbox.pack_start(BakSmaliBtn, False, False, 3)

		label = gtk.Label( _("\n\n OR choose a Smali folder to Smali:"))
		vbox.pack_start(label, False, False, 0)

		NameBtn = None

		for Folder in os.listdir(os.path.join(ScriptDir, "Advance", "Smali", "Smali")):
			NameBtn = gtk.RadioButton(NameBtn, Folder)
			NameBtn.set_active(True)
			vbox.pack_start(NameBtn, False, False, 0)

		self.Output = gtk.Entry()
		self.Output.set_text("out.dex")
		vbox.pack_start(self.Output, False, False, 0)

		SmaliBtn = gtk.Button("Smali")
		SmaliBtn.connect("clicked", self.StartSmali, NameBtn)
		vbox.pack_start(SmaliBtn, False, False, 3)

		space = gtk.Label("")
		vbox.pack_start(space, False, False, 10)

		CstApiLabel = gtk.Label( _("Choose a custom API Level:") )
		vbox.pack_start(CstApiLabel, False, False, 0)
	
		self.CstApi = gtk.Entry()
		vbox.pack_start(self.CstApi, False, False, 0)

		SmaliLabel = NewPage("BakSmali", vbox)
		SmaliLabel.show_all()
		notebook.insert_page(vbox, SmaliLabel)
		vbox.show_all()
		window.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)

def Deodex():
	class DeoFC(FileChooserD):pass
	DeoDialog = DeoFC()

	def DoDeodex(cmd, deo, bootclass=''):
		buildprop = open(os.path.join(ScriptDir, "Advance", "ODEX", "WORKING", "system", "build.prop"), "r")
		for line in buildprop.readlines():
			if line.startswith("ro.build.version.release=2.3.7"):
				global api
				version = line.replace('ro.build.version.release=', '')
				if version.startswith('2.3'):
					api = ' -a 12'
				elif version.startswith('3'):
					api = ' -a 13'
				elif version.startswith('4.0'):
					api = ' -a 14'
				elif version.split('.')[0] == '4' and version.split('.')[1] == '0' and version.split('.')[-1] >= 3:
					api = ' -a 15'
				elif version.startswith('4.1'):
					api = ' -a 16'

		WorkDir = os.path.join(ScriptDir, "Advance", "ODEX", "CURRENT")
		for apk in deo:
			ExDir = os.path.join(ScriptDir, "Advance", "ODEX", "WORKING")
			shutil.rmtree(WorkDir, True)
			os.makedirs(WorkDir)
			apk = os.path.join(ExDir, apk)
			odex = apk.replace('apk', 'odex')
			print _("Deodexing %s" % odex)
			SystemLog("java -Xmx512m -jar %s%s%s -x %s -o %s" %(BaksmaliJar, bootclass, api, odex, WorkDir) )
			SystemLog("java -Xmx512m -jar %s %s %s -o %s" %(SmaliJar, api, os.path.join(WorkDir, "*"), os.path.join(WorkDir, "classes.dex")))
			for fname in os.listdir(WorkDir):
				if not fname == "classes.dex":
					fname = os.path.join(WorkDir, fname)
					if os.path.isdir(fname):
						shutil.rmtree(fname)
					elif not os.path.isdir(fname):
						os.remove(fname)

			classes = os.path.join(WorkDir, "classes.dex")
			if os.path.exists(classes):
				print _("Adding %s to %s" %(classes, apk))
				zipf = zipfile.ZipFile(apk, "a")
				zipf.write(classes, "classes.dex")
				zipf.close()


			os.remove(odex)

		print _("\n\nDeodexing done!\n\n")
		NewDialog("Deodex", _("Done!"))
			
	def DeodexStart(cmd):
		sw = gtk.ScrolledWindow()
		vbox = gtk.VBox()
		sw.add_with_viewport(vbox)
		deo = []
		UpdateZip = DeoDialog.out
		print _("Extracting %s" % UpdateZip)
		ExDir = os.path.join(ScriptDir, "Advance", "ODEX", "WORKING", '')
		ExZip(UpdateZip, ExDir)
		if os.path.exists(os.path.join(ExDir, "system", "framework")):
			bootclass = " -d %s" % os.path.join(ExDir, "system", "framework")
		for filea in find_files(ExDir, "*.apk"):
			if os.path.exists(filea.replace('apk', 'odex')):
				files = filea.replace(ExDir, '')
				NameBtn = gtk.CheckButton(files)
				NameBtn.set_active(1)
				deo.append(filea)
				NameBtn.connect("toggled", AddToList, deo, files)
				vbox.pack_start(NameBtn, False, False, 0)
		StartButton = gtk.Button("Start deodex!")
		StartButton.connect("clicked", DoDeodex, deo, bootclass)
		vbox.pack_start(StartButton, False, False, 0)
		DeodexLabel = NewPage( _("Start deodex") , sw)
		DeodexLabel.show_all()
		notebook.insert_page(sw, DeodexLabel)
		window.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)
	notebook = MainApp.notebook
	vbox = gtk.VBox(False, 0)

	RomChooser = gtk.FileChooserDialog("Open..",  None, gtk.FILE_CHOOSER_ACTION_OPEN, 
					(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

	RomChooseBtn = gtk.Button("Choose ROM to deodex")
	RomChooseBtn.connect("clicked", DeoDialog.openFile, RomChooser, [".zip"], False)
	vbox.pack_start(RomChooseBtn, False, False, 0)

	DoneBtn = gtk.Button( _("Done") )
	DoneBtn.connect("clicked", DeodexStart)
	vbox.pack_start(DoneBtn, False, False, 3)
	
	DeodexLabel = NewPage("De-ODEX", vbox)
	DeodexLabel.show_all()
	notebook.insert_page(vbox, DeodexLabel)
	window.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)

def Odex():
	MainApp.Out = None
	def DoOdex(cmd, odex, bootclass=''):
		buildprop = open(os.path.join(ScriptDir, "Advance", "ODEX", "WORKING", "system", "build.prop"), "r")
		for line in buildprop.readlines():
			if line.startswith("ro.build.version.release=2.3.7"):
				global api
				version = line.replace('ro.build.version.release=', '')
				if version.startswith('2.3'):
					api = ' -a 12'
				elif version.startswith('3'):
					api = ' -a 13'
				elif version.startswith('4.0'):
					api = ' -a 14'
				elif version.startswith('4.1'):
					api = ' -a 15'
		for apk in odex:
			ExDir = os.path.join(ScriptDir, "Advance", "ODEX", "WORKING")
			WorkDir = os.path.join(ScriptDir, "Advance", "ODEX", "CURRENT")
			shutil.rmtree(WorkDir, True)
			os.makedirs(WorkDir)
			apk = os.path.join(ExDir, apk)
			odex = apk.replace('apk', 'odex')

			print _("Odexing %s" % odex)
			if "classes.dex" in zipfile.ZipFile(apk).namelist():
				zipfile.ZipFile(apk).extract("classes.dex", WorkDir)
				Classes = os.path.join(WorkDir, "classes.dex")
				shutil.move(Classes, odex)
			else:
				print _("Skipped %s " % odex)
			SystemLog("%s d -y -tzip %s classes.dex" %(sz, apk) )

		print _("\n\nOdexing done!\n\n")
		NewDialog("Odex", _("Done!"))
			
	def OdexStart(cmd):
		sw = gtk.ScrolledWindow()
		vbox = gtk.VBox()
		sw.add_with_viewport(vbox)
		odex = []
		UpdateZip = MainApp.Out
		print _("Extracting %s" % UpdateZip)
		ExDir = os.path.join(ScriptDir, "Advance", "ODEX", "WORKING", '')
		ExZip(UpdateZip, ExDir)
		if os.path.exists(os.path.join(ExDir, "system", "framework")):
			bootclass = " -d %s" % os.path.join(ExDir, "system", "framework")
		for filea in find_files(ExDir, "*.apk"):
			if not os.path.exists(filea.replace('apk', 'odex')):
				files = filea.replace(ExDir, '')
				NameBtn = gtk.CheckButton(files)
				NameBtn.set_active(1)
				odex.append(filea)
				NameBtn.connect("toggled", AddToList, odex, files)
				vbox.pack_start(NameBtn, False, False, 0)
		StartButton = gtk.Button("Start Odex!")
		StartButton.connect("clicked", DoOdex, odex, bootclass)
		vbox.pack_start(StartButton, False, False, 0)
		DeodexLabel = NewPage( _("Start deodex") , sw)
		DeodexLabel.show_all()
		notebook.insert_page(sw, DeodexLabel)
		window.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)

	notebook = MainApp.notebook
	vbox = gtk.VBox(False, 0)

	RomChooser = gtk.FileChooserDialog("Open..",  None, gtk.FILE_CHOOSER_ACTION_OPEN, 
					(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

	RomChooseBtn = gtk.Button("Choose ROM to odex")
	RomChooseBtn.connect("clicked", GetFile, RomChooser, [RomChooseBtn], False, ".zip")
	vbox.pack_start(RomChooseBtn, False, False, 0)

	DoneBtn = gtk.Button( _("Done") )
	DoneBtn.connect("clicked", OdexStart)
	vbox.pack_start(DoneBtn, False, False, 20)
	
	DeodexLabel = NewPage("Re-ODEX", vbox)
	DeodexLabel.show_all()
	notebook.insert_page(vbox, DeodexLabel)
	window.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)

def BinaryPort():
	class ToFC(FileChooserD):pass
	class FromFC(FileChooserD):pass
	ToDialog = ToFC()
	FromDialog = FromFC()

	InDirTo = os.path.join(ScriptDir, "Advance", "PORT", "TO")
	InDirFrom = os.path.join(ScriptDir, "Advance", "PORT", "ROM")
	WorkDir = os.path.join(ScriptDir, "Advance", "PORT", "WORKING")
	BackDir = os.path.join(ScriptDir, "Advance", "PORT", "Backup")

	def Start(cmd):
		ToROM = ToDialog.out
		ROM = FromDialog.out
		ExZip(ToROM, InDirTo)
		buildprop = open(os.path.join(InDirTo, "system", "build.prop"))
		for line in buildprop.readlines():
			if line.startswith("ro.build.version.release="):
				Version = line.replace("ro.build.version.release=", '')
				Ver = list(Version)
				StockVer = float(''.join(Ver[0:3]))
		ExZip(ROM, InDirFrom)
		buildprop = open(os.path.join(InDirFrom, "system", "build.prop"))
		for line in buildprop.readlines():
			if line.startswith("ro.build.version.release="):
				Version = line.replace("ro.build.version.release=", '')
				Ver = list(Version)
				ROMVer = float(''.join(Ver[0:3]))
		if not StockVer == ROMVer:
			NewDialog( _("Info"), _("Choose a ROM you want to port to your device with version %s.\n\n Version of your BASE: %s\nVersion of the ROM you want to port: %s" %(StockVer, StockVer, ROMVer)) )
		else:
			def Copy(From, To):
				if os.path.exists(To):
					print _("Removing %s" % To)
					if os.path.isdir(To):
						shutil.rmtree(To, True)
					else:
						os.remove(To)
				if os.path.exists(From):
					print _("Copying %s to %s" %(From, To))
					if os.path.isdir(From):
						shutil.copytree(From, To)
					else:
						shutil.copy(From, To)

			if os.path.exists(BackDir):
				shutil.rmtree(BackDir)
			os.mkdir(BackDir)
			# START EDIT!
			# Replace kernel with device one
			for kernel in ["boot.img", "zImage", "kernel.sin"]:
				original = os.path.join(InDirTo, kernel)
				ported = os.path.join(WorkDir, kernel)
				if os.path.exists(ported): os.remove(ported)
				if os.path.exists(original): shutil.copy(original, ported)
			

			# Copy the device-specific APKs
			for apk in ['Stk.apk', 'VpnServices.apk', 'Camera.apk', 'Bluetooth.apk']:
				modified = os.path.join(WorkDir, "system", "app", apk)
				apk = os.path.join(InDirFrom, "system", "app", apk)
				if os.path.exists(apk):
					shutil.copy(apk, modified)
					odex = apk.replace('.apk', '.odex')
					if os.path.exists(odex):
						shutil.copy(odex, os.path.join(WorkDir, "system", "app", os.path.basename(odex)))


			# 
			for folder in ["cameradata", "tts", "usr", "vendor", "modules", os.path.join("etc", "wifi"), os.path.join("etc", "firmware")]:
				original = os.path.join(InDirTo, "system", folder)
				modified = os.path.join(WorkDir,"system", folder)
				if os.path.exists(modified): shutil.rmtree(modified)
				if os.path.exists(original): CopyTree(original, modified, True)

			for folder in [file for file in os.listdir(os.path.join(WorkDir,"system", "etc")) if os.path.isdir(os.path.join(WorkDir, "system", "etc", file))]:
				fulldir = os.path.join(WorkDir, "system", "etc", folder)
				if not folder == "init.d" or folder == "permissions" or folder == "license":
					shutil.rmtree(fulldir)
			CopyTree(os.path.join(InDirTo, "system", "etc"), os.path.join(WorkDir, "system", "etc"), True)

			if ROMVer >= 4.0:
				for x in ["LMprec_508.emd", "PFFprec_600.emd"]:
					original = os.path.join(InDirTo, "system", "media", x)
					modified = os.path.join(WorkDir, "system", "media", x)
					if os.path.exists(modified):os.remove(modified)
					if os.path.exists(original):shutil.copy(original, modified)

			# CERTIFICATIONS
			os.remove(os.path.join(WorkDir, "META-INF", "com", "google", "android", "update-binary"))
			shutil.copy(os.path.join(InDirTo, "META-INF", "com", "google", "android", "update-binary"), os.path.join(WorkDir, "META-INF", "com", "google", "android", "update-binary"))

			for cert in os.listdir(os.path.join(WorkDir, "META-INF")):
				fullfile = os.path.join(WorkDir, "META-INF", cert)
				if not os.path.isdir(fullfile): os.remove(fullfile)
					
			for x in os.listdir(BackDir):
				Copy(os.path.join(BackDir, x), os.path.join(WorkDir, "system", "app", x))

	notebook = MainApp.notebook
	vbox = gtk.VBox(False, 0)
	ToFileDial = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  	buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
	ToExtractBtn = gtk.Button( _("Choose a working ROM for your device:"))
	ToExtractBtn.connect("clicked", ToDialog.openFile, ToFileDial, [], False, ToExtractBtn.set_label)
	RomFileDial = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  	buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
	RomFileBtn = gtk.Button( _("Choose the ROM you want to port") )
	RomFileBtn.connect("clicked", FromDialog.openFile, RomFileDial, [], False, RomFileBtn.set_label)
	vbox.pack_start(ToExtractBtn, False, False, 0)
	vbox.pack_start(RomFileBtn, False, False, 0)

	StartBtn = gtk.Button( _("Start porting") )
	StartBtn.connect("clicked", Start)
	vbox.pack_start(StartBtn, False, False, 30)
	BinaryLabel = NewPage( _("Binary port"), vbox)
	BinaryLabel.show_all()
	notebook.insert_page(vbox, BinaryLabel)
	window.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)

class Compile:
	class CustomPy(FileChooserD):
		out = FullFile
	class CustomIcon(FileChooserD):
		out = os.path.join(ScriptDir, "images", "icon.ico")
	CustomPyDialog = CustomPy()
	CustomIconDialog = CustomIcon()

	def __init__(self):
		notebook = MainApp.notebook
		vbox = gtk.VBox()

		label = gtk.Label("\nWelcome!\nThis is my home made tool to compile Python Scripts on any OS.\n")
		vbox.pack_start(label, False, False, 0)

		CustomPythonDial = gtk.FileChooserDialog("Open..",  None, gtk.FILE_CHOOSER_ACTION_OPEN, 
							(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		CustomPyBtn = gtk.Button("Choose .py file (default Studio.py)")
		CustomPyBtn.connect("clicked", self.CustomPyDialog.openFile, CustomPythonDial, ["*.py"], False, CustomPyBtn.set_label)
		vbox.pack_start(CustomPyBtn, False, False, 0)

		CustomIconDial = gtk.FileChooserDialog("Open..",  None, gtk.FILE_CHOOSER_ACTION_OPEN, 
							(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		CustomIconBtn = gtk.Button("Choose .ico file (default icon.ico)")
		CustomIconBtn.connect("clicked", self.CustomIconDialog.openFile, CustomIconDial, ["*.ico"], False, CustomIconBtn.set_label)
		if not OS == "Win":
			vbox.pack_start(CustomIconBtn, False, False, 0)

		StartComp = gtk.Button("Start compiling...")
		StartComp.connect("clicked", self.StartCompile)
		vbox.pack_start(StartComp, False, False, 40)

		CompLabel = NewPage("Compile", vbox)
		CompLabel.show_all()
		notebook.insert_page(vbox, CompLabel)
		vbox.show_all()
		window.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)


	def StartCompile(self, widget):
		ScriptFile = self.CustomPyDialog.out
		PyDir = os.path.join(Home, "PyInstallerTmp")
		PyFile = os.path.join(ConfDir, 'PyInstaller.zip')
		PyInstDir = os.path.join(Home, "PyInstaller")
		icon = self.CustomIconDialog.out
		Name = os.path.basename(ScriptFile).replace('.py', '')

		if not os.path.exists(PyInstDir):
			if not os.path.exists(PyDir):
				os.makedirs(PyDir)
				print("%s made" % PyDir)
			if not os.path.exists(PyFile):
				print _("Retrieving PyInstaller source...")
				urllib.urlretrieve('https://github.com/pyinstaller/pyinstaller/zipball/develop', PyFile)
			print _("Extracting PyInstaller source...")
			ExZip(PyFile, PyDir)
			DwnDir = os.path.join(PyDir, os.listdir(PyDir)[0])
			shutil.copytree(DwnDir, PyInstDir)
		else:
			print("%s already exists" % PyDir)

		os.chdir(PyInstDir)
		
		if OS == 'Win':
			PythonF = os.path.join(PythonDir, "python.exe")
			print _("Python = %s" % PythonF)
			SystemLog("%s pyinstaller.py -y -w -F %s -i %s -n %s" %(PythonF, ScriptFile, icon, Name))
		elif OS == 'Lin':
			SystemLog("python pyinstaller.py -y -F %s -n %s" %(ScriptFile, Name))
		elif OS == 'Mac':
			SystemLog("python pyinstaller.py -y -w -F %s -n %s" %(ScriptFile, Name))

		CompiledDir = os.path.join(PyInstDir, Name, "dist")
		compiled = os.path.join(CompiledDir, os.listdir(CompiledDir)[0])
		if os.path.exists(os.path.join(ScriptDir, os.path.basename(compiled))): os.remove(os.path.join(ScriptDir, os.path.basename(compiled)))
		shutil.copy(compiled, ScriptDir)

def ADBConfig():
	def Configure(cmd):
		active = [r for r in ConnectBtn.get_group() if r.get_active()][0].get_label()
		if not active == "Connect via IP:":
			GlobalData.AdbOpts = "-s %s" % active
		else:
			IPAdressPort = IP.get_text()			
			SystemLog("%s connect %s" %(adb, IPAdressPort))
			GlobalData.AdbOpts = "-s %s" % active

	def WirelessADB(cmd, wire=False):
		if wire == True:
			SystemLog("adb usb")
		else:
			active = [r for r in ConnectBtn.get_group() if r.get_active()][0].get_label()
			if not active == "Connect via IP:":
				IPLine = commands.getoutput("""%s shell 'netcfg | grep -e "wlan0"'""" %(adb)).split(' ')
				for x in IPLine:
					if '.' in x:
						IPAdress = x.split('/')[0]
						break
				print IPAdress
				SystemLog("%s -s %s tcpip 5555" %(adb, active))
				SystemLog("%s connect %s:5555" %(adb, IPAdress))
				NewDialog(_("ADB"), _("ADB traffic now goes through WiFi"))
			
			
	notebook = MainApp.notebook
	vbox = gtk.VBox()
	AdbConfigLabel = NewPage("Configure ADB",vbox)

	label = gtk.Label("Please select your device below:")
	vbox.pack_start(label, False, False, 15)

	devices = []

	SystemLog("%s start-server" % adb)
	adbc = commands.getoutput("%s devices" % adb).split('\n')[1:-1]
	for line in adbc:
		devicen = line.split('\t')[0]
		devices.append(devicen)

	NameBtn = None
	for device in devices:
		NameBtn = gtk.RadioButton(NameBtn, device)
		vbox.pack_start(NameBtn)

	ConnectHbox = gtk.HBox(True)
	ConnectBtn = gtk.RadioButton(NameBtn, "Connect via IP:")
	ConnectHbox.pack_start(ConnectBtn)
	IP = gtk.Entry()
	IP.set_text("IP Adress:PORT")
	ConnectHbox.pack_start(IP)
	vbox.pack_start(ConnectHbox)

	hbox = gtk.HBox(True)

	ConfigureBtn = gtk.Button("Configure")
	ConfigureBtn.connect("clicked", Configure)
	hbox.pack_start(ConfigureBtn, False)

	WirelessBtn = gtk.Button("Enable wireless ADB")
	WirelessBtn.connect("clicked", WirelessADB, False)
	hbox.pack_start(WirelessBtn, False)

	WireBtn = gtk.Button("Disable wireless ADB")
	WireBtn.connect("clicked", WirelessADB, True)
	hbox.pack_start(WireBtn, False)

	vbox.pack_end(hbox, False)


	notebook.insert_page(vbox, AdbConfigLabel)
	window.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)

class LogCat:
	READ = True
	def __init__(self):
		notebook = MainApp.notebook
		vbox = gtk.VBox()
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

		gobject.threads_init()
		gtk.gdk.threads_init()

		LogCatLabel = NewPage("Logcat",vbox)

		TextBox = gtk.TextView()
		buff = TextBox.get_buffer()
		TextBox.set_wrap_mode(gtk.WRAP_WORD)
		TextBox.set_editable(False)
		TextBox.set_cursor_visible(True)

		command = "'%s' logcat" % adb
		thr = threading.Thread(target=self.read_output, args=(TextBox, buff, command))
	
		sw.add(TextBox)
		vbox.pack_start(sw)

		hbox = gtk.HBox()
		SaveBtn = gtk.Button(_("Save logcat"))
		SaveBtn.connect("clicked", self.SaveLogcat, buff)
		hbox.pack_start(SaveBtn, True, True, 10)
		PauseBtn = gtk.Button(_("Pause"))
		PauseBtn.connect("clicked", self.PauseLogcat, thr)
		hbox.pack_start(PauseBtn, True, True, 10)
		vbox.pack_start(hbox, False, False, 0)

		notebook.insert_page(vbox, LogCatLabel)
		window.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)

		thr.start()

	def SaveLogcat(self, widget, buffer):
		start = buffer.get_start_iter()
		end = buffer.get_end_iter()
		text = buffer.get_text(start, end)
		with open(os.path.join(ScriptDir, "ADB", "Logcat-%s%s" %(date(), ['', '.txt'][OS == "Win"])), "w") as f:
			f.write(text)
		print _("Logcat saved")

	def PauseLogcat(self, widget, thread):
		widget.set_label([_("Pause"), _("Resume")][self.READ])
		self.READ = [True, False][self.READ]

	def read_output(self, view, buffer, command):
		encoding = locale.getpreferredencoding()
		utf8conv = lambda x : unicode(x, encoding).encode('utf8')
		stdin, stdouterr = os.popen4(command)
		while 1:
			while self.READ == True:
				line = stdouterr.readline()
				if not line:
					break
				gtk.gdk.threads_enter()
				iter = buffer.get_end_iter()
				buffer.place_cursor(iter)
				buffer.insert(iter, utf8conv(line))
				view.scroll_to_mark(buffer.get_insert(), 0.1)
				gtk.gdk.threads_leave()



def BuildProp():
	def Save(cmd):
		textbuffer = TextBox.get_buffer()
		text = textbuffer.get_text(textbuffer.get_start_iter() , textbuffer.get_end_iter())
		NewBuildProp = os.path.join(ScriptDir, 'ADB', 'new-build.prop')
		open(NewBuildProp, "w").write(text)
	def Pull(cmd):
		SystemLog("'%s' pull '/system/build.prop' '%s'" %(adb, os.path.join(ScriptDir, 'ADB', 'build.prop')))
		textbuffer.set_text(open(os.path.join(ScriptDir, 'ADB', 'build.prop'), "r").read())
		TextBox.set_buffer(textbuffer)
	def Reload(cmd):
		if os.path.exists(os.path.join(ScriptDir, 'ADB', 'new-build.prop')):
			textbuffer.set_text(open(os.path.join(ScriptDir, 'ADB', 'new-build.prop'), "r").read())
			TextBox.set_buffer(textbuffer)
		elif not os.path.exists(os.path.join(ScriptDir, 'ADB', 'new-build.prop')) and os.path.exists(os.path.join(ScriptDir, 'ADB', 'build.prop')):
			textbuffer.set_text(open(os.path.join(ScriptDir, 'ADB', 'build.prop'), "r").read())
			TextBox.set_buffer(textbuffer)
	def Push(cmd):
		NewBuildProp = os.path.join(ScriptDir, 'ADB', 'new-build.prop')
		Save(None)
		SystemLog("%s root" % adb)
		SystemLog("%s remount" % adb)
		SystemLog("%s wait-for-device" % adb)
		SystemLog("%s push %s /system/build.prop" %(adb, NewBuildProp) )
			
			
		
	notebook = MainApp.notebook
	vbox = gtk.VBox()
	BuildPropLabel = NewPage("Build.prop",vbox)
	sw = gtk.ScrolledWindow()

	if not os.path.exists(os.path.join(ScriptDir, 'ADB', 'build.prop')):
		SystemLog("'%s' pull '/system/build.prop' '%s'" %(adb, os.path.join(ScriptDir, 'ADB', 'build.prop')))

	TextBox = gtk.TextView()
	TextBox.set_wrap_mode(gtk.WRAP_WORD)
	TextBox.set_editable(True)
	TextBox.set_cursor_visible(True)

	textbuffer = gtk.TextBuffer()
	textbuffer.set_text(open(os.path.join(ScriptDir, 'ADB', 'build.prop'), "r").read())
	TextBox.set_buffer(textbuffer)
	
	sw.add_with_viewport(TextBox)
	vbox.pack_start(sw)

	hbox = gtk.HBox(True)

	SaveBtn = gtk.Button("Save")
	SaveBtn.connect("clicked", Save)
	hbox.pack_start(SaveBtn, False)

	PullBtn = gtk.Button("Pull un-edited")
	PullBtn.connect("clicked", Pull)
	hbox.pack_start(PullBtn, False)

	ReloadEdited = gtk.Button("Reload edited")
	ReloadEdited.connect("clicked", Reload)
	hbox.pack_start(ReloadEdited, False)

	PushBtn = gtk.Button("Push saved build.prop")
	PushBtn.connect("clicked", Push)
	hbox.pack_start(PushBtn, False)

	vbox.pack_end(hbox, False)
	

	notebook.insert_page(vbox, BuildPropLabel)
	window.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)


def BackupRestore():
	def BackupData(cmd):
		dir = date()
		os.mkdir(os.path.join(ScriptDir, 'ADB', dir))
		for x in ['/data/misc/wifi/wpa_supplicant.conf', '/data/wifi/bcm_supp.conf', '/data/misc/wifi/wpa.conf', '/data/data/com.android.providers.contacts/databases/contacts2.db', '/data/data/com.android.providers.telephony/databases/mmssms.db']:
			
			basename = x.split('/')[-1]
			SystemLog("%s pull %s %s" %(adb, x, os.path.join(ScriptDir, 'ADB', dir, basename)))
	def RestoreData(cmd, NameBtn):
		if not NameBtn == None:
			active = [r for r in NameBtn.get_group() if r.get_active()][0].get_label()
			fullpath = os.path.join(ScriptDir, 'ADB', active)
		for x in ['/data/misc/wifi/wpa_supplicant.conf', '/data/wifi/bcm_supp.conf', '/data/misc/wifi/wpa.conf', '/data/data/com.android.providers.contacts/databases/contacts2.db', '/data/data/com.android.providers.telephony/databases/mmssms.db']:
			basename = x.split('/')[-1]
			filepath = os.path.join(fullpath, basename)
			SystemLog("%s push %s %s" %(adb, filepath, x))
	def Backup(cmd):
		opts = []
		if BackupAPKs.get_active():opts.append('-apk')
		if Shared.get_active():opts.append('-shared')
		if All.get_active():opts.append('-all')
		if DecludeSystemApps.get_active(): opts.append('-nosystem')
		options = ' '.join(opts)
		SystemLog("%s backup -f %s %s" %(adb, os.path.join(ScriptDir, 'ADB', '%s.ab' % date()), options))
		NewDialog(_("Warning!"), _("Please copy your backups from the ADB directory to a safe place elsewhere"))
	def Restore(cmd):
		file = os.path.join(ScriptDir, 'ADB', [r for r in NameBtn.get_group() if r.get_active()][0].get_label()) + '.ab'
		SystemLog("%s restore %s" %(adb, file))
	notebook = MainApp.notebook
	hbox = gtk.HBox(True)
	frame = gtk.Frame("Backup apps and/or data")
	vbox = gtk.VBox()
	frame.add(vbox)
	hbox.pack_start(frame)
	BackupRestoreLabel = NewPage("Backup/Restore",hbox)

	BackupAPKs = gtk.CheckButton(_("Backup the APKs too"))
	vbox.pack_start(BackupAPKs)
	
	Shared = gtk.CheckButton(_("Backup shared storage"))
	vbox.pack_start(Shared)	
	
	All = gtk.CheckButton(_("Backup ALL applications"))
	vbox.pack_start(All)
	
	DecludeSystemApps = gtk.CheckButton(_("Declude System apps"))
	vbox.pack_start(DecludeSystemApps)
	
	BackupBtn = gtk.Button(_("Backup (get a cup of coffee)"))
	BackupBtn.connect("clicked", Backup)
	vbox.pack_start(BackupBtn, False)


	NameBtn = None
	frame2 = gtk.Frame("Restore backups")
	vbox2 = gtk.VBox()
	frame2.add(vbox2)
	for x in find_files(os.path.join(ScriptDir, 'ADB'), "*.ab"):
		for file in find_files(os.path.join(ScriptDir, 'ADB'), "*.ab"):
			BaseFile = os.path.basename(file).replace('.ab', '')
			NameBtn = gtk.RadioButton(NameBtn, BaseFile)
			vbox2.pack_start(NameBtn)

	if not NameBtn == None:
		RestoreBtn = gtk.Button(_("Restore (get a cup of coffee)"))
		RestoreBtn.connect("clicked", Restore)
		vbox2.pack_start(RestoreBtn, False)
		hbox.pack_start(frame2)

	vbox3 = gtk.VBox()
	frame3 = gtk.Frame(_("Backup Contacts, SMS, WiFi"))
	frame3.add(vbox3)

	BackupDataBtn = gtk.Button(_("Backup Contacts, SMS, WiFi"))
	BackupDataBtn.connect("clicked", BackupData)
	vbox3.pack_start(BackupDataBtn, False)

	NameBtn = None
	for x in os.listdir(os.path.join(ScriptDir, 'ADB')):
		if os.path.exists(os.path.join(ScriptDir, 'ADB', x, '')):
			NameBtn = gtk.RadioButton(NameBtn, x)
			vbox3.pack_start(NameBtn)

	if not NameBtn == None:
		RestoreDataSpecBtn = gtk.Button(_("Restore Contacts, WiFi, SMS"))
		RestoreDataSpecBtn.connect("clicked", RestoreData, NameBtn)
		vbox3.pack_end(RestoreDataSpecBtn, False)


	hbox.pack_start(frame3)

	notebook.insert_page(hbox, BackupRestoreLabel)
	window.show_all()
	notebook.set_current_page(notebook.get_n_pages() - 1)

def AdbFE():
	class Data():
		PrevDir = '/sdcard/'
		MainPrevDir = ScriptDir
		FromFile = None
	def Previous(cmd, type='Android'):
		if type == 'Android':
			Update(None, Data.PrevDir, sw, type)
		elif type == 'PC':
			Update(None, Data.MainPrevDir, SwPC, type)
	def Refresh(cmd, sw, type='Android'):
		if type == 'Android':
			Update(None, Data.CurrentDir, sw, type)
		elif type == 'PC':
			Update(None, Data.MainCurrentDir, sw, type)
	def Push(cmd, Btn):
		print("%s -> %s" %(Btn.realname, Data.CurrentDir))
		if os.path.isdir(Btn.realname):
			ToDir = os.path.join(Data.CurrentDir, os.path.basename(os.path.normpath(Btn.realname)))
			SystemLog("%s shell mkdir -p %s" %(adb, ToDir))
		else: ToDir = Data.CurrentDir
		SystemLog("%s push '%s' '%s'" %(adb, Btn.realname, ToDir))
		Refresh(None, sw, 'Android')
	def Pull(cmd, Btn):
		print("%s -> %s" %(Btn.realname, Data.MainCurrentDir))
		subprocess.Popen([adb, "pull", Btn.realname, Data.MainCurrentDir])
		#SystemLog("%s pull '%s' '%s'" %(adb, Btn.realname, Data.MainCurrentDir))
		Refresh(None, SwPC, 'PC')
	def Delete(cmd):
		File = frame.CurrentFile
		print _("Deleting %s" % File)
		SystemLog("%s shell rm '%s'" %(adb, File))
		Refresh("cmd", sw, "Android")
	def Copy(cmd):
		Data.FromFile = frame.CurrentFile
		Data.DeleteFile = False
	def Paste(cmd):
		if not Data.FromFile == None:
			SystemLog('%s shell cp "%s" "%s"' %(adb, Data.FromFile, Data.CurrentDir))
			if Data.DeleteFile == True:
				SystemLog("%s shell rm %s" %(adb, Data.FromFile))
		Refresh("cmd", sw, "Android")
	def Cut(cmd):
		Data.FromFile = frame.CurrentFile
		Data.DeleteFile = True
	def SetPerm(cmd):
		file = frame.CurrentFile
		perm = ''
		curvalue = 0
		for btn in permissions:
			txt = btn.pos
			row = txt.split(',')[0]
			col = txt.split(',')[-1]
			value = [1, 2, 4][int(col)]

			if btn.get_active():
				curvalue = curvalue + value
			if col == "2":
				perm = perm + str(curvalue)
				curvalue = 0
		SystemLog("%s shell chmod %s %s" %(adb, perm, file))
	def EditFile(cmd, file):
		frame.set_label(os.path.basename(file))
		frame.CurrentFile = file
		frame.show_all()	
	def Update(cmd, Dir, sw, type='Android'):
		NewDir = os.path.join(Dir, '')
		child = sw.get_child()
		if not child == None: child.destroy()
		vbox1 = gtk.VBox()
		sw.add_with_viewport(vbox1)
		if type == 'Android':
			Data.PrevDir = os.path.dirname(os.path.normpath(NewDir))
			Data.CurrentDir = NewDir
			for x in [["'%s' shell find '%s' -maxdepth 1 -type d | sort -d" %(adb, NewDir), True], ["'%s' shell find '%s' -maxdepth 1 -type f | sort -d" %(adb, NewDir), False]]:
				cmd = x[0]
				Dir = x[1]
				for filen in str(commands.getoutput(cmd)).split('\n'):
					FileName = str(filen).replace('\r', '')
					BaseName = os.path.basename(os.path.normpath(FileName))
					if FileName == NewDir:
						continue
					box = gtk.HBox()
					image = gtk.Image()
					if Dir == True and BaseName.startswith("."): imf = os.path.join(ScriptDir, "images", "folder.png")
					elif Dir == True: imf = os.path.join(ScriptDir, "images", "folder-brown.png")
					else: imf = os.path.join(ScriptDir, "images", "file.png")
					image.set_from_file(imf)
					Btn = gtk.Button(BaseName)
					Btn.realname = FileName
					if Dir == True:
						Btn.connect("clicked", Update, FileName, sw, 'Android')
					else:
						Btn.connect("clicked", EditFile, FileName)
						
					Btn.set_relief(gtk.RELIEF_NONE)
					# Set PULL BTN
					PullBtn = gtk.Button()
					im = gtk.Image()
					im.set_from_stock(gtk.STOCK_GO_FORWARD, gtk.ICON_SIZE_MENU)
					PullBtn.set_image(im)
					PullBtn.connect("clicked", Pull, Btn)
					box.pack_start(PullBtn, False)
					# 
					box.pack_start(image, False, False, 4)
					box.pack_start(Btn, False)
					vbox1.pack_start(box, False, False, 0)
			location.set_text(NewDir)
		else:
			Data.MainPrevDir = os.path.dirname(os.path.normpath(NewDir))
			Data.MainCurrentDir = NewDir
			dirlist = []
			for dir in os.listdir(NewDir):
				if os.path.isdir(os.path.join(NewDir, dir)): dirlist.append(os.path.join(NewDir, dir))
			dirlist.sort()
			filelist = []
			for file in os.listdir(NewDir):
				if not os.path.isdir(os.path.join(NewDir, file)): filelist.append(os.path.join(NewDir, file))
			filelist.sort()
			for files in dirlist + filelist:
				BaseName = os.path.basename(os.path.normpath(files))
				box = gtk.HBox()
				image = gtk.Image()
				if BaseName.startswith("."): imf = os.path.join(ScriptDir, "images", "folder.png")
				elif os.path.isdir(files): imf = os.path.join(ScriptDir, "images", "folder-brown.png")
				else: imf = os.path.join(ScriptDir, "images", "file.png")
				image.set_from_file(imf)
				Btn = gtk.Button(BaseName)
				Btn.realname = files
				if os.path.isdir(files): Btn.connect("clicked", Update, files, SwPC, 'PC')
				Btn.set_relief(gtk.RELIEF_NONE)
				#Set PUSH Button
				PushBtn = gtk.Button()
				im = gtk.Image()
				im.set_from_stock(gtk.STOCK_GO_BACK, gtk.ICON_SIZE_MENU)
				PushBtn.set_image(im)
				PushBtn.connect("clicked", Push, Btn)
				box.pack_start(PushBtn, False)
				#
				box.pack_start(image, False, False, 4)
				box.pack_start(Btn, False)
				vbox1.pack_start(box, False, False, 0)
			if dirlist + filelist == []:
				label = gtk.Label(_("Empty directory..."))
				vbox1.pack_start(label)
				
			
			LocationPC.set_text(NewDir)
		sw.show_all()
		
	notebook = MainApp.notebook
	vbox = gtk.VBox()
	AdbFELabel = NewPage("ADB FE",vbox)
	AdbFELabel.show_all()

	SwPC = gtk.ScrolledWindow()
	sw = gtk.ScrolledWindow()

	# Set Android frame
	hbox = gtk.HBox()
	location = gtk.Label('')
	BackBtn = gtk.Button()
	BackBtn.connect("clicked", Previous, "Android")
	BackImage = gtk.Image()
	BackImage.set_from_file(os.path.join(ScriptDir, "images", "back.png"))
	BackBtn.set_image(BackImage)
	RefreshImage = gtk.Image()
	RefreshImage.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU)
	RefreshBtn = gtk.Button()
	RefreshBtn.set_image(RefreshImage)
	RefreshBtn.connect("clicked", Refresh, sw, 'Android')
	hbox.pack_start(BackBtn, False, False, 0)
	hbox.pack_start(RefreshBtn, False, False, 0)
	hbox.pack_start(location, False, False, 4)
	vbox.pack_start(hbox, False, False, 0)
	
	# Set PC frame
	LocationPC = gtk.Label('')
	PcBackBtn = gtk.Button()
	PcBackBtn.connect("clicked", Previous, "PC")
	image = gtk.Image()
	image.set_from_file(os.path.join(ScriptDir, "images", "back.png"))
	PcBackBtn.set_image(image)
	PcRefreshImage = gtk.Image()
	PcRefreshImage.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU)
	PcRefreshBtn = gtk.Button()
	PcRefreshBtn.set_image(PcRefreshImage)
	PcRefreshBtn.connect("clicked", Refresh, SwPC, 'PC')
	hbox.pack_end(PcBackBtn, False, False, 0)
	hbox.pack_end(PcRefreshBtn, False, False, 0)
	hbox.pack_end(LocationPC, False, False, 4)


	HboxFM = gtk.HBox(True)
	VboxAFM = gtk.VBox()
	vbox1 = gtk.VBox()
	sw.add_with_viewport(vbox1)
	VboxAFM.pack_start(sw)
	HboxFM.pack_start(VboxAFM)

	HboxFM.pack_end(SwPC)
	Update(None, ScriptDir, SwPC, 'PC')

	Update(None, '/sdcard', sw, 'Android')
	vbox.pack_start(HboxFM)


	# SET THE EDIT PART
	vbox2 = gtk.VBox()
	hboxx = gtk.HBox(True)
	hboxx.pack_start(vbox2)
	frame = gtk.Frame("Edit")
	frame.add(hboxx)
	permissions = []
	for x in range(0,4):
		hbox2 = gtk.HBox(True)
		if not int(x) == 0:
			x = x - 1
			label = gtk.Label(["owner", "group", "others"][x])
			hbox2.pack_start(label)
			for y in range(0,3):
				CheckButton = gtk.CheckButton()
				CheckButton.pos = "%s,%s" %(x, y)
				permissions.append(CheckButton)
				hbox2.pack_start(CheckButton, False)
		else:
			for y in range(0,4):
				label = gtk.Label(["", "read", "write", "execute"][y])
				hbox2.pack_start(label, False)


			
		vbox2.pack_start(hbox2, False, False, 0)
	PermBtn = gtk.Button(_("Set permissions"))
	PermBtn.connect("clicked", SetPerm)
	vbox2.pack_start(PermBtn, False, False, 0)

	sep = gtk.HSeparator()
	vbox2.pack_start(sep, False, False, 2)

	vbox3 = gtk.VBox()
	ToolHBox = gtk.HBox(True)
	for x in [[gtk.STOCK_DELETE, Delete], [gtk.STOCK_COPY, Copy], [gtk.STOCK_CUT, Cut], [gtk.STOCK_PASTE, Paste]]:
		im = gtk.Image()
		im.set_from_stock(x[0], gtk.ICON_SIZE_MENU)
		Btn = gtk.Button()
		Btn.connect("clicked", x[1])
		Btn.set_image(im)
		ToolHBox.pack_start(Btn)
	vbox2.pack_start(ToolHBox, False, False, 0)

	VboxAFM.pack_end(frame, False)
	frame.show_all()
	vbox.show_all()

	notebook.insert_page(vbox, AdbFELabel)
	notebook.set_current_page(notebook.get_n_pages() - 1)
	window.show_all()
	frame.hide()

class OmegaSB(Theme, CopyFrom):
	class OmegaThemeFC(FileChooserD): pass
	OmegaThemeDialog = OmegaThemeFC()

	Name = "Statusbar"
	PreviewDir = os.path.join(ScriptDir, "images", "Omega")
	SrcDir = os.path.join(OmegaDir, "Working")
	DownloadDir = os.path.join(OmegaDir, "Download")
	TemplateDir = os.path.join(OmegaDir, "Templates")
	CurrentTemplateDir = os.path.join(TemplateDir, Name)
	TemplateZip = os.path.join(TemplateDir, Name + ".zip")
	BuildDir = os.path.join(OmegaDir, "Build")
	msg = _("Choose the color you want to theme with!")

	def __init__(self):
		notebook = MainApp.notebook
		self.OmegaVbox = gtk.VBox()
		self.OmegaNotebook = gtk.Notebook()
		self.OmegaNotebook.set_tab_pos(gtk.POS_LEFT)
		self.OmegaVbox.pack_start(self.OmegaNotebook)

		self.ThemeImage = gtk.Image()
		self.OmegaVbox.pack_start(self.ThemeImage, False, False, 8)

		self.ThemeSW = gtk.ScrolledWindow()
		self.ThemeVbox = gtk.VBox()
		self.ThemeSW.add_with_viewport(self.ThemeVbox)


		UploadThemeBtn = gtk.Button(_("Upload theme APK"))
		UploadThemeBtn.connect("clicked", self.UploadTheme)
		self.ThemeVbox.pack_start(UploadThemeBtn, False, False)

		self.OmegaNotebook.insert_page(self.ThemeSW, gtk.Label("Theme"), 0)
		NotificationTypes = ["*com*", "*background*", "*bluetooth*", "*noti*", "*alarm*", "*ringer*", "*gps*", "*warning*", "*usb*"]
		BatteryTypes = ["*battery*.png"]
		SignalTypes = ["*signal*.png", "*data_fully_connected*"]
	
		# DOWNLOAD THEMES TAB
		BatteryList = ["battery", "batt_*.png", "batt_", "*battery*.png", "*battery*65*.png"]
		SignalList = ["signal", "*signal_*.png", "signal_", ["*signal*.png", "*data_fully_connected*"], "*wifi*4*.png"]
		NotificationsList = ["Notifications", "noti_*.png", "noti_", NotificationTypes, "*adb*"]
		for type in [BatteryList, SignalList, NotificationsList]:
			model = gtk.ListStore(str, gtk.gdk.Pixbuf)
			for x in find_files(os.path.join(self.PreviewDir), type[1]):
				name = str(os.path.splitext(os.path.basename(x))[0].split(type[2])[1]).capitalize()
				model.append([name, gtk.gdk.pixbuf_new_from_file(x)])

			cb = gtk.ComboBox(model)
			hbox = gtk.HBox(True)
			ThemesVbox = gtk.VBox()

			txt_cell = gtk.CellRendererText()
			cb.pack_start(txt_cell, True)
			cb.add_attribute(txt_cell, 'text', 0)

			pb_cell = gtk.CellRendererPixbuf()
			cb.pack_start(pb_cell, False)
			cb.add_attribute(pb_cell, 'pixbuf', 1)
			cb.set_title("Select battery")

			DownloadBtn = gtk.Button(_("Download"))
			DownloadBtn.connect("clicked", StartThread, self.DownloadTheme, (cb, type[2], type[4], type[0],))

			hbox.pack_start(cb)
			hbox.pack_start(DownloadBtn, False, False, 0)
			ThemesVbox.pack_start(hbox, False, False, 0)
			UploadBatteryBtn = gtk.Button(_("Upload custom battery files"))
			UploadBatteryBtn.connect("clicked", self.UpdateTheme, type[3])
			ThemesVbox.pack_start(UploadBatteryBtn, False, False)

			ThemesFrame = gtk.Frame(_("Select %s style") % type[0])
			ThemesFrame.add(ThemesVbox)
			if find_files(os.path.join(self.PreviewDir), type[1]) != []:
				self.ThemeVbox.pack_start(ThemesFrame, True, False)		
		#

		hbox = gtk.HBox()
		self.CenterClockBtn = gtk.RadioButton(None, "Center clock")
		lClock = gtk.RadioButton(self.CenterClockBtn, "Left clock")
		rClock = gtk.RadioButton(self.CenterClockBtn, "Right clock")
		for x in [lClock, self.CenterClockBtn, rClock]:
			hbox.pack_start(x, True, False)
			x.connect("toggled", self.CustomClock)
		self.ThemeVbox.pack_end(hbox, True, False)

		# COLORIZE TAB
		self.vbox = gtk.VBox()
		self.hbox = gtk.HBox()
		vbox1 = gtk.VBox()
		vbox2 = gtk.VBox()
		self.OmegaNotebook.insert_page(self.vbox, gtk.Label("Colorize"), 1)
		OmegaLabel = NewPage(_("Omega"), self.vbox)
		self.colorsel = gtk.ColorSelection()
		self.colorsel.set_current_color(gtk.gdk.Color("#33b5e5"))

		if not os.path.exists(self.SrcDir):
			os.makedirs(self.SrcDir)
		self.vbox.pack_start(self.colorsel, False, False, 0)

		self.vbox.pack_start(self.hbox, False, False, 10)
		self.hbox.pack_start(vbox1)
		sep = gtk.VSeparator()
		self.hbox.pack_start(sep, False, False, 20)
		self.hbox.pack_start(vbox2)

		StartButton = gtk.Button( _("Colorize") )
		StartButton.connect("clicked", self.StartTheming)
		PreviewButton = gtk.Button( _("Preview") )
		PreviewButton.connect("clicked", self.PreviewTheming)
		UndoPreviewButton = gtk.Button( _("Undo preview") )
		UndoPreviewButton.connect("clicked", self.UndoPreview)
		hbox = gtk.HBox(True)
		for x in [StartButton, PreviewButton, UndoPreviewButton]:hbox.pack_start(x)
		self.vbox.pack_end(hbox, True, False)
		# SET CHECKBUTTONS FOR THEMING
		self.BatteryCheck = gtk.CheckButton("Battery")
		self.NotificationCheck = gtk.CheckButton("Notifications")
		self.SignalCheck = gtk.CheckButton("Signal")
		self.StatBg = gtk.CheckButton("Statusbar bg")
		for x in [self.BatteryCheck, self.NotificationCheck, self.SignalCheck, self.StatBg]:
			vbox1.pack_start(x, False, False)
		# SET CLOCK COLORS
		self.BatteryPercColor = "#FFFFFF"
		self.ClockHourColor = "#FFFFFF"
		self.ClockDividerColor = "#FFFFFF"
		self.ClockMinuteColor = "#FFFFFF"
		self.ClockAMColor = "#FFFFFF"
		# SET CLOCK CHECKS
		self.ClockCheck = gtk.CheckButton("Clock")
		self.BattPercCheck = gtk.CheckButton("Battery percentage")
		self.ClockAMCheck = gtk.CheckButton("AM/PM")
		self.ClockHourCheck = gtk.CheckButton("Hour")
		self.ClockMinuteCheck = gtk.CheckButton("Minute")
		self.ClockDividerCheck = gtk.CheckButton("Divider")
		for x in [self.BattPercCheck, self.ClockAMCheck, self.ClockHourCheck, self.ClockMinuteCheck, self.ClockDividerCheck]:
			vbox2.pack_start(x, False, False)

		# CUSTOMIZE TAB
		self.intList = []
		self.strList = []

		# PREVIEW

		if find_files(self.SrcDir, "stat_sys_battery_65.png") == []: self.BattPic = os.path.join(ScriptDir, "images", "Empty.png")
		else: self.BattPic = find_files(self.SrcDir, "stat_sys_battery_65.png")[0]
		if find_files(self.SrcDir, "*wifi*4*") == []: self.SignPic = os.path.join(ScriptDir, "images", "Empty.png")
		else: self.SignPic = find_files(self.SrcDir, "*wifi*4*")[0]
		self.Pic3 = PILImage.open(os.path.join(self.PreviewDir, "CLOCK.png"))
		if find_files(self.SrcDir, "*adb*") == []: self.NotiPic = os.path.join(ScriptDir, "images", "Empty.png")
		else: self.NotiPic = find_files(self.SrcDir, "*adb*")[0]
		if os.path.exists(os.path.join(ScriptDir, "Omega", "Working", "status_bar_bg.png")):
			self.StatusbarPic = os.path.join(ScriptDir, "Omega", "Working", "status_bar_bg.png")
		else: self.StatusbarPic = os.path.join(self.PreviewDir, "status_bar_bg.png")

		# BUILD TAB
		self.BuildVbox = gtk.VBox()
		self.OmegaNotebook.insert_page(self.BuildVbox, gtk.Label("Build"), 3)

		hbox = gtk.HBox()
		DownloadBtn = gtk.Button("Download Template")
		DownloadBtn.connect("clicked", StartThread, self.DownloadTemplate, (self.BuildVbox,))
		hbox.pack_start(DownloadBtn)
		self.Customize = False
		if os.path.exists(os.path.join(self.TemplateDir, self.Name)): self.DownloadTemplate(DownloadBtn, self.BuildVbox)
		BuildBtn = gtk.Button("Build!")
		BuildBtn.connect("clicked", self.BuildTheme)
		hbox.pack_start(BuildBtn)
		self.BuildVbox.pack_end(hbox, True, False)
		notebook.insert_page(self.OmegaVbox, OmegaLabel)
		self.OmegaNotebook.connect("switch-page", self.EndTheming)
		window.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)
		if not os.path.exists(self.TemplateZip): StartThread("", self.DownloadTemplate, (self.BuildVbox,))

	def DownloadTheme(self, widget, cb, startpatt, newpatt, name):
		if not os.path.exists(self.DownloadDir):
			os.makedirs(self.DownloadDir)
		activeText = cb.get_active_text().lower()
		pattern = startpatt+activeText
		link = "https://dl.dropbox.com/u/22147062/Omega_Theme_Styles/StatusBar/%s/%s%s.zip" % (name.capitalize(), startpatt, activeText)
		print link
		Zip = os.path.join(self.DownloadDir, pattern + ".zip")
		if not os.path.exists(Zip):
			urllib.urlretrieve(link, Zip)
		if startpatt == "batt_": self.ExBatt(Zip, self.SrcDir, ign="*.db")
		else: ExTo(Zip, self.SrcDir, ign="*.db")
		newImage = find_files(self.SrcDir, newpatt)[0]

		if startpatt == "batt_": self.BattPic = newImage
		elif startpatt == "signal_": self.SignPic = newImage
		elif startpatt == "noti_": self.NotiPic = newImage
		self.EndTheming(widget)

	def ExBatt(self, zipf, expath, pattern = "*", ign=""):
		zip_file = zipfile.ZipFile(zipf, 'r')
		for member in zip_file.namelist():
			File = os.path.basename(member)
			if not File:continue
			source = zip_file.open(member)
			if fnmatch.fnmatch(File, pattern) and not fnmatch.fnmatch(File, ign):
				filename = self.BattNameChanger(os.path.basename(member))
				target = file(os.path.join(expath, filename), "wb")
				shutil.copyfileobj(source, target)
			source.close()
			target.close()
		zip_file.close()

	def BattNameChanger(self, name):
		perc = ''.join(filter(lambda x: x.isdigit(), name))
		if "charge" in name or "anim" in name: filename = "stat_sys_battery_charge_anim%s.png" % perc
		else: filename = "stat_sys_battery_%s.png" % perc
		if filename != name:print "%s -> %s" %(name, filename)
		return filename

	def DownloadTemplate(self, widget, vbox):
		Zip = self.TemplateZip
		if not os.path.exists(Zip):
			urllib.urlretrieve(ToolAttr.DropboxLink + self.Name + ".zip", Zip)
		ExZip(Zip, os.path.dirname(Zip))
		stringFile = find_files(os.path.dirname(Zip), "strings.xml")[0]
		strings = open(stringFile, "r")
		i = 0
		hbox = gtk.HBox()
		vbox.pack_start(hbox)
		vbox1 = gtk.VBox()
		vbox2 = gtk.VBox()
		hbox.pack_start(vbox1)
		hbox.pack_start(vbox2)
		for line in strings.read().split("\n"):
			if i > 0 and '"' in line:
				value = strip_esc(line).split('"')[1]
				sett = str(strip_esc(line).split(">", 1)[1]).split("<")[0]
				try:
					if int(sett) in range(0,23):self.intList.append([value, sett])
				except:
					self.strList.append([value, sett])
			i += 1
		for x in self.strList:
			frame = gtk.Frame(x[0])
			entry = gtk.Entry()
			frame.add(entry)
			if self.strList.index(x) < len(self.strList) / 2 : vbox1.pack_start(frame)
			else: vbox2.pack_start(frame)
			self.strList[self.strList.index(x)].append(entry.get_text)
		if not self.Customize == True:
			self.SetCustomize()
			self.Customize = True

	def SetCustomize(self):
		sw = gtk.ScrolledWindow()
		hbox = gtk.HBox(True)
		vbox1 = gtk.VBox()
		vbox2 = gtk.VBox()
		hbox.pack_start(vbox1, True, False)
		self.ShiftCheck = gtk.CheckButton(_("Shift value when changing"))
		vbox1.pack_start(self.ShiftCheck)
		hbox.pack_start(vbox2, True, False)
		sw.add_with_viewport(hbox)
		for x in self.intList:
			frame = gtk.Frame(x[0])
			adj = gtk.Adjustment(1.0, 1.0, 22.0, 1.0, 0.0, 0.0)
			spin = gtk.SpinButton(adj, 0, 0)
			spin.set_value(float(x[1]))
			frame.add(spin)
			if "location" in x[0]:
				spin.connect("value-changed", self.SpinChanged, x[0])
				vbox2.pack_start(frame)
			else: 
				spin.connect("value-changed", self.EndTheming)
				vbox1.pack_start(frame)
			self.intList[self.intList.index(x)] += [spin.get_value_as_int, spin]
		self.OmegaNotebook.insert_page(sw, gtk.Label("Customize"), 2)
		window.show_all()

	def UploadTheme(self, widget):
		ThemeVbox = gtk.VBox()
		ThemeVbox.pack_start(gtk.Label(_("Import from APK:")), False, False, 10)
		self.SignalImportBtn = gtk.CheckButton("Signal styles")
		self.NotiImportBtn = gtk.CheckButton("Notification styles")
		self.BatteryImportBtn = gtk.CheckButton("Battery styles")
		ThemeVbox.pack_start(self.SignalImportBtn, False, False, 0)
		ThemeVbox.pack_start(self.NotiImportBtn, False, False, 0)
		ThemeVbox.pack_start(self.BatteryImportBtn, False, False, 0)
		SelectApkBtn = gtk.Button("Select theme APK")
		SelectApkBtn.connect("clicked", self.ImportTheme)
		SelectApkBtn.connect("clicked", KillPage, ThemeVbox, self.OmegaNotebook)
		ThemeVbox.pack_start(SelectApkBtn, True, False)
		self.OmegaNotebook.insert_page(ThemeVbox, gtk.Label("Upload APK"), 1)
		window.show_all()
		self.OmegaNotebook.set_current_page(1)

	def ImportTheme(self, widget):
		NotificationTypes = ["com_*", "global_counter_background", "*bluetooth*", "stat_overflow_notifications", "*alarm*", "*ringer*", "*gps*", "stat_sys_warning*", "*usb*"]
		BatteryTypes = ["*stat_sys_battery*"]
		SignalTypes = ["*stat_sys_signal*", "*stat_sys_wifi*", "*stat_sys_data_fully_connected*"]
		Types = []

		NotiIgn = ["*off*", "*on*", "*tether*", "*dialog*", "ic_*"]
		IgnoreTypes = []

		self.UpdateThemeDial = gtk.FileChooserDialog(title=_("Select your theme APK"),action=gtk.FILE_CHOOSER_ACTION_OPEN,
					  	buttons=(gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		APK = self.OmegaThemeDialog.openFile(widget, self.UpdateThemeDial, ["*.apk"], False)
		
		if self.SignalImportBtn.get_active():Types += SignalTypes
		if self.NotiImportBtn.get_active():
			Types += NotificationTypes
			IgnoreTypes += NotiIgn
		if self.BatteryImportBtn.get_active():Types += BatteryTypes

		for filter in Types: ExTo(APK, self.SrcDir, pattern=filter + ".png", ign=IgnoreTypes)
		self.UndoName(None, self.SrcDir, fr="framework_res_")
		self.UndoName(None, self.SrcDir, fr="com_systemui_")

		if find_files(self.SrcDir, "*stat_sys_battery_65.png") == []: self.BattPic = os.path.join(ScriptDir, "images", "Empty.png")
		else: self.BattPic = find_files(self.SrcDir, "*stat_sys_battery_65.png")[0]
		if find_files(self.SrcDir, "*wifi*4*") == []: self.SignPic = os.path.join(ScriptDir, "images", "Empty.png")
		else: self.SignPic = find_files(self.SrcDir, "*wifi*4*")[0]
		self.Pic3 = PILImage.open(os.path.join(self.PreviewDir, "CLOCK.png"))
		if find_files(self.SrcDir, "*adb*") == []: self.NotiPic = os.path.join(ScriptDir, "images", "Empty.png")
		else: self.NotiPic = find_files(self.SrcDir, "*adb*")[0]
		if os.path.exists(os.path.join(ScriptDir, "Omega", "Working", "status_bar_bg.png")):
			self.StatusbarPic = os.path.join(ScriptDir, "Omega", "Working", "status_bar_bg.png")
		else: self.StatusbarPic = os.path.join(self.PreviewDir, "status_bar_bg.png")
		self.EndTheming(widget)

	def UndoName(self, widget, findDir, pattern="*", fr="", ba="", ex=""):
		for file in find_files(findDir, pattern):
			originalFile = os.path.basename(file)
			fileName = originalFile
			if not fr.startswith("[") and not fr.endswith("]") and not fr == '':fileName = ''.join(fileName.split(fr)[1:])
			if not ba.startswith("[") and not ba.endswith("]") and not ba == '':fileName = ''.join(os.path.splitext(fileName)[0].rsplit(ba)[:-1]) + os.path.splitext(fileName)[1]
			if not ex.startswith("[") and not ex.endswith("]") and not ex == '':fileName = os.path.splitext(fileName)[0] + ''.join(os.path.splitext(fileName)[1].rsplit(ex)[:-1])
			fullRenamed = os.path.join(os.path.dirname(file), fileName)
			if not originalFile == fileName:
				os.rename(file, fullRenamed)
		

	def UpdateTheme(self, widget, patterns=["*"]):
		self.UpdateThemeDial = gtk.FileChooserDialog(title=_("Select your theme folder"),action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
					  	buttons=(gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		self.BaseDir = self.OmegaThemeDialog.openFile(widget, self.UpdateThemeDial, [], False)

		if not self.BaseDir == None:
			if not self.BaseDir.endswith("dpi"):
				for dir in ["xhdpi", "hdpi", "mdpi", "ldpi"]:
					self.SearchDir = os.path.join(self.BaseDir, "res", "drawable-%s" % dir)
					if os.path.exists(self.SearchDir): break
			if not os.path.exists(self.SearchDir) or self.BaseDir.endswith("dpi"):
				self.SearchDir = self.BaseDir

			if isinstance(patterns, str):patterns = [patterns]
			for pattern in patterns:
				for file in [x for x in find_files(self.SearchDir, pattern) if fnmatch.fnmatch(x, pattern)]:
					if "stat_sys_battery" in os.path.basename(file):
						Dest = os.path.join(self.SrcDir, self.BattNameChanger(os.path.basename(file)) )
					else:
						Dest = os.path.join(self.SrcDir, os.path.basename(file))
					shutil.copy(file, Dest)

			if find_files(self.SrcDir, "*stat_sys_battery_65.png") == []: self.BattPic = os.path.join(ScriptDir, "images", "Empty.png")
			else: self.BattPic = find_files(self.SrcDir, "*stat_sys_battery_65.png")[0]
			if find_files(self.SrcDir, "*wifi*4*") == []: self.SignPic = os.path.join(ScriptDir, "images", "Empty.png")
			else: self.SignPic = find_files(self.SrcDir, "*wifi*4*")[0]
			self.Pic3 = PILImage.open(os.path.join(self.PreviewDir, "CLOCK.png"))
			if find_files(self.SrcDir, "*adb*") == []: self.NotiPic = os.path.join(ScriptDir, "images", "Empty.png")
			else: self.NotiPic = find_files(self.SrcDir, "*adb*")[0]
			if os.path.exists(os.path.join(ScriptDir, "Omega", "Working", "status_bar_bg.png")):
				self.StatusbarPic = os.path.join(ScriptDir, "Omega", "Working", "status_bar_bg.png")
			else: self.StatusbarPic = os.path.join(self.PreviewDir, "status_bar_bg.png")
			self.EndTheming(widget)
		

	def StartTheming(self, widget):
		Clr = self.ParseColor()
		images = []
		if self.BatteryCheck.get_active(): images += find_files(self.SrcDir, "*battery*")
		if self.NotificationCheck.get_active():
			images += find_files(self.SrcDir, "com*")
			for x in find_files(self.SrcDir, "*stat_*"):
				if not "signal" in x and not "battery" in x: images.append(x)
		if self.SignalCheck.get_active():
			images += find_files(self.SrcDir, "*stat*sys*signal*")
			images += find_files(self.SrcDir, "*stat_sys_data*")
		if self.BattPercCheck.get_active():
			self.BatteryPercColor = Clr
		if self.ClockAMCheck.get_active():
			self.ClockAMColor = Clr
		if self.ClockHourCheck.get_active():
			self.ClockHourColor = Clr
		if self.ClockMinuteCheck.get_active():
			self.ClockMinuteColor = Clr
		if self.ClockDividerCheck.get_active():
			self.ClockDividerColor = Clr

		for image in images:
			Image1 = str(image)
			if Pil == True:
				img = self.image_tint(Image1, Clr)
				img.save("%s" % Image1)
			else:
				SystemLog('convert %s -colorspace gray %s' %(Image1, Image1) )
				SystemLog('mogrify -fill "%s" -tint 100 %s' %(Clr, Image1))
		if self.StatBg.get_active():
			NewStat = PILImage.new("RGBA", PILImage.open(self.StatusbarPic).size, Clr)
			NewStat.save(os.path.join(self.SrcDir, "status_bar_bg.png"))
			self.StatusbarPic = os.path.join(self.SrcDir, "status_bar_bg.png")
		self.EndTheming(widget)

	def PreviewTheming(self, widget):
		Clr = self.ParseColor()
		images = []
		if self.BatteryCheck.get_active(): 	self.BattPic = self.image_tint(self.BattPic, Clr)
		if self.NotificationCheck.get_active():	self.NotiPic = self.image_tint(self.NotiPic, Clr)
		if self.SignalCheck.get_active():	self.SignPic= self.image_tint(self.SignPic, Clr)
		self.BattPercCheck.set_active(False)
		self.ClockAMCheck.set_active(False)
		self.ClockHourCheck.set_active(False)
		self.ClockMinuteCheck.set_active(False)
		self.ClockDividerCheck.set_active(False)

		if self.StatBg.get_active():
			NewStat = PILImage.new("RGBA", PILImage.open(self.StatusbarPic).size, Clr)
			self.StatusbarPic = NewStat
		self.EndTheming(widget)

	def UndoPreview(self, widget):
		if find_files(self.SrcDir, "*stat_sys_battery_65.png") == []: self.BattPic = os.path.join(ScriptDir, "images", "Empty.png")
		else: self.BattPic = find_files(self.SrcDir, "*stat_sys_battery_65.png")[0]
		if find_files(self.SrcDir, "*wifi*4*") == []: self.SignPic = os.path.join(ScriptDir, "images", "Empty.png")
		else: self.SignPic = find_files(self.SrcDir, "*wifi*4*")[0]
		self.Pic3 = PILImage.open(os.path.join(self.PreviewDir, "CLOCK.png"))
		if find_files(self.SrcDir, "*adb*") == []: self.NotiPic = os.path.join(ScriptDir, "images", "Empty.png")
		else: self.NotiPic = find_files(self.SrcDir, "*adb*")[0]
		if os.path.exists(os.path.join(ScriptDir, "Omega", "Working", "status_bar_bg.png")):
			self.StatusbarPic = os.path.join(ScriptDir, "Omega", "Working", "status_bar_bg.png")
		else: self.StatusbarPic = os.path.join(self.PreviewDir, "status_bar_bg.png")
		self.EndTheming(widget)
		
	def EndTheming(self, widget, event=None, data=0):
		if event == None: data = self.OmegaNotebook.get_current_page()
		TabName = CurrentPageText(self.OmegaNotebook, data)
		if (TabName == _("Customize")) and not self.intList == None: 
			Landscape = True
		else: Landscape = False

		if isinstance(self.StatusbarPic, str):
			im = PILImage.open(self.StatusbarPic).convert("RGBA")
			im.load()
		else: im = self.StatusbarPic
		if Landscape == False:
			Result = im.resize((240, 24), PILImage.ANTIALIAS)
		else: Result = im.resize((480, 24), PILImage.ANTIALIAS)
		self.usedRight = 0
		self.usedLeft = 0
		
		# RETREIVE CLOCK SIZE
		if not self.intList == []:
			ClockFontSize = ClockDotSize = int([x for x in self.intList if x[0] == "digital_clock_text_size"][0][2]())
			#int([x for x in self.intList if x[0] == "digital_clock_period_text_size"][0][2]())
		else:
			ClockFontSize = ClockDotSize = 14
		# SET CLOCK TEXT TO CUSTOM SIZE
		font = PILImageFont.truetype(os.path.join(ScriptDir, "Utils", "Roboto-Regular.ttf"), ClockFontSize)
		dotfont = PILImageFont.truetype(os.path.join(ScriptDir, "Utils", "Roboto-Regular.ttf"), ClockDotSize)
		ClockImage=PILImage.new("RGBA", (4*ClockFontSize,ClockFontSize))
		draw = PILImageDraw.Draw(ClockImage)
		draw.text((0, 0),"19", PILImageColor.getrgb(self.ClockHourColor),font=font)
		draw.text((ClockFontSize*8 /7, 0),".", PILImageColor.getrgb(self.ClockDividerColor),font=dotfont)
		draw.text((ClockFontSize + ClockDotSize/3, 0),"43", PILImageColor.getrgb(self.ClockMinuteColor),font=font)
		draw.text((ClockFontSize*15 /7 + ClockDotSize/3, 0),"pm", PILImageColor.getrgb(self.ClockAMColor),font=font)
		draw = PILImageDraw.Draw(ClockImage)
		draw = PILImageDraw.Draw(ClockImage)

		ClockLoc = [self.pasteLeft, self.pasteCenter, self.pasteRight][["Left clock", "Center clock", "Right clock"].index([r for r in self.CenterClockBtn.get_group() if r.get_active()][0].get_label())]
		Result = ClockLoc(Result, [ClockImage])

		#<!-- 22 GRID SPACES (1-2-3-4-5-6-7-8    *9-10-11-12-13-14*    15-16-17-18-19-20-21-22)-->
		if Landscape == True:
			StatusPadding = [val[2]() for val in self.intList if "statusbar_content_padding" in val][0]
			ClockLocation = [val[2]() for val in self.intList if "digital_clock_grid_location" in val][0]

			for val in [intv for intv in self.intList if "location" in intv[0] and 15 <= intv[2]() <= 22]:
				RightLoc = [7,6,5,4,3,2,1,0][val[2]() - 15]
				Padding = RightLoc*(24+StatusPadding)
				if val[2]() < ClockLocation:
					Padding += 4*ClockFontSize
				icon = self.ParseIcon(val[0], ClockImage)
				if not icon == None:
					self.pasteRight(Result, [icon], Padding)

			for val in [intv for intv in self.intList if "location" in intv[0] and 1 <= intv[2]() <= 8]:
				LeftLoc = val[2]() - 1
				icon = self.ParseIcon(val[0], ClockImage)
				if not icon == None:
					self.pasteLeft(Result, [icon], LeftLoc*(24+StatusPadding))
		else:
			Result = self.pasteRight(Result, [self.BattPic, self.SignPic])

			Result = self.pasteLeft(Result, [self.NotiPic])
			Result.load()	
		
		self.ThemeImage.set_from_pixbuf(image2pixbuf(Result))
		
	def ParseIcon(self, value, ClockIcon):
		try:
			if "omega_system" in value: 	icon = find_files(self.SrcDir, "stat_sys_warning.png")[0]
			elif "adb" in value:		icon = find_files(self.SrcDir, "stat_sys_adb.png")[0]	
			elif "usb" in value: 		icon = find_files(self.SrcDir, "stat_sys_data_usb.png")[0]

			elif "digital_clock" in value:	icon = ClockIcon
			elif "headset" in value:	icon = find_files(self.SrcDir, "stat_sys_headset_no_mic.png")[0]
			elif "bluetooth" in value:	icon = find_files(self.SrcDir, "stat_sys_data_bluetooth.png")[0]
			elif "alarm" in value:		icon = find_files(self.SrcDir, "stat_sys_alarm.png")[0]
			elif "ringer" in value:		icon = find_files(self.SrcDir, "stat_sys_ringer_silent.png")[0]
			elif "gps" in value:		icon = find_files(self.SrcDir, "stat_sys_gps*")[0]
			elif "wifi" in value: 		icon = find_files(self.SrcDir, "stat_sys_wifi_signal_3_fully.png")[0]
			elif "battery" in value: 	icon = find_files(self.SrcDir, "stat_sys_battery_65.png")[0]
			elif "network_grid" in value:	icon = find_files(self.SrcDir, "stat_sys_signal_3_fully.png")[0]
			elif "network_type" in value:	icon = find_files(self.SrcDir, "stat_sys_data_fully_connected_h.png")[0]
			else: icon = None
		except: icon = None
		return icon

	def pasteLeft(self, im, imList, padding="standard"):
		w, h = im.size
		for x in imList:
			if padding == "standard": usePadding = self.usedLeft
			else: usePadding = padding
			if PILImage.isStringType(x):  # file path?
				pasteImage = PILImage.open(x)
			else:
				pasteImage = x
			if not pasteImage.mode in ["RGB", "RGBA"]:
				if pasteImage.mode == "P": print("Converting %s to RGBA" % pasteImage.mode)
				pasteImage = pasteImage.convert("RGBA")
			pasteImage.load()
			width, height = pasteImage.size
			if height > h:
				perc = (h - 4) / height
				pasteImage = pasteImage.resize((int(perc * width), int(perc * height)), PILImage.ANTIALIAS)
				pasteImage.load()
				width, height = pasteImage.size
			box = (usePadding + 2, int((h - height) / 2), usePadding + width + 2, int(((h - height) / 2) + height))
			im.paste(pasteImage, box, pasteImage)
			if padding == "standard":
				self.usedLeft += width + 2
		return im

	def pasteCenter(self, im, image):
		if isinstance(image, str):  # file path?
			pasteImage = PILImage.open(image[0])
		else: pasteImage = image[0]
		if not pasteImage.mode in ["RGB", "RGBA"]:
			print("Converting %s to RGBA" % pasteImage.mode)
			pasteImage = pasteImage.convert("RGBA")
		pasteImage.load()
		w, h = pasteImage.size
		width, height = im.size
		if h > height:
			perc = (height - 2) / h
			pasteImage = pasteImage.resize((int(perc * w), int(perc * h)), PILImage.ANTIALIAS)
			pasteImage.load()
			w, h = pasteImage.size
		im.paste(pasteImage, (int((width / 2) - (w/2)), int((height - h) / 2),  int((width / 2) + (w/2)),   int(((height - h) / 2) + h)), pasteImage)
		return im

	def pasteRight(self, im, imList, padding="standard"):
		w, h = im.size
		for x in imList:
			if padding == "standard": usePadding = self.usedRight
			else: usePadding = padding
			if PILImage.isStringType(x):  # file path?
				pasteImage = PILImage.open(x)
			else:
				pasteImage = x
			if not pasteImage.mode in ["RGB", "RGBA"]:
				if pasteImage.mode == "P": print("Converting %s to RGBA" % pasteImage.mode)
				pasteImage = pasteImage.convert("RGBA")
			pasteImage.load()
			width, height = pasteImage.size
			if height > h:
				perc = (h - 4) / height
				pasteImage = pasteImage.resize((int(perc * width), int(perc * height)), PILImage.ANTIALIAS)
				pasteImage.load()
				width, height = pasteImage.size
			box = (w - usePadding - width - 2, int((h - height) / 2), w - usePadding - 2, int(((h - height) / 2) + height))
			im.paste(pasteImage, box, pasteImage)
			if padding == "standard":
				self.usedRight += width + 2
		return im

	def CustomClock(self, widget):
		if not self.Customize == False:
			val = ["Left clock", "Center clock", "Right clock"].index(widget.get_label())
			self.ShiftCustom("digital_clock_grid_location", [1,11,22][val], ["plus", "plus", "min"][val])
		self.EndTheming(widget)

	def SpinChanged(self, widget, valname):
		if not self.ShiftCheck.get_active(): self.EndTheming(widget)
		else:
			currentValue = widget.get_value_as_int()
			self.EndTheming(widget)
			rest = range(1, 23)
			rest.remove(currentValue)
			current = 40
			for val in [val for val in self.intList if "location" in val[0]]:
				if val[2]() in rest: rest.remove(val[2]())
			for val in rest:
				dif = val - currentValue
				if abs(dif) < abs(current):current = dif
			if current < 0: mat="min"
			elif current > 0: mat="plus"
			self.ShiftCustom(valname, currentValue, mat)

	def ShiftCustom(self, value, valInt, mat="min"):
		valList = [val for val in self.intList if val[0] == value][0]
		value = valList[0]
		AlreadySet = []
		for val in [intv for intv in self.intList if "location" in intv[0]]:
			if val[0] != value and val[2]() == valInt:AlreadySet.append(val[0])
		valList[3].set_value(valInt)
		if not AlreadySet == []:
			if mat == "min":self.ShiftCustom(AlreadySet[0], valInt - 1)
			elif mat == "plus":self.ShiftCustom(AlreadySet[0], valInt + 1)

	def BuildTheme(self, cmd):
		self.CurrentBuildDir = os.path.join(self.BuildDir, self.Name, date())
		shutil.copytree(self.CurrentTemplateDir, self.CurrentBuildDir)
		TemplateStrings = find_files(self.CurrentBuildDir, "*strings.xml")[0]
		TemplateColors = find_files(self.CurrentBuildDir, "colors.xml")[0]
		values = []
		for x in self.strList + self.intList: 
			print x[2]()
			values.append([x[0], x[2]()])
		SetXml(TemplateStrings, values)
		SetXml(TemplateColors, [["digital_clock_minute_text_color", self.ClockMinuteColor], ["digital_clock_hour_text_color", self.ClockHourColor], ["digital_clock_am_pm_text_color", self.ClockAMColor], ["digital_clock_:_text_color", self.ClockDividerColor], ["battery_percent_text_color", self.BatteryPercColor]])
		self.StartCopy(None, (self.SrcDir, os.path.join(self.CurrentBuildDir, "res", "drawable-xhdpi"), "*.png"))
		for density in [[480, "hdpi"], [320, "mdpi"], [240, "ldpi"]]:
			dpi = density[0]
			Perc = dpi * 100 / 720
			dpiDir = density[1]
			SrcDir = os.path.join(self.CurrentBuildDir, "res", "drawable-xhdpi")
			DstDir = SrcDir.replace("drawable-xhdpi", "drawable-%s" % dpiDir)
			if os.path.exists(DstDir):shutil.rmtree(DstDir)
			os.makedirs(DstDir)
			for image in find_files(SrcDir, "*.png"):
				DstFile = image.replace("drawable-xhdpi", "drawable-%s" % dpiDir)
				print("%s -> %s" %(image, DstFile))
				if image.endswith("9.png"):
					print("%s has 9patch" % image)
					shutil.copy(image, DstFile)
					continue
				if r"%" in str(Perc):
					Perc = round(float(str(Perc).replace(r'%', '')), 2)
				pixbuf = gtk.gdk.pixbuf_new_from_file(image)
				w = pixbuf.get_width()
				h = pixbuf.get_height()
				if not w <= 1 and not h <= 1:
					w = int(int(Perc * w) / 100)
					h = int(int(Perc * h)  / 100)
					pixbuf = pixbuf.scale_simple(w,h,gtk.gdk.INTERP_HYPER)
				pixbuf.save(DstFile, os.path.splitext(image)[1].replace(".", ""))

		class Compile(DeCompile):
				name = "DeCompile"
				text = _("Choose the themes you want to (de)compile")
				InDir = os.path.join(self.BuildDir, "OUT")
				DecDir = os.path.join(os.path.join(self.BuildDir, self.Name))
				OutDir = os.path.join(ScriptDir, "APK", "OUT")
				dual = False
		Compile()


class MissingTools(Utils):
	i = 0
	PageTitle = _("Missing tools")
	LabelText = _("These tools are not found on your system, and quite necessary!\nPlease install them.")
	if not OS == "Win": Java = False
	elif os.getenv("JAVA_HOME") == None: 
		Java = True
		i += 1
	if OS == "Win":
		try: import pywin32
		except ImportError: 
			PyWin32 = True
			i += 1
		else: PyWin = False
	else: PyWin = False
	if Pil == True: PIL = False
	else: 
		PIL = True
		i += 1
	if os.path.exists(os.path.join(ScriptDir, "test.jpg")): os.remove(os.path.join(ScriptDir, "test.jpg"))
	os.system("convert %s %s" %(os.path.join(ScriptDir, "images", "Empty.png"), os.path.join(ScriptDir, "test.jpg")))
	if os.path.exists(os.path.join(ScriptDir, "test.jpg")):
		IM = False
		os.remove(os.path.join(ScriptDir, "test.jpg"))
	else: 
		IM = True
		i += 1


class Customize:
	def __init__(self):
		vbox = NewPageBox()
		if not MissingTools.i == 0:
			MissingButton = gtk.Button(_("Warning! %d missing tools!" % MissingTools.i))
			MissingButton.connect("clicked", callback, MissingTools)
			vbox.pack_start(MissingButton, True, False)
		vbox.pack_start(gtk.Label(_("Use this page to customize the whole tool on-the-go!")))

		hbox = gtk.HBox()
		vbox.pack_start(hbox, False, False, 0)

		PilToggle = gtk.CheckButton(_("Use PIL (beta)"))
		if Pil == True: PilToggle.set_active(True)
		PilToggle.connect("toggled", TogglePil)
		hbox.pack_start(PilToggle, True, False)

		OmegaToggle = gtk.CheckButton(_("Omega mode"))
		if ToolAttr.OmegaVersion == True: OmegaToggle.set_active(True)
		OmegaToggle.connect("toggled", self.ToggleOmega)
		hbox.pack_start(OmegaToggle, True, False)

		DebugToggle = gtk.CheckButton(_("Debug mode"))
		if ToolAttr.Debug == True: DebugToggle.set_active(True)
		DebugToggle.connect("toggled", self.ToggleDebug)
		hbox.pack_start(DebugToggle, True, False)

		hbox1 = gtk.HBox(True)
		vbox.pack_start(hbox1, True, True, 20)
		vbox1 = gtk.VBox()
		vbox2 = gtk.VBox()
		hbox1.pack_start(vbox1, True, True, 10)
		hbox1.pack_start(vbox2, True, True,  10)
		vbox1.pack_start(gtk.Label(_("Set StudioAndroid theme:")), False, False, 0)
		Stock = gtk.RadioButton(None, _("Stock theme"))
		Stock.set_active(True)
		vbox1.pack_start(Stock, False, False)
		
		sw = gtk.ScrolledWindow()
		vbox1.pack_start(sw, True, True, 0)
		swvbox = gtk.VBox()
		sw.add_with_viewport(swvbox)
		for x in find_files(os.path.join(ScriptDir, "Utils", "Themes"), "*.zip"):
			NameBtn = gtk.RadioButton(Stock, os.path.splitext(os.path.basename(x))[0])
			swvbox.pack_start(NameBtn, False, False)
		ApplyButton = gtk.Button(_("Apply theme!"))
		ApplyButton.connect("clicked", self.SetTheme, Stock)
		vbox1.pack_end(ApplyButton, False, False)

		vbox2.pack_start(gtk.Label(_("Set language")), True, False)
		
		self.EnBtn = gtk.RadioButton(None, "English")
		self.EnBtn.set_active(True)
		self.FrBtn = gtk.RadioButton(self.EnBtn, "Francais")
		self.ItBtn = gtk.RadioButton(self.FrBtn, "Italiano")
		self.NlBtn = gtk.RadioButton(self.FrBtn, "Nederlands")
		self.RoBtn = gtk.RadioButton(self.FrBtn, "Romanian")
		vbox2.pack_start(self.EnBtn, False, False)
		vbox2.pack_start(self.FrBtn, False, False)
		vbox2.pack_start(self.ItBtn, False, False)
		vbox2.pack_start(self.NlBtn, False, False)
		NewLang = []
		for langd in [r for r in os.listdir(os.path.join(ScriptDir, "lang")) if "_" in r]:
			if not langd.split("_")[0] in ["fr", "en", "it", "nl", "ro"]:
				NewBtn = gtk.RadioButton(self.FrBtn, langd.replace("_", "--"))
				vbox2.pack_start(NewBtn, False, False)
				NewLang.append(langd)
	
		ChooseBtn = gtk.Button("Choose Language")
		vbox2.pack_end(ChooseBtn, False, False)
		ChooseBtn.connect("clicked", self.PickLanguage, self.EnBtn)

		MainApp.notebook.insert_page(vbox, gtk.Label("Customize"))
		window.show_all()
		MainApp.notebook.set_current_page(MainApp.notebook.get_n_pages() - 1)

	def SetTheme(self, widget, group):
		active = [r for r in group.get_group() if r.get_active()][0].get_label()
		if os.path.exists(os.path.join(ScriptDir, "Utils", "Themes", "Theme")):shutil.rmtree(os.path.join(ScriptDir, "Utils", "Themes", "Theme"))
		if not active == _("Stock theme"):
			ExZip(os.path.join(ScriptDir, "Utils", "Themes", active + ".zip"), os.path.join(ScriptDir, "Utils", "Themes"))
		Restart(widget)

	def PickLanguage(self, widget, group):
		with open(os.path.join(ConfDir, "Language"), "w") as f:
			if self.FrBtn.get_active(): f.write("fr_FR")
			elif self.EnBtn.get_active(): f.write("en_US")
			elif self.ItBtn.get_active(): f.write("it_IT")
			elif self.NlBtn.get_active(): f.write("nl_NL")
			else:
				active = [r for r in group.get_group() if r.get_active()][0].get_label().replace("--", "_")
				f.write(active)
		Restart(widget)

	def ToggleOmega(self, widget):
		if widget.get_active():
			with open(ToolAttr.VersionFile, "w") as f:
				f.write("omega")
			ToolAttr.OmegaVersion = False
			KillPage(widget, MainApp.AndroidVBox, False, False)
			KillPage(widget, MainApp.AdvanceVBox, False, False)
			MainApp.notebook.insert_page(MainApp.OmegaVbox, MainApp.OmegaLabel, 3)
		else:
			with open(ToolAttr.VersionFile, "w") as f:
				f.write("studio")
			ToolAttr.OmegaVersion = True
			KillPage(widget, MainApp.OmegaVbox, False, False)
			MainApp.notebook.insert_page(MainApp.AdvanceVBox, MainApp.AdvanceLabel, 3)
			MainApp.notebook.insert_page(MainApp.AndroidVBox, MainApp.AndroidLabel, 4)
		window.show_all()

		on = _("Enabled")
		off = _("Disabled")
		print ("Debug = %s, PIL = %s, Omega = %s" %([on, off][ToolAttr.Debug], [on, off][Pil], [on, off][ToolAttr.OmegaVersion]))

	def ToggleDebug(self, widget):
		if widget.get_active():
			open(os.path.join(ConfDir, "debug"), "w").close()
			ToolAttr.Debug = True
		else:
			os.remove(os.path.join(ConfDir, "debug"))
			ToolAttr.Debug = False
		on = _("Enabled")
		off = _("Disabled")
		print ("Debug = %s, PIL = %s, Omega = %s" %([on, off][ToolAttr.Debug], [on, off][Pil], [on, off][ToolAttr.OmegaVersion]))

def Changelog():
	ChangeWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
	ChangeWindow.set_size_request(700, 600)
	ChangeWindow.set_title("%s - Changelog" % ToolAttr.ToolName)
	sw = gtk.ScrolledWindow()
	ChangeWindow.add(sw)

	changelog = open(os.path.join(ScriptDir, "changelog"), "r")
	Text = changelog.read()
	Label = gtk.Label(Text)

	sw.add_with_viewport(Label)
	ChangeWindow.show_all()

def Log():
	def DeleteLog(cmd):
		os.remove(os.path.join(ScriptDir, "log")) 
	LogWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
	LogWindow.set_size_request(700, 600)
	LogWindow.set_title("%s - Log" % ToolAttr.ToolName)
	vbox = gtk.VBox(False, 4)
	sw = gtk.ScrolledWindow()
	vbox.pack_start(sw)
	LogWindow.add(vbox)

	log = open(os.path.join(ScriptDir, "log"), "r")
	Text = log.read()
	Label = gtk.Label(Text)
	Label.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("blue"))
	Label.set_selectable(True)

	sw.add_with_viewport(Label)
	DeleteButton = gtk.Button( _("Delete log") )
	DeleteButton.connect("clicked", DeleteLog)
	vbox.pack_start(DeleteButton, False)
	vbox.show_all()
	LogWindow.show_all()

def Bug(widget):
	text = "[QUOTE=log]%s[/QUOTE]\nHere is my log!" % open(os.path.join(ScriptDir, "log"), "r").read()
	clipboard = gtk.Clipboard()
	clipboard.set_text(text)
	NewDial = NewDialog("BUGREPORT", _("The log content has been copied to the clipboard"
				"\nPlease paste it in the reply that will be opened now!"))
	webbrowser.open("http://forum.xda-developers.com/newreply.php?do=newreply&noquote=1&p=22414621")

def Update():
	os.remove(ToolAttr.VersionFile)
	stablechoose =  ChooseDialog("Update", "What branch do you want?", ["Stable", "Test"])
	if stablechoose == 1:
		link = ToolAttr.GitLink + ToolAttr.UnstableBranch
	else:
		LatestTags = os.path.join(ConfDir, "Tags")
		if os.path.exists(LatestTags): os.remove(LatestTags)
		urllib.urlretrieve("https://github.com/mDroidd/StudioAndroid-GtkUI/tags", LatestTags)
		with open(LatestTags) as f:
			newestTag = [line.split('"', 2)[1] for line in f.readlines() if "/mDroidd/StudioAndroid-GtkUI/zipball/" in line][0]
		link = "https://github.com" + newestTag
	Web.open(link)

class About:
	def __init__(self):
		notebook = MainApp.notebook
		vbox = NewPageBox()

		image = gtk.Image()
		image.set_from_file(os.path.join(ScriptDir, "images", "Logo.png"))
		image.show()
		vbox.pack_start(image, False)

		hbox = gtk.HBox()
		vbox.pack_start(hbox)

		me = gtk.Image()
		me.set_from_file(os.path.join(ScriptDir, "images", "mDroidd.png"))
		me.show()
		hbox.pack_start(me, False, False, 30)


		vbox1 = gtk.VBox()
		hbox.pack_start(vbox1, True, False)
		label = gtk.Label()
		label.set_markup('<a href="http://bit.ly/SA-XDA">StudioAndroid @ XDA</a>\n<a href="mailto:martijn.ruijzendaal@gmail.com?subject=StudioAndroid">Email me: martijn.ruijzendaal@gmail.com</a>\n<a href="http://bit.ly/SA-Donate">Donate to me</a>')
		label.set_justify(gtk.JUSTIFY_CENTER)
		vbox1.pack_start(label)

		DonateImage = gtk.Image()
		DonateImage.set_from_file(os.path.join(ScriptDir, "images", "donate.png"))
		DonateButton = gtk.Button()
		DonateButton.set_image(DonateImage)
		DonateButton.set_relief(gtk.RELIEF_NONE)
		DonateButton.connect("clicked", self.Donate)
		vbox1.pack_start(DonateButton)
	
	
		notebook.insert_page(vbox, gtk.Label("About"))
		window.show_all()
		notebook.set_current_page(notebook.get_n_pages() - 1)
	def Donate(self, widget):
		Web.open("http://bit.ly/SA-Donate")

if not os.path.exists(ToolAttr.VersionFile):
	callback("cmd", "Customize")

def main():
	About()
	try:
		gobject.threads_init()
		gtk.main()
	except KeyboardInterrupt:
		exit(0)

if  __name__ == '__main__':
	main()


