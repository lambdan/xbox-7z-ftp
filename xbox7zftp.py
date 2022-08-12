# pip3 install pyunpack patool tqdm
# usage: xbox7zftp.py game.7z
# Tested with XBMC4Gamers and Windows 11 on HDD ready pack, 2022-08-12


# xbox settings, change these if you need to !!!!

xbox_ip = '10.0.0.44'
xbox_user = 'xbox'
xbox_password = 'xbox'
xbox_path = '/F/games/'

#################################################
#################################################

from ftplib import FTP
from tqdm import tqdm
from pyunpack import Archive
import tempfile, shutil, os, random, sys

bs = 1000
maxBS = 102400

xbox_free_space = False
xbox_drive = False

# ftp upload function from https://stackoverflow.com/a/27299745
def uploadThis(path):
	global bs

	files = os.listdir(path)
	os.chdir(path)
	
	for f in files:
		if os.path.isfile(f):
			
			# dynamic blocksize based on filesize
			fs = os.path.getsize(f)
			if fs > maxBS:
				bs = maxBS
			else:
				bs = fs

			with open(f,'rb') as fh:
				myFTP.storbinary('STOR %s' % f, fh, blocksize=bs, callback=blockTransfered)
		
		elif os.path.isdir(f):	
			myFTP.mkd(f)
			myFTP.cwd(f)
			uploadThis(f)

	myFTP.cwd('..')
	os.chdir('..')

def blockTransfered(block): # updates the progress bar
	global pbar
	global bs
	pbar.update(bs)

def folderStats(path):
	size = 0
	filecount = 0
	for path, dirs, files in os.walk(path):
		for f in files:
			filecount += 1
			fp = os.path.join(path, f)
			size += os.path.getsize(fp)
	return size, filecount

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
print("Game:", infile)
print()

# Test xbox connection
print("Testing FTP connection to Xbox...", end=" ", flush=True)
try:
	myFTP = FTP(xbox_ip, xbox_user, xbox_password, timeout=3)
	print("ok")
except Exception as e:
	print()
	print("FTP error:", e, "Exiting...")
	sys.exit(1)

# create temp folder to store extracted files in
temp_folder = tempfile.mkdtemp()

# extract
print ("Unzipping game to temp folder...")
Archive(infile).extractall(temp_folder)

# get folder size and file count
folder_size, folder_files = folderStats(temp_folder)

# cd on server (xbox) to games folder
myFTP.cwd(xbox_path) 

# if game is not in its own folder, make a folder for it 
if os.path.isfile(os.path.join(temp_folder, "default.xbe")):
	print("default.xbe detected in root of temp folder. We need to make a folder for the game.")
	game_name = input("Enter name for game folder: ")
	myFTP.mkd(game_name)
	myFTP.cwd(game_name)


print ("Starting FTP transfer")

pbar = tqdm(total=folder_size, unit="B", unit_scale=True, unit_divisor=1024)

try:
	uploadThis(temp_folder)
except Exception as e:
	print("Error occurred during FTP transfer!")
	print("Error message:", e)
	myFTP.quit()
	input("Press any key to exit")
	sys.exit(1)

pbar.close()
myFTP.quit()
print ("FTP complete!")

# remove temp folder
print ("Deleting temp folder...")
shutil.rmtree(temp_folder)

print ("All done :)")