#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# 
# A Python script template
#
# File:    pyplate.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:    2016-02-19
# Version: 0.2
# Python:  >=3
# License: MIT
# 
# -----------------------------------------------------------------------
#

# Imports -------------------------------------------------------------------

import sys
import os
import traceback
import logging
import argparse
from datetime import datetime, date, time


# Settings ------------------------------------------------------------------

# Application settings
AppName     = "pyplate"
AppVersion  = "0.1"
AppLicense  = "MIT"
AppAuthor   = "Peter Malmberg <peter.malmberg@gmail.com>"

# Uncomment to use logfile
#LogFile     = "pyplate.log"

# Code ----------------------------------------------------------------------



def main():
    logging.basicConfig(level=logging.DEBUG)

    # options parsing
    parser = argparse.ArgumentParser(description="C/C++ template generator")
    parser.add_argument("--helpx",   help="Print help informationt")
    parser.add_argument("--newcpp",  action="store_true", help="Create a new C++ and H file set")
    parser.add_argument("--licence", type=str,            help="Licence of new file", default="")
    parser.add_argument("--author",  type=str,            help="Author of file",      default="")
    parser.add_argument("--dir",     type=str,            help="Directory where to store file",  default=".")    
    parser.add_argument("--info",    action="store_true", help="Information about script")
    
    args = parser.parse_args()

    if args.info:
        printInfo()
        sys.exit(0)

    parser.print_help()
    sys.exit(0)


#
#
def printInfo():
    print("Script name:     " + AppName    )
    print("Script version:  " + AppVersion )
    print("Script path:     " + scriptPath )
        

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
                

