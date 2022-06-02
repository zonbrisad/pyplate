#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# 
# asdf asdf asdf
#
# File:    basic.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:    2022-05-25
# License: MIT
# Python:  3
# 
#----------------------------------------------------------------------------
# Pyplate
#   This file is generated from pyplate Python template generator.
#
# Pyplate is developed by:
#   Peter Malmberg <peter.malmberg@gmail.com>
#
# Available at:
#   https://github.com/zobrisad/pyplate.git
# 
# ---------------------------------------------------------------------------
#
# Imports -------------------------------------------------------------------
import sys
import os
import traceback

# Code ----------------------------------------------------------------------

def main():
    print("Basic python project")


# Main program handle 
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
                

