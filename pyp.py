#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# 
# Pyplate management script.
#
# File:    pyp.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:    2017-05-06
# Version: 0.1
# Python:  >=3
# Licence: MIT
# 
# -----------------------------------------------------------------------
#

# Imports -------------------------------------------------------------------

import sys
import os
import pwd
import traceback
import logging
import argparse
from datetime import datetime, date, time
import shutil

# Settings ------------------------------------------------------------------

# Application settings
AppName     = "pyp"
AppVersion  = "0.1"
AppLicence  = "MIT"
AppAuthor   = "Peter Malmberg <peter.malmnerg@gmail.com>"
AppInfo     = "Management script for pyplate."

# Installation directory for pyplate
InstallDir = "bin/pyplate"

# Uncomment to use logfile
#LogFile     = "pyplate.log"

# Code ----------------------------------------------------------------------

def installPyplate():
    print("Installing pyplate")
#    shutil.copy2("flower.jpg", "flower2.jpg")
    try: 
        shutil.copytree("nisse", "nisse2")
        shutil.copytree("nisse", InstallDir)
        
    except FileExistsError:
        pass
        
    print(getUserName())
    sys.exit(0)


def main():
    logging.basicConfig(level=logging.DEBUG)

    # options parsing
    parser = argparse.ArgumentParser(description=AppInfo)
#    parser.add_argument("--helpx",   help="Print help informationt")
    parser.add_argument("--basic",    action="store_true", help="Create a new basic python file")
    parser.add_argument("--install",  action="store_true", help="Install pyplate")    
    parser.add_argument("--info",     action="store_true", help="Information about script")
#    parser.add_argument("--license", type=str,            help="Licence of new file", default="")
#    parser.add_argument("--author",  type=str,            help="Author of file",      default="")
#    parser.add_argument("--dir",     type=str,            help="Directory where to store file",  default=".")
    
    args = parser.parse_args()
    
    if args.info:
        printInfo()
        sys.exit(0)
        
    if args.install:
        installPyplate()
        sys.exit(0)
         
        
    parser.print_help()    
    sys.exit(0)


#
#
def printInfo():
    print("Script name:     " + AppName    )
    print("Script version:  " + AppVersion )
    print("Script path:     " + scriptPath )
    print("Script author:   " + AppAuthor  )
    print("Script info:     " + AppInfo    )


#
#
def query_list(question, db, default="yes"):
    prompt = " >"
    
    while 1:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        print(choice)
        for x in db:
            if (x.lower()==choice):
                return x
            
            print("\nPlease resplond with: ")
            for c in db:
                print("  "+c)
                

#
#
def query_yn(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


#
# Absolute path to script itself        
#
scriptPath = os.path.abspath(os.path.dirname(sys.argv[0]))

# Find username of caller
def getUserName():
    return pwd.getpwuid( os.getuid() )[ 0 ]

#
# 
if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt as e: # Ctrl-C
        raise e
    except SystemExit as e:        # sys.exit()
        raise e
    except Exception as e:
        print('ERROR, UNEXPECTED EXCEPTION')
        print(str(e))
        traceback.print_exc()
        os._exit(1)
                

