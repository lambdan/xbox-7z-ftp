# pip3 install pyunpack patool
# usage: xbox7zftp.py game.7z
# Tested with XBMC4Gamers and Windows 11 on HDD ready pack, 2022-08-11

# xbox settings, change these if you need to !!!!
xbox_ip = '10.0.0.44'
xbox_user = 'xbox'
xbox_password = 'xbox'
xbox_path = '/G/games/'
#################################################

from ftplib import FTP
from pyunpack import Archive
import tempfile, shutil, os, random, sys, time, math

folder_size = 0
folder_files = 0
total_uploaded = 0
files_uploaded = 0
current_path = []

# ftp upload function from https://stackoverflow.com/a/27299745
def uploadThis(path):
	global folder_size
	global folder_files

	global files_uploaded
	global total_uploaded
	
	global current_path

	files = os.listdir(path)
	os.chdir(path)
	current_path.append(path)

	for f in files:
		if os.path.isfile(f):
			filesize = os.path.getsize(f)

			
			print("Uploading", "/".join(current_path[1:]) + "/" + f, "(" + prettySize(filesize) + ")", end="... ", flush=True)

			with open(f,'rb') as fh:
				myFTP.storbinary('STOR %s' % f, fh)

			files_uploaded += 1
			total_uploaded += filesize
			
			#size_progress = "[" + prettySize(total_uploaded) + "/" + prettySize(folder_size) + "]"
			#files_progress = "[" + str(files_uploaded) + "/" + str(folder_files) + " files]"
			#total_progress = "[" + percentage(total_uploaded, folder_size) + " " + percentage(files_uploaded, folder_files) + "]"
			progress = percentage(total_uploaded+files_uploaded, folder_size+folder_files) + " (" + prettySize(total_uploaded) + "/" + prettySize(folder_size) + ", " + str(files_uploaded) + "/" + str(folder_files) + " files)"
			# this is kinda weird but its so we end up with 100% at the end
			print("OK\n", progress, end=" ", flush=True)

		elif os.path.isdir(f):	
			#print("Making dir", f)
			myFTP.mkd(f)
			myFTP.cwd(f)
			uploadThis(f)

	myFTP.cwd('..')
	os.chdir('..')
	current_path.pop() # remove last path from current_path

def folderStats(path):
	size = 0
	filecount = 0
	for path, dirs, files in os.walk(path):
		for f in files:
			filecount += 1
			fp = os.path.join(path, f)
			size += os.path.getsize(fp)
	return size, filecount

def prettySize(z):
	KB = z/1024
	MB = z/(1024*1024)
	GB = z/(1024*1024*1024)
	if GB >= 1:
		return str( round(GB, 1) ) + " GB"
	elif MB >= 1:
		return str( round(MB, 1) ) + " MB"
	elif KB >= 1:
		return str( round(KB, 1) ) + " KB"
	else:
		return str(z) + " B" # bytes

def percentage(part, whole):
	return str( math.floor( (part/whole) * 100) ) + "%"

# get input file
try:
	infile = sys.argv[1]
except IndexError:
	print ("usage:", sys.argv[0], "game.7z")
	print ("Edit the script to change ip, username, password, etc...")
	sys.exit(1)

if not os.path.isfile(infile):
	print("Error, not a file:", infile)
	sys.exit(1)

print("Destination:", xbox_ip, xbox_path)
print("Processing", infile)

# create temp folder to store extracted files in
temp_folder = tempfile.mkdtemp()
print ("Temp folder:", temp_folder)

# extract
print ("Unzipping to temp folder...", end="", flush=True)
Archive(infile).extractall(temp_folder)
print ("OK")



print ("Checking size of game...", end="", flush=True)
folder_size, folder_files = folderStats(temp_folder)
print(" it's " + prettySize(folder_size) + " and has " + str(folder_files) + " files.")

# upload over ftp
print ("Starting FTP upload:")
myFTP = FTP(xbox_ip, xbox_user, xbox_password)
myFTP.cwd(xbox_path) # cd to xbox_path on the xbox

# if game is not in its own folder, make a folder for it 
if os.path.isfile(os.path.join(temp_folder, "default.xbe")):
	print("default.xbe detected in root of temp folder. We need to make a folder for the game.")
	game_name = input("Enter game folder name: ")
	myFTP.mkd(game_name)
	myFTP.cwd(game_name)

time_started = time.time()
try:
	uploadThis(temp_folder)
except:
	print("Error occurred during upload! Deleting temp folder and then exiting.")
	shutil.rmtree(temp_folder)
	sys.exit(1)

time_done = time.time()
print ("All files uploaded!")

time_taken = time_done - time_started
speed = total_uploaded/time_taken
print("Uploaded", prettySize(total_uploaded), "in", int(time_taken), "seconds", "(" + str(round(speed/(1024*1024), 1)) + " MB/s)")

# remove temp folder
print ("Deleting temp folder...", end="", flush=True)
shutil.rmtree(temp_folder)
print(" OK")

print ("All done :)")