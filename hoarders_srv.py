#!/usr/bin/env python
from xml.dom import minidom
import os

#Read in the the directory path
xmldoc = minidom.parse('hoarders_srv.xml')
hoarderspath = xmldoc.getElementsByTagName('hoarderspath')[0].firstChild.wholeText
dropboxpath = xmldoc.getElementsByTagName('dropboxpath')[0].firstChild.wholeText
gdrivepath = xmldoc.getElementsByTagName('gdrivepath')[0].firstChild.wholeText

#Create directory if it doesnt exist
if not os.path.isdir(hoarderspath):
    os.mkdir(hoarderspath)
    
#Syncing

#print os.listdir(dropboxpath)
for root, dirs, files in os.walk(dropboxpath):
    print root
    print files
    root2 = root.replace(dropboxpath, hoarderspath)
    if not os.path.exists(root2):
        os.symlink(root, root2)
        