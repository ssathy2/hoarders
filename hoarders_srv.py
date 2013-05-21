#!/usr/bin/env python
from xml.dom import minidom
from filecmp import dircmp

import md5
import difflib
import os
import shutil

# ignore all .DS_Store files
FILES_TO_IGNORE = ['.DS_Store']

# From http://mail.python.org/pipermail/python-list/2005-February/306758.html
def md5file(filename):
	"""Return the hex digest of a file without loading it all into memory"""
	fh = open(filename)
	digest = md5.new()
	while 1:
		buf = fh.read(4096)
		if buf == "":
			break
		digest.update(buf)
	fh.close()
	return digest.hexdigest()

# scans directory recursively and computes checksum for files and subdirs in dir passed in
# returns a dict of checksums->file paths...if we have 
def scan_dir(dir):	
	checksums_to_file_paths = {}

	for root, dirs, files in os.walk(dir):
		files = set(files) - set(IGNORE_FILES)
		for file in files:
			#if file.startswith('.'):
			#	continue
			name = os.path.join(root, file)
			md5 = md5file(name)
			checksums_to_file_paths[md5] = name

	return checksums_to_file_paths

def copy_files_from_src_to_dst(src, dst):
	src_scanned_dict = scan_dir(src)
	dst_scanned_dict = scan_dir(dst)
	
	files_to_copy_to_dest_dir = set(src_scanned_dict.keys()) - set(dst_scanned_dict.keys())
	
	for key in files_to_copy_to_dest_dir:
		path_to_file = src_scanned_dict[key]
		ind = path_to_file.rfind(src)
		ind += len(src)
		file_rel_path = path_to_file[ind:]
		
		assert not os.path.isabs(file_rel_path)
		dstdir = os.path.join(dst, os.path.dirname(file_rel_path))
		
		# check if the dir exists already and then add if it doesn't
		if not os.path.exists(dstdir):	
			# create all sub-dirs
			os.makedirs(dstdir) 
		shutil.copy(path_to_file, dstdir)

def run_hoarders():
	#Read in the the directory path
	xmldoc = minidom.parse('hoarders_srv.xml')
	
	# parse out the paths to google drive and dropbox...testing
	dropboxpath = xmldoc.getElementsByTagName('dropboxpath')[0].firstChild.wholeText
	gdrivepath = xmldoc.getElementsByTagName('gdrivepath')[0].firstChild.wholeText

	copy_files_from_src_to_dst(dropboxpath, gdrivepath)

if __name__ == "__main__":
	run_hoarders()