#!/usr/bin/env python
from xml.dom import minidom
from filecmp import dircmp
import math
import sys
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

# scans directory recursively and computes checksum for files
# returns a dict of checksums->file paths...if we have 
def scan_dir(dir):	
	print "Scanning directory: %s" % dir
	num_files_processed = 0

	checksums_to_file_paths = {}
	for root, dirs, files in os.walk(dir):
		files = set(files) - set(FILES_TO_IGNORE)
		for file in files:
			#if file.startswith('.'):
			#	continue
			name = os.path.join(root, file)
			md5 = md5file(name)
			checksums_to_file_paths[md5] = name
			num_files_processed = num_files_processed+1

	print "Scannning complete...indexed %d files" % num_files_processed
	return checksums_to_file_paths

def drawProgressBar(percent):
	sys.stdout.write('\r[{0}] {1}%'.format('#'*(percent/10), percent))
	sys.stdout.flush()

def copy_files_from_src_to_dst(src_scanned_dict, dst_scanned_dict, src, dst):
	files_to_copy_to_dest_dir = set(src_scanned_dict.keys()) - set(dst_scanned_dict.keys())
	
	num_files_to_copy = len(files_to_copy_to_dest_dir)
	num_files_copied_so_far = 0
	percentage = 0;

	print "Copying %i files from %s to %s" % (num_files_to_copy, src, dst)
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
			for root, dirs, name in os.walk(dst):
				if(root != dst):
					ind = root.rfind(dst)
					ind += len(dst)
					dir_rel_path = root[ind:]
					shutil.copystat(os.path.join(src, dir_rel_path), root)
			
		shutil.copy2(path_to_file, dstdir)
		num_files_copied_so_far=num_files_copied_so_far+1;
		if num_files_copied_so_far != 0:
			prev_percentage = percentage;
			percentage = int(((1.0 * num_files_copied_so_far) / num_files_to_copy)*100);
			if percentage % 10 == 0 and prev_percentage != percentage:
				drawProgressBar(percentage)
	sys.stdout.write("\n")

def run_hoarders():
	#Read in the the directory path
	xmldoc = minidom.parse('hoarders_srv.xml')
	
	storage_paths = []
	parsed_dirs = {}

	# parse out the paths to the storage dirs and scan the dir to compile a state of the directory
	for path in xmldoc.getElementsByTagName('storage_path'):
			string_path = path.firstChild.wholeText
			if not os.path.exists(string_path):
				sys.stderr.write("Path {0} was not found...the program will now exit\n".format(string_path))
				sys.exit(0)
			storage_paths.append(string_path)
			parsed_dirs[string_path] = scan_dir(string_path)

	for path_1 in storage_paths:
		for path_2 in storage_paths:
			if not (path_1 is path_2):
				print "Syncing directory %s with directory %s..." % (path_2,path_1)
				copy_files_from_src_to_dst(parsed_dirs[path_1], parsed_dirs[path_2], path_1, path_2)


if __name__ == "__main__":
	run_hoarders()