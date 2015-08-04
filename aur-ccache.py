#!/usr/bin/python
#Remove all cached AUR packages other than the ones installed
#By Charles Bos

from subprocess import Popen, PIPE
import os
import sys

def usage() :
    print('''Usage:
  aur-ccache.py <path to cache> <options>
  Note: without the path to cache argument, the path is taken to be ~/.aurcache

  Options:
    -h, --help: print this dialog
    --dry-run: show packages to be deleted but do not delete them''')

# Get cache directory
args = sys.argv
if (len(args) > 1) and (args[1] != "--dry-run") :
    if (args[1] == '-h') or (args[1] == '--help') :
        usage()
        os._exit(0)
    elif os.path.exists(args[1]) : cacheDir = args[1]
    else :
        usage()
        os._exit(0)
elif os.path.exists(os.path.expanduser('~') + "/.aurcache") : cacheDir = os.path.expanduser('~') + "/.aurcache"
else :
    usage()
    os._exit(0)

#Get package list in cache
cachePkgs = os.listdir(cacheDir)

#Get installed AUR package list
instOutput = Popen(["pacman", "-Qmi"], stdout = PIPE).communicate()
instOutput = (str(instOutput).replace("\\n", " ").replace("b\'", "").replace("\', None", "").strip("()").rstrip(" ")).split(" ")
instOutput = [x for x in instOutput if (x != "") and (x != ":")]

name = []
version = []
arch = []
instPkgs = []

counter = 0
while counter < len(instOutput) :
    if instOutput[counter] == "Name" : name.append(instOutput[counter + 1])
    elif instOutput[counter] == "Version" : version.append(instOutput[counter + 1])
    elif instOutput[counter] == "Architecture" : arch.append(instOutput[counter + 1])
    counter += 1

#Exit if package info extraction failed
if not (len(name) == len(version) == len(arch)) :
    print("Error getting names of installed packages.")
    os._exit(0)

counter = 0
while counter < len(name) :
    pkgName = name[counter] + "-" + version[counter] + "-" + arch[counter] + ".pkg.tar.xz"
    instPkgs.append(pkgName)
    counter += 1

#Check cache packages against installed ones
oldPkgs = []
for x in cachePkgs :
    if x not in instPkgs : oldPkgs.append(x)

#Show packages to be removed if --dry-run. Remove them if not --dry-run
if "--dry-run" in args :
    if len(oldPkgs) > 0 :
        print("Files to be removed:\n-----")
        for x in oldPkgs : print(x)
    else : print("No files to be removed.")
else :
    if len(oldPkgs) > 0 :
        for x in oldPkgs :
            print("Removing: " + x)
            os.remove(cacheDir + "/" + x)
        print("\nAll old files removed!")
    else : print("No files to be removed.")