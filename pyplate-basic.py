#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# 
# __DESC__
#
# File:    __NAME__.py
# Author:  __AUTHOR__
# Date:    __DATE__
# License: __LICENSE__
# Python:  >=3
# 
# -----------------------------------------------------------------------
# This file is generated from pyplate Python template generator.
# Pyplate is developed by
# Peter Malmberg <peter.malmberg@gmail.com>
#

# Imports -------------------------------------------------------------------

import sys
import os
import traceback
from datetime import datetime, date, time

# Settings ------------------------------------------------------------------


# Code ----------------------------------------------------------------------

def main():
    print("Pyplate basic template.")
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
                
