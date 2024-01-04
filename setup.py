"""
Setup script for Easy Trim utility
Supported Maya versions are 2018 and 2019

drag and drop this file into a maya viewport to automatically copy files
to the necessary folders. 
"""
import sys
import os.path
import shutil
import maya.mel as mel
import maya.cmds as cmds

def onMayaDroppedPythonFile(self):
	
	mayaPath, mayaPrefsPath, setupPath = getPaths()

	versionOfMaya = getMayaVersion(mayaPath)[4:]

	print "\nVersion of Maya: %s" % versionOfMaya

	#names of the files
	script = "easyTrim.py"
	shelf = "shelf_EasyTrim.mel"
	icon = "ezTrim.png"

	#create paths to and from the proper folders
	mayaScriptsPath = os.path.join(mayaPrefsPath, versionOfMaya, "scripts", script)
	mayaShelvesPath = os.path.join(mayaPrefsPath, versionOfMaya, "prefs", "shelves", shelf)
	mayaIconsPath = os.path.join(mayaPrefsPath, versionOfMaya, "prefs", "icons", icon)

	#print paths to verify
	print "\nMaya Paths"
	print mayaScriptsPath
	print mayaShelvesPath
	print mayaIconsPath

	localScriptsPath = os.path.join(setupPath, "scripts", script)
	localShelvesPath = os.path.join(setupPath, "shelves", shelf)
	localIconsPath = os.path.join(setupPath, "icons", icon)

	print "\nSetup folder paths"
	print localScriptsPath
	print localShelvesPath
	print localIconsPath

	#copy files
	print "\ncopying files to proper directoies...\n"
	shutil.copyfile(localScriptsPath, mayaScriptsPath)
	shutil.copyfile(localShelvesPath, mayaShelvesPath)
	shutil.copyfile(localIconsPath, mayaIconsPath)

	paths = [mayaScriptsPath, mayaShelvesPath, mayaIconsPath]

	#verify all the paths exist
	pathsExist = verifyPaths(paths)

	if pathsExist:
		cmds.confirmDialog( title="Setup Complete!", message='Restart Maya to load Easy Trim tool!',
									button=['Ok'], defaultButton='Ok', dismissString='No' )
	else:
		pass

def verifyPaths(paths):
	#expecting a list of paths
	for path in paths:
		if os.path.exists(path):
			print "Verified path exists: %s" % path
		else:
			print "Path does not exist: %s" % path

			cmds.confirmDialog( title="Error in Setup", message='You may need to manually copy files, '
																'as described in Setup Instructions.txt',
								button=['Ok'], defaultButton='Ok', dismissString='No' )
			return False

	return True
	

def getMayaVersion(mayaPath):

	#determine version of maya
	supportedVersions = ["Maya2018", "Maya2019"]
	currentVersion = ""

	for year in supportedVersions:
		if year in mayaPath:
			currentVersion = year
			break
	return currentVersion
	
def getPaths():

	#gives you the path to the version of maya the script is run on
	mayaPath = sys.argv[0]

	#gives you the path to maya prefs
	mayaPrefsPath = os.path.abspath(mel.eval('getenv "MAYA_APP_DIR"'))

	#directory of currently running file
	scriptPath = os.path.abspath(os.path.dirname(__file__))

	return mayaPath, mayaPrefsPath, scriptPath