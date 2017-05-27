#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# 
# Pyplate basic example.
#
# File:    pyplate-basic.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:    2016-02-19
# Version: 0.2
# Python:  >=3
# Licence: MIT
# 
# -----------------------------------------------------------------------
#

# Imports -------------------------------------------------------------------

import sys
import os
import traceback
from datetime import datetime, date, time


# Settings ------------------------------------------------------------------


# Code ----------------------------------------------------------------------

def main():
    print("Pyplate basic example.")
    sys.exit(0);



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
                

