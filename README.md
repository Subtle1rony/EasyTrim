## Setup

To setup the tool and begin using it, the fastest way is to drag the setup.py script into the viewport of a running instance of Maya. That will copy the script files to the appropriate Maya folders. There should be some output in the script editor so you can see what it's doing.

Restart Maya and you should see a new shelf tab with an 'EZTrim' button in it. You can then drag this button to any shelf you like. You can delete the Easy Trim shelf tab if you do not need it and the 'EZTrim' button should still work.

If for some reason the above setup script does not work, you can manually copy the files to the proper folders as follows:

copy file: ../EasyTrim/scripts/easyTrim.py to ../Documents/maya/2024/scripts
copy file: ../EasyTrim/icons/eZTrim.png to ../Documents/maya/2024/prefs/icons
copy file: ../EasyTrim/shelves/shelf_EasyTrim.mel to ../Documents/maya/2024/prefs/shelves
(this is exactly the same thing setup.py is doing)
