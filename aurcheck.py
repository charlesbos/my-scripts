#!/usr/bin/python
#A simple script to check for AUR package updates
#By Charles Bos

from subprocess import Popen, PIPE
from bs4 import BeautifulSoup
import requests
import os

print("Checking...")

aurPkgs = Popen(["pacman", "-Qm"], stdout = PIPE).communicate()
aurPkgs = (str(aurPkgs).replace("\\n", " ").replace("b\'", "").replace("\', None", "").strip("()").rstrip(" ")).split(" ")

counter = 0
while counter < len(aurPkgs) - 1 :
    aurPkgs[counter] = (aurPkgs[counter], aurPkgs[counter + 1])
    del aurPkgs[counter + 1]
    counter += 1
    
try :
    updates = []
    mismatches = []
    failures = []
    aurUrl = "https://aur4.archlinux.org/packages/"
    
    for x in aurPkgs:
        #Check for unmigrated packages first (will be removed when AUR4 replaces AUR3)
        response = requests.get("https://aur4.archlinux.org/cgit/aur.git/log/?h=" + x[0])
        logPage = str(BeautifulSoup(response.content))
        if logPage.find("Invalid branch: " + x[0]) != -1 :
            failures.append(x[0])
            continue
        response = requests.get(aurUrl + x[0])
        page = str(BeautifulSoup(response.content))
        start = page.find("<h2>Package Details: ")
        if start == -1 : failures.append(x[0])
        else :
            end = page.find("</h2>", start)
            version = page[start + 21:end].split(" ")[1]
            if x[1] < version : updates.append(str(x[0] + " " +x[1] + " --> " + version))
            elif x[1] > version : mismatches.append(str(x[0] + " " +x[1] + " --> " + version))  

    if updates == mismatches == failures == [] : print("\nEverything is up to date.")
    else :
        if failures != [] :
            print("\nThe following packages were not found in the AUR:\n-----")
            for x in failures : print(x)
        if mismatches != [] :
            print("\nThe following local packages are more recent than their AUR versions:\n-----")
            for x in mismatches : print(x)
        if updates != [] :
            print("\nThe following packages have updates available:\n-----")
            for x in updates : print(x)
            fetch = input("\nFetch updated tarballs? [y/n] ")
            if fetch == "y" :
                if os.path.exists(os.path.expanduser('~') + "/Downloads") : downloadsDir = os.path.expanduser('~') + "/Downloads"
                else : downloadsDir = os.path.expanduser('~')
                for x in updates :
                    newPkg = x.split(' ')[0]
                    print("Fetching: " + newPkg + ".tar.gz")
                    pkgUrl = "https://aur4.archlinux.org/cgit/aur.git/snapshot/" + newPkg + ".tar.gz"
                    Popen(["wget", "-q", pkgUrl, "-P", downloadsDir]).wait()
                print("\nTarballs have been downloaded. Check: " + downloadsDir)    
except requests.ConnectionError :
    print("Error. Connection to network failed.")
