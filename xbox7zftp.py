# usage: xbox7zftp.py game.7z

# xbox settings
xbox_ip = '10.0.0.36'
xbox_user = 'xbox'
xbox_password = 'xbox'
xbox_path = '/G/Games/'
block_size = 262144

# imports
from ftplib import FTP
from pyunpack import Archive
from tqdm import tqdm
import tempfile, shutil, os, random, sys

def updatePbars():
	filebar.update(1)
	pbarSize.update(block_size)

# ftp upload function from https://stackoverflow.com/a/27299745
def uploadThis(path):
	files = os.listdir(path)
	os.chdir(path)
	for f in files:
		if os.path.isfile(f):
			filebar.reset(total=os.path.getsize(f))
			filebar.set_description("Uploading %s" % f)
			fh = open(f,'rb')
			myFTP.storbinary('STOR %s' % f, fh, block_size, updatePbars())
			fh.close()
		elif os.path.isdir(f):
			myFTP.mkd(f)
			myFTP.cwd(f)
			uploadThis(f)
		pbar.update(1)
	myFTP.cwd('..')
	os.chdir('..')

# get input file
try:
	infile = sys.argv[1]
except IndexError:
	print ("usage: xbox7zftp.py game.7z")
	sys.exit(1)

if not os.path.isfile(infile):
	print("not a file:", infile)
	sys.exit(1)

# create temp folder to store extracted files in
temp_folder = os.path.join(tempfile.gettempdir(), "xbox7zftp" + str(random.randint(1,10000)))
print ("Temp folder:", temp_folder)
os.mkdir(temp_folder)

# extract
print ("Unpacking", infile)
Archive(infile).extractall(temp_folder)

# count files and folders in the folder (for progress bar)
print ("Counting files...")
total_files = sum([len(files) for r, d, files in os.walk(temp_folder)])
total_files += sum([len(d) for r, d, files in os.walk(temp_folder)])

# directory size
print ("Size...")
total_size = 0
for path, dirs, files in os.walk(temp_folder):
	for f in files:
		fp = os.path.join(path, f)
		total_size += os.path.getsize(fp)

# upload over ftp
print ("Starting FTP upload...")
myFTP = FTP(xbox_ip, xbox_user, xbox_password)
myFTP.cwd(xbox_path) # cd to xbox_path on the xbox

filebar = tqdm()
pbar = tqdm(total=total_files) # set up progress bar
pbar.set_description("Total progress (files)")
pbarSize = tqdm(total=total_size)
pbarSize.set_description("Total progress (size)")

uploadThis(temp_folder)

filebar.close()
pbar.close()
pbarSize.close()
print ("Done with FTP upload")

# remove temp folder
print ("Removing temp folder", temp_folder)
shutil.rmtree(temp_folder)

print ("All done!")