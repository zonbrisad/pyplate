#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#
# Python template generator
#
# File:    ctemplate.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:    2016-02-19
# Version: 0.3
# Python:  >=3
# Licence: MIT
#
# ---------------------------------------------------------------------------

# History -------------------------------------------------------------------
# - Ver 0.3
# Major rewrite for better code generation
#

# Todo ----------------------------------------------------------------------
#

# Imports -------------------------------------------------------------------

from dataclasses import dataclass
from enum import Enum, auto
import sys
import os
import traceback
import logging
import argparse
import shutil
from  pathlib import Path
from datetime import datetime, date, time


# Settings ------------------------------------------------------------------

AppName     = "mptemplate"
AppVersion  = "0.3"
AppLicense  = "MIT"
AppAuthor   = "Peter Malmberg <peter.malmberg@gmail.com>"

# Uncomment to use logfile
#LogFile     = "pyplate.log"

src_preamble="""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

src_header = """
#----------------------------------------------------------------------------
# 
# __DESC__
#
# File:    __NAME__.py
# Author:  __AUTHOR__
# Date:    __DATE__
# License: __LICENSE__
# Python:  >= 3.0
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
"""

src_main = """
def main():
    pass


if __name__ == "__main__":
    main()
"""

src_main_extra = """
def main():
    pass


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
        os._exit(1)§
"""


# Code ----------------------------------------------------------------------


@dataclass
class TConf:
    """Template configuration class"""
    name: str = ""
    main: bool = False
    author: str = ""
    brief: str = ""
    date: str = ""
    module_name: str = ""

    email: str = ""
    license: str = ""
    org: str = ""
    author: str = ""
    separators: bool = True

    def __init__(self):
        self.date = datetime.now().strftime("%Y-%m-%d")


class template(object):
    """docstring for template."""
    
    def __init__(self, conf: TConf):
        super(template, self).__init__()
        # self.arg = arg
        self.text = ""
        self.header = ""
        self.imports = ""
        self.filename = ""
        self.modulename = ""

        self.conf = conf

    def add(self, text):
        self.text += text

    def addPreamble(self):
        self.add(src_preamble)

    def addHeader(self):
        self.add(src_header)
        
    def addImport(self, imp):
        pass

    def addSeparator(self):
        pass

    def addMain(self):
        self.add(src_main)

    def write(self):
        pass

    def generate(self):
        self.text = ""

        self.addPreamble()
        self.addHeader()
        self.addMain()
        
    def print(self):
        print(self.text)
    
    def write(self):
        with open(filename, "w") as file:
            file.write("")
            file.close()


def printInfo():
    print("Script name    " + AppName)
    print("Script version " + AppVersion)
    print("Script path    " + os.path.realpath(__file__))

# Absolute path to script itself
scriptPath = os.path.abspath(os.path.dirname(sys.argv[0]))
mpPath     = scriptPath+"/.."

def main() -> None:

    conf = TConf()

    t = template()
    t.generate()
    t.print()

    logging.basicConfig(level=logging.DEBUG)

    parrent_parser = argparse.ArgumentParser(add_help=False)
    parrent_parser.add_argument("--name", type=str, help="Name of C/C++ module", default="")
    parrent_parser.add_argument("--brief", type=str, help="Brief description", default="")
    parrent_parser.add_argument("--author", type=str, help="Author of file", default=conf.name+" <"+conf.email+">")
    parrent_parser.add_argument("--license", type=str, help="License of new file", default=conf.license)

    parrent_parser.add_argument("--main", action="store_true", help="Add main function block", default=False)
    parrent_parser.add_argument("--header", action="store_true", help="External header file", default=False)

    parrent_parser.add_argument("--dir", type=str, help="Project source directory", default=".")
    parrent_parser.add_argument("--basedir", type=str, help="Project directory", default=".")

    # options parsing
    parser = argparse.ArgumentParser(
            prog=AppName+'.py',
            description="Pyplate python template generator",
            epilog="",
            parents=[parrent_parser],
        )

    parser.add_argument("--version", action='version', help="Directory where to store file", version=AppVersion)

    subparsers = parser.add_subparsers(help="")
    parser_newc = subparsers.add_parser("new", parents=[parrent_parser], help="Create a new python file")
    parser_newc = subparsers.add_parser("newm", parents=[parrent_parser], help="Create a new python module")

   #parser_newc.set_defaults(func=cmd_newc)
    # parser_newclass = subparsers.add_parser("newclass", parents=[parrent_parser],   help="Create a new C++ class")
    # parser_newclass.set_defaults(func=cmd_newclass)
    # parser_newcpp = subparsers.add_parser("newcpp", parents=[parrent_parser],  help="Create a new C++ file")
    # parser_newcpp.set_defaults(func=cmd_newcpp)
    # parser_qtdia = subparsers.add_parser("giti",    parents=[parrent_parser],  help="Create .gitignore file")
    # parser_qtdia.set_defaults(func=cmd_giti)

#    parser.add_argument("--header",   type=str,            help="External header file",  default="headerExample")
#    subparsers = parser.add_subparsers(title='subcommands', help="sfda fdsa fdsa afsd")

    args = parser.parse_args()
    # if hasattr(args, 'author'):
    #     conf.author  = args.author
    # if hasattr(args, 'license'):
    #     conf.license = args.license
    # if hasattr(args, 'name'):
    #     conf.moduleName = args.name
    # if hasattr(args, 'brief'):
    #     conf.brief = args.brief
    # if hasattr(args, 'basedir'):
    #     conf.basedir = args.basedir

    # if hasattr(args, 'func'):
    #     args.func(args, conf)
    #     exit(0)

    parser.print_help()
    exit(0)


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

