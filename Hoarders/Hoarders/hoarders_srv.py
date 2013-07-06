#!/usr/bin/env python

from xml.dom import minidom
from filecmp import dircmp
import math
import sys
import md5
import difflib
import os
import shutil

HOARDERS_DIR = ''
DROPBOX_DIR = ''

# ignore all .DS_Store files
# This is probably the bad way to do it but for copytree we need to pass a tuple for the list of files
# to ignore and this makes the most sense
FILES_TO_IGNORE_LIST = ['.DS_Store']
FILES_TO_IGNORE_TUPLE = ('.DS_Store')

def process_xml(file_name):
	xmldoc = minidom.parse(file_name)
	
	# list containing all of the storage paths that the user has
	storage_paths = []
	hoarders_paths = []

	# parsed hoarders_dir 
	#base_hoarders_parsed_dir_files = {}
	#base_hoarders_parsed_dir_subdirs = {}

	# parse out the paths to the storage dirs and scan the dir to compile a state of the directory
	for path in xmldoc.getElementsByTagName('storage_path'):
			string_path = path.firstChild.wholeText
			if not os.path.exists(string_path):
				sys.stderr.write("Path {0} was not found...the program will now exit\n".format(string_path))
				sys.exit(0)
			storage_paths.append(string_path)
	
	for hoarders_dir in xmldoc.getElementsByTagName('hoarders_directory'):
			string_path = hoarders_dir.firstChild.wholeText
			if not os.path.exists(string_path):
				sys.stderr.write("Path {0} was not found...the program will now exit\n".format(string_path))
				sys.exit(0)
			hoarders_paths.append(string_path)

	return storage_paths, hoarders_paths;

def copy_hoarders_dir_into_storage_dir(hoarders_dir, storage_dir):
	print "hoarders_dir: %s, storage_dir: %s" % (hoarders_dir, storage_dir)
	shutil.copytree(hoarders_dir, storage_dir)

def init_hoarders():
	#Read in the the directory path
	storage_paths, global_hoarders_path = process_xml('hoarders_srv.xml')

	for storage_path in storage_paths:
		for hoarders_path in global_hoarders_path:
			storage_base_hoarders_dir = os.path.join(storage_path, 'hoarders')
			hoarders_tmp = os.path.join(storage_base_hoarders_dir, os.path.basename(hoarders_path))
			
			if(os.path.exists(storage_base_hoarders_dir)):
				shutil.rmtree(storage_base_hoarders_dir)
			copy_hoarders_dir_into_storage_dir(hoarders_path, hoarders_tmp) 

def run_hoarders():
    #Startup
    print('Welcome to Hoarders!')

    HOARDERS_DIR = raw_input("Enter your Hoarders dir: ");

    if HOARDERS_DIR == '':
        print 'Need to specify Hoarders dir'
        sys.exit(0)

    DROPBOX_DIR = raw_input("Enter your Dropbox dir: ");

    if DROPBOX_DIR == '':
        print 'Need to specify Dropbox dir'
        sys.exit(0)

	#Read in the the directory path
	#storage_paths, parsed_dir_files, parsed_dir_subdirs = process_xml('hoarders_srv.xml')

	#for path_1 in storage_paths:
	#	for path_2 in storage_paths:
	#		if not (path_1 is path_2):
	#			print "Syncing sub-directories from directory %s with directory %s..." % (path_2,path_1)
	#			copy_subdirs_from_src_to_dst(parsed_dir_subdirs[path_1], parsed_dir_subdirs[path_2], path_1, path_2)
	#			print "Syncing files from directory %s with directory %s..." % (path_2,path_1)
	#			copy_files_from_src_to_dst(parsed_dir_files[path_1], parsed_dir_files[path_2], path_1, path_2)

if __name__ == "__main__":
	#run_hoarders()
	init_hoarders()