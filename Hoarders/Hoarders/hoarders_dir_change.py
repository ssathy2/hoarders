import shutil
import sys
import os

from hoarders_srv import process_xml

# basically take the files modified from stdin separated by newlines and return them...this call should be made only once
def get_modified_files_from_stdin():
	lines = []
	for line in sys.stdin:
  		stripped = line.strip()
  		if not stripped: break
  		lines.append(stripped)

  	return lines;

"""
Hoarders_Dir:
/Users/siddharthsathyam/Documents/Resumes

Modified:
/Users/siddharthsathyam/Documents/Resumes/r1/h1/res112012.pdf

Storage Paths:
/Users/siddharthsathyam/Dropbox/
/Users/siddharthsathyam/Google_Drive/
/Users/siddharthsathyam/Skydrive_slim/
"""
def get_suffix_from_file_modified(hoarders_paths, file_modified):
	for hoarders_path in hoarders_paths:
		if hoarders_path in file_modified:
			return hoarders_path

def main():
	# the first arg to the program contains the path to the xml
	if(len(sys.argv) is not 2):
		print "Invalid commands to hoarders_dir_change.py"
		sys.exit()
	
	# get the storage paths and global_hoarders_path from xml
	hoarders_xml_path = sys.argv[1]
	
	print "Hoarders XML File at: %s" % (hoarders_xml_path)
	storage_paths, global_hoarders_paths = process_xml(hoarders_xml_path)

	# get the files that were modded by calling get_files_from_stdin
	files_modified = get_modified_files_from_stdin()
	print "Files modified: "
	print files_modified
	if(len(files_modified) != 0):
		for file_modified in files_modified:
			print file_modified
			suffix = get_suffix_from_file_modified(global_hoarders_paths, file_modified)
			print suffix
			"""for storage_path in storage_paths:
				storage_hoarders_path = os.path.join(storage_path, 'hoarders')
				if(!os.path.exists(file_modified)):
					os.mkdir(file_modified)
				shutil.copy2(file_modified, storage_hoarders_path)
				print "File: %s copied to %s" % (files_modified, storage_hoarders_path)"""
				

if __name__ == '__main__':
	main()