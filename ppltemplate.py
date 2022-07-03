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
# License: MIT
#
# ---------------------------------------------------------------------------

# History -------------------------------------------------------------------
# - Ver 0.3
# Major rewrite for better code generation
#

# Todo ----------------------------------------------------------------------
#

# Imports -------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass
import sys
import os
import traceback
import logging
import argparse
from datetime import datetime
import query

# Settings ------------------------------------------------------------------

AppName = "mptemplate"
AppVersion = "0.3"
AppLicense = "MIT"
AppAuthor = "Peter Malmberg <peter.malmberg@gmail.com>"


# Uncomment to use logfile
# LogFile     = "pyplate.log"

# Absolute path to script itself
scriptPath = os.path.abspath(os.path.dirname(sys.argv[0]))
mpPath = scriptPath + "/.."


# Code ----------------------------------------------------------------------


@dataclass
class TemplateX:
    text: str = ""
    preamble_text: str = ""
    header_text: str = ""
    imports_text: str = ""
    variables_text: str = ""
    code_text: str = ""
    main_func_text: str = ""
    main_text: str = ""

    def add(self, a: TemplateX):
        self.preamble_text += a.preamble_text
        self.header_text += a.header_text
        self.imports_text += a.imports_text
        self.variables_text += a.variables_text
        self.code_text += a.code_text
        self.main_func_text += a.main_func_text
        self.main_text += a.main_text


@dataclass
class TConf:
    """Template configuration class"""
    name: str = ""
    author: str = ""
    description: str = ""
    date: str = ""
    email: str = ""
    license: str = ""
    org: str = ""
    # header: str = ""

    has_preamble: bool = True
    has_header: bool = True
    has_main: bool = False
    has_main_application: bool = False
    has_separators: bool = False

    def __init__(self, args: argparse.ArgumentParser) -> None:
        self.args = args
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.has_main = self.args.main
        self.has_separators = self.args.separators

        self.set_attribute("name", "Enter module name")
        self.set_attribute("description", "Enter brief description")
        self.set_attribute("author", "Enter name of author")
        self.set_attribute("email", "Enter email of author")

        # if external header, read into var
        if self.args.header is not None:
            self.header = TemplateX()
            with self.args.header as f:
                self.header.header_text = f.read()
        else:
            self.header = t_header

    def set_attribute(self, attribute: str, question: str):
        if getattr(self.args, attribute) is not None:
            setattr(self, attribute, getattr(self.args, attribute))
        else:
            setattr(self, attribute, query.query_string(question, ""))


t_preamble = TemplateX(
    preamble_text="""\
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
)

t_header = TemplateX(
    header_text="""\
# ----------------------------------------------------------------------------
#
# __BRIEF__
#
# File:     __NAME__
# Author:   __AUTHOR__  __EMAIL__
# Date:     __DATE__
# License:  __LICENSE__
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------
"""
)

t_main = TemplateX(
    main_text="""\
if __name__ == "__main__":
    main()
"""
)

t_main_application = TemplateX(
    imports_text="""\
import traceback
import os
import sys
""",
    main_text="""\
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
"""
)

t_application = TemplateX(
    variables_text="""\
app_name = "__NAME__"
app_version = "0.1"
app_license = "X"
app_author = "__AUTHOR__  __EMAIL__"
app_description = "__DESCRIPTION__"
"""
)

t_argtable = TemplateX(
    imports_text="""\
import argparse
""",
    main_func_text="""\
    parser = argparse.ArgumentParser(
        prog=app_name,
        description=app_description,
        epilog="",
        add_help=True)
    parser.add_argument("--name",
                        type=str,
                        help="Name of Python module",
                        default="")
    parser.add_argument("--brief",
                        type=str,
                        help="Brief description",
                        default="")
    parser.add_argument("--main",
                        action="store_true",
                        help="Add main function block",
                        default=False)
    parser.add_argument("--header",
                        action="store_true",
                        help="Include header",
                        default=False)
    parser.add_argument("--version",
                        action="version",
                        help="Print version information",
                        version=f"{app_name} {app_version}")


    args = parser.parse_args()
    parser.print_help()
"""
)


t_logging = TemplateX(
    imports_text="""\
import logging
""",
    main_func_text="""\
    logging.basicConfig
"""
)


t_qt5 = TemplateX(
    imports_text="""\
from Qt5 import
""",
    variables_text="""
""",
    main_func_text="""
"""
)


class Template(TemplateX):
    """docstring for template."""

    def __init__(self, conf: TConf):
        super().__init__()
        self.conf = conf

    def clear(self):
        self.text = ""

    def replace(self, old: str, new: str):
        self.text = self.text.replace(old, new)

    def add_separator(self, header):
        if self.conf.has_separators:
            self.text += f"\n# {header} {'-'*(75-len(header))}\n\n\n"
        # else:
        #     self.text += "\n\n"

    def generate(self):
        self.clear()

        if self.conf.has_preamble:
            self.add(t_preamble)

        if self.conf.has_header:
            self.add(self.conf.header)

        if self.conf.has_main_application:
            self.add(t_main_application)
        elif self.conf.has_main:
            self.add(t_main)

        self.text += self.preamble_text
        self.text += self.header_text
        self.add_separator("Imports")
        self.text += self.imports_text
        self.add_separator("Variables")
        self.text += self.variables_text
        self.add_separator("Code")

        if self.conf.has_main or self.conf.has_main_application:
            self.text += "def main():\n"
            if self.main_func_text == "":
                self.text += "    pass"
            else:
                self.text += self.main_func_text
            self.text += "\n\n"
            self.text += self.main_text

        self.replace("__NAME__", self.conf.name)
        self.replace("__DESCRIPTION__", self.conf.description)
        self.replace("__AUTHOR__", self.conf.author)

        if self.conf.email == "":
            self.replace("__EMAIL__", "")
        else:
            self.replace("__EMAIL__", f"<{self.conf.email}>")

        self.replace("__DATE__", self.conf.date)
        self.replace("__LICENSE__", self.conf.license)

    def write(self):
        with open(self.conf.name, "w") as file:
            file.write(self.text)
        os.chmod(self.conf.name, 0o770)

    def __str__(self) -> str:
        return self.text


def print_info():
    print("Script name    " + AppName)
    print("Script version " + AppVersion)
    print("Script path    " + os.path.realpath(__file__))


def cmd_new(args):
    conf = TConf(args)
    conf.has_main = True

    t = Template(conf)
    t.generate()
    #print(t)
    t.write()


def cmd_newa(args):
    conf = TConf(args)
    conf.has_main = False
    conf.has_main_application = True
    conf.has_separators = True

    t = Template(conf)
    t.add(t_application)
    if query.query_bool("Include argparse?", default="yes"):
        t.add(t_argtable)
    t.generate()
    t.write()
    if args.debug:
        print(t)


def cmd_newm(args):
    conf = TConf(args)
    conf.has_main = False
    conf.has_main_application = False

    t = Template(conf)
    t.generate()
    t.write()


def main() -> None:

    logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s]%(asctime)s %(message)s")
    # logging.debug("Hello")

    parrent_parser = argparse.ArgumentParser(add_help=False)
    parrent_parser.add_argument("--name",
                                type=str,
                                help="Name of Python module"
                                )
    parrent_parser.add_argument("--description",
                                type=str,
                                help="Brief description"
                                )
    parrent_parser.add_argument("--author",
                                type=str,
                                help="Author of file"
                                )
    parrent_parser.add_argument("--email",
                                type=str,
                                help="Email of author of file"
                                )
    # parrent_parser.add_argument("--license",
    #                             type=str,
    #                             help="License of new file",
    #                             default=conf.license)

    parrent_parser.add_argument("--main",
                                action="store_true",
                                help="Add main function block",
                                default=False)
    parrent_parser.add_argument("--header",
                                type=argparse.FileType("r"),
                                help="Include external header"
                                )
    parrent_parser.add_argument("--dir",
                                type=str,
                                help="Project source directory",
                                default=".")
    parrent_parser.add_argument("--basedir",
                                type=str,
                                help="Project directory",
                                default=".")
    parrent_parser.add_argument("--write",
                                action="store_true",
                                help="Write file to disk",
                                default=False)
    parrent_parser.add_argument("--printheader",
                                action="store_true",
                                help="Print default header to stdout",
                                default=False)
    parrent_parser.add_argument("--separators",
                                action="store_true",
                                help="Add code separators",
                                default=False)
#    parrent_parser.add_argument("--outfile",
#                                type=argparse.FileType("w",0),
#                                help="Write template to file")
    parrent_parser.add_argument("--debug",
                                action="store_true",
                                help="Print debug information")
    parrent_parser.add_argument("--version",
                                action="version",
                                help="Print application version",
                                version=AppVersion)

    # options parsing
    parser = argparse.ArgumentParser(
            prog=AppName,
            description="Pyplate python template generator",
            epilog="Pyplate <https://github.com/zonbrisad/pyplate.git>",
            parents=[parrent_parser],
        )

    subparsers = parser.add_subparsers(help="")
    parser_new = subparsers.add_parser("new",
                                       parents=[parrent_parser],
                                       help="Create a new python file")
    parser_new.set_defaults(func=cmd_new)
    parser_new = subparsers.add_parser("newm",
                                       parents=[parrent_parser],
                                       help="Create a new minimal python file without main")
    parser_new.set_defaults(func=cmd_newm)
    parser_new = subparsers.add_parser("newa",
                                       parents=[parrent_parser],
                                       help="Create a new application")
    parser_new.set_defaults(func=cmd_newa)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
        exit(0)

    if args.printheader:
        print(t_header.header_text)
        exit(0)

    parser.print_help()


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt as e:  # Ctrl-C
        raise e
    except SystemExit as e:        # sys.exit()
        raise e
    except Exception as e:
        print('ERROR, UNEXPECTED EXCEPTION')
        print(str(e))
        traceback.print_exc()
        os._exit(1)
