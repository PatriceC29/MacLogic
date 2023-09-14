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