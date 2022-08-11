Python script to make it easier to transfer Xbox games that are zipped up (like the HDD Ready packs...) by automatically unzipping, FTP'ing it over, and then removing the unzipped files.

## Features

- Automatically unzips archives (`.7z` and `.zip` tested)
- Removes unzipped files after they've been transfered
- Prevents transfering game root straight to Games folder root
	- (Basically makes sure you always have `/F/Games/game/default.xbe` instead of accidentally getting (`/F/Games/default.xbe`)

## Caveats

- Not great at error handling
- Single threaded transfer. Makes it very slow for games with thousands of files.

## Usage

- Download the `xbox7zftp.py` script and put it somewhere
- Install prereqs: `pip3 install pyunpack patool`
- Edit Xbox settings at top of the script (IP, username, path, etc)
- Run `python xbox7zftp.py game.7z` and wait :)

Tested with Xbox running XBMC4Gamers and Windows 11 PC with Python 3.10.5 but I don't see any reason why it wouldn't work on other OSes or Xbox Dashboards.

![Screenshot](https://djsimg.org/sPcV.png)