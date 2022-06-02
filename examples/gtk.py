#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# 
# Example of gtk bindings.
#
# File:    gtk.py
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
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


# Code ----------------------------------------------------------------------

def main():
    window = Gtk.Window(title="Hello World")
    window.show()
    window.connect("delete-event", Gtk.main_quit)
    Gtk.main()



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
                

