# MacLogic

# Documentation
This is a pair of Python scripts for forensic logical copy of macOS.
A version for Python 2.x and another for Python 3.x.
In MacOS Ventura Apple removed Python from the default installed software.
A all-in-one binary of the original python scripts is now available for both x86 and ARM CPUs.

The source scripts are still available.

# Build from source
You can build your own binaries using Brew and PyInstaller.
* A shell script for installing Brew is available at brew.sh
* Then you will need to install PyInstaller : brew install pyinstaller
* You can now run the command : pyinstaller --onefile <script.py>
replace <script.py> with the appropriate file name (logic_v2.py for python 2.x, logic_v3.py for python 3.x)

# Usage
Run the program : 
* sudo logic_x86
or 
* sudo logic_arm

If you don't have access to the sudo command, you can still run it without. It will copy less data.

It will ask for the target mounted drive located in /Volumes
Then you have to input the named of the container (ie. the name of the backup)
You can choose between APFS and HFS+. It is reommanded to use the same file system as the one you are going to copy.
The default items that are going to be copied or not are then prompted to you.
You can also input a custom path.

The program will then estimate the amount of data to copy and create a container accordingly.
At the end of the copy process the SHA1 hash of the container is computed.
A log file of the process is also created.

The program uses custom builds of rsync for both architectures located in the ./bin subdirectory

# Notes
The x86 release is based upon the Python 2.x version of the script.
The ARM release is based upon the Python 3.x version of the script.

The x86 version as been tested on MacOS High Sierra.
The ARM version as been tested on MacOS Ventura.

Using the binaries is recommanded.