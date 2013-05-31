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
# This is probably the bad way to do it but for copytree we need to pass a tuple for the list of files
# to ignore and this makes the most sense
FILES_TO_IGNORE_LIST = ['.DS_Store']
FILES_TO_IGNORE_TUPLE = ('.DS_Store')

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
# returns a dict of checksums->file paths and a list of all subdirs in the dir passed in

def scan_dir(dir):	
	print "Scanning directory: %s" % dir
	num_files_processed = num_sub_dirs_processed = 0
	# store key-value of {file_path, md5(file)}
	checksums_to_file_paths = {}
	# store all sub-directories of directory passed in
	dir_paths = []

	for root, dirs, files in os.walk(dir):
		
		if(root != dir):
			dir_paths.append(root[len(dir):])
			num_sub_dirs_processed += 1

		files = set(files) - set(FILES_TO_IGNORE_LIST)
		for file in files:
			#if file.startswith('.'):
			#	continue
			name = os.path.join(root, file)
			md5 = md5file(name)
			checksums_to_file_paths[md5] = name
			num_files_processed += 1

	print "Scannning complete...indexed %d files and %d sub-directories" % (num_files_processed, num_sub_dirs_processed)
	return (dir_paths, checksums_to_file_paths)

def draw_progress_bar(percent):
	sys.stdout.write('\r[{0}] {1}%'.format('#'*(percent/10), percent))
	sys.stdout.flush()

def ignore_files_callback(dir,filenames):
    return [filename for filename in filenames if not filename.endswith(FILES_TO_IGNORE_TUPLE)]

def copy_dir_stat(rel_dir_path, src, dst):
	dir_name = os.path.dirname(rel_dir_path)
	while dir_name != "":
		shutil.copystat(os.path.join(src, dir_name), os.path.join(dst, dir_name))
		dir_name = os.path.dirname(dir_name)

def copy_subdirs_from_src_to_dst(src_scanned_sub_dir_arr, dst_scanned_sub_dir_arr, src, dst):
	directories_to_copy_to_dst_dir = set(src_scanned_sub_dir_arr) - set(dst_scanned_sub_dir_arr)
	num_sub_dirs_to_copy = len(directories_to_copy_to_dst_dir)

	if num_sub_dirs_to_copy == 0:
		print "No sub-directories to copy!"
		return

	num_sub_dirs_copied_so_far = percentage = 0

	print "Copying %i sub directories from %s to %s" % (num_sub_dirs_to_copy, src, dst)

	for sub_dir in directories_to_copy_to_dst_dir:
		abs_path = os.path.join(dst, sub_dir)
		if not os.path.exists(abs_path):
			shutil.copytree(os.path.join(src, sub_dir), abs_path, ignore=ignore_files_callback)
		
		num_sub_dirs_copied_so_far+=1
		if num_sub_dirs_copied_so_far != 0:
			prev_percentage = percentage
			percentage = int((1.0 * num_sub_dirs_copied_so_far) / num_sub_dirs_to_copy)*100
		if prev_percentage != percentage:
				if percentage % 10 == 0:
					draw_progress_bar(percentage)
	
	print ""

def copy_files_from_src_to_dst(src_scanned_dict, dst_scanned_dict, src, dst):
	files_to_copy_to_dest_dir = set(src_scanned_dict.keys()) - set(dst_scanned_dict.keys())
	num_files_to_copy = len(files_to_copy_to_dest_dir)
	if num_files_to_copy == 0:
		print "No files to copy!"
		return

	num_files_copied_so_far = percentage = 0

	print "Copying %i files from %s to %s" % (num_files_to_copy, src, dst)
	for key in files_to_copy_to_dest_dir:
		path_to_file = src_scanned_dict[key]
		ind = path_to_file.rfind(src)
		ind += len(src)
		file_rel_path = path_to_file[ind:]
		
		assert not os.path.isabs(file_rel_path)
		dstdir = os.path.join(dst, file_rel_path)

		# check if the file was already copied before trying to copy it again...could use os.path.exists but if the directory is updated right after the exists call happens then we run into problems
		try:
   			with open(dstdir): pass
		except IOError:
   			shutil.copy2(path_to_file, dstdir)
		
		copy_dir_stat(file_rel_path, src, dst)
		num_files_copied_so_far += 1
		if num_files_copied_so_far != 0:
			prev_percentage = percentage
			percentage = int((1.0 * num_files_copied_so_far) / num_files_to_copy)*100
			if prev_percentage != percentage:
					if percentage % 10 == 0:
						draw_progress_bar(percentage)
	print ""

def process_xml(file_name):
	xmldoc = minidom.parse(file_name)
	storage_paths = []
	parsed_dir_files = {}
	parsed_dir_subdirs = {}

	# parse out the paths to the storage dirs and scan the dir to compile a state of the directory
	for path in xmldoc.getElementsByTagName('storage_path'):
			string_path = path.firstChild.wholeText
			if not os.path.exists(string_path):
				sys.stderr.write("Path {0} was not found...the program will now exit\n".format(string_path))
				sys.exit(0)
			storage_paths.append(string_path)
			parsed_dir_subdirs[string_path], parsed_dir_files[string_path] = scan_dir(string_path)
	
	return (storage_paths, parsed_dir_files, parsed_dir_subdirs)

def run_hoarders():
	#Read in the the directory path
	storage_paths, parsed_dir_files, parsed_dir_subdirs = process_xml('hoarders_srv.xml')

	for path_1 in storage_paths:
		for path_2 in storage_paths:
			if not (path_1 is path_2):
				print "Syncing sub-directories from directory %s with directory %s..." % (path_2,path_1)
				copy_subdirs_from_src_to_dst(parsed_dir_subdirs[path_1], parsed_dir_subdirs[path_2], path_1, path_2)
				print "Syncing files from directory %s with directory %s..." % (path_2,path_1)
				copy_files_from_src_to_dst(parsed_dir_files[path_1], parsed_dir_files[path_2], path_1, path_2)

if __name__ == "__main__":
	run_hoarders()