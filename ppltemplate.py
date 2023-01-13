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

import argparse
import json
import os
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from typing import List

from git import Repo

from bashplates import Bp
from query import Query

# Settings ------------------------------------------------------------------

AppName = "mptemplate"
AppVersion = "0.3"
AppLicense = "MIT"
AppAuthor = "Peter Malmberg <peter.malmberg@gmail.com>"

# Absolute path to script itself
self_dir = os.path.abspath(os.path.dirname(sys.argv[0]))


class App:
    NAME = "mpterm"
    VERSION = "0.2"
    DESCRIPTION = "MpTerm is a simple serial terminal program"
    LICENSE = ""
    AUTHOR = "Peter Malmberg"
    EMAIL = "peter.malmberg@gmail.com"
    ORG = ""
    HOME = "github.com/zonbrisad/mpterm"
    ICON = f"{self_dir}/icons/mp_icon2.png"


template_dir = f"{self_dir}/pyplate"
# readme_md = f"{template_dir}/README.md"

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

#    dependencies: List[TemplateX] = field(default_factory=list)

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
    project: str = ""

    out_dir: str = ""

    has_preamble: bool = True
    has_header: bool = True
    has_main: bool = False
    has_main_application: bool = False
    has_separators: bool = False
    has_argparse: bool = False
    has_argparse_sub: bool = False
    has_debug: bool = False

    def __init__(self, args: argparse.ArgumentParser) -> None:
        self.args = args
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.out_dir = os.getcwd()
        self.has_main = self.args.main
        self.has_separators = self.args.separators

        self.set_attribute("name", "Enter module name", "")
        self.set_attribute("description", "Enter brief description", "")
        self.set_attribute("author", "Enter name of author", "BP_NAME")
        self.set_attribute("email", "Enter email of author", "BP_EMAIL")

        # if external header, read into var
        if self.args.header is not None:
            self.header = TemplateX()
            with self.args.header as f:
                self.header.header_text = f.read()
        else:
            self.header = t_header

    def set_attribute(self, attribute: str, question: str, env: str):
        if getattr(self.args, attribute) is not None:  # If command line arguments are present use them
            setattr(self, attribute, getattr(self.args, attribute))
        else:
            setattr(self, attribute,
                    Query.read_string(question, os.getenv(env)))


@dataclass
class ClassTemplate():
    name: str = ""
    parrent: str = ""
    methods: str = ""
    dataclass: bool = False
    _init: str = ""
    _str: str = ""
    _eq: str = ""
    vars = None

    def add_var(self, name, type="", default=""):
        if self.vars is None:
            self.vars = []

        self.vars.append({name, type, default})

    def __str__(self) -> str:
        if self.vars is None:
            self.vars = []

        str = ""
        if self.dataclass:
            str = "@dataclass\n"

        if self.parrent == "":
            str += f"class {self.name}:"
        else:
            str = f"class {self.name}({self.parrent}):"

        for v in self.vars:
            str += f"    {v[0]}"

        return str


class Template(TemplateX):
    """docstring for template."""

    def __init__(self, conf: TConf, pre: List[TemplateX], post: List[TemplateX]):
        super().__init__()
        self.conf = conf
        self.pre = pre
        self.post = post

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

        for x in self.pre:
            self.add(x)

        if Query.read_bool("Include logging?", default=True):
            self.add(t_logging)

        if Query.read_bool("Include argparse?", default=True):
            if Query.read_bool("Argparse with subcommands?", default=False):
                self.add(t_argtable_cmd)
            else:
                self.add(t_argtable)

        if self.conf.has_main_application:
            self.add(t_main_application)
        elif self.conf.has_main:
            self.add(t_main)

        for x in self.post:
            self.add(x)

        self.text += self.preamble_text
        self.text += self.header_text
        self.add_separator("Imports")
        self.text += self.imports_text
        self.add_separator("Variables")
        self.text += self.variables_text
        self.add_separator("Code")
        self.text += self.code_text

        if self.conf.has_main or self.conf.has_main_application:
            self.text += "def main() -> None:\n"
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

    def write(self, dir=None) -> str:
        if dir is None:
            file_name = f"{self.conf.out_dir}/{self.conf.name}"
        else:
            file_name = f"{dir}/{self.conf.name}"

        with open(file_name, "w") as file:
            file.write(self.text)
        os.chmod(file_name, 0o770)
        return file_name

    def __str__(self) -> str:
        return self.text


def print_info():
    print("Script name    " + AppName)
    print("Script version " + AppVersion)
    print("Script path    " + os.path.realpath(__file__))


@dataclass
class ProjectGenerator:
    create_subdir: bool = True
    create_git: bool = True
    create_gitignore: bool = True
    create_readme: bool = True
    create_history: bool = True
    project_name: str = ""
    project_dir: str = ""
    subdir_name: str = ""

    def query(self):
        self.project_dir = os.getcwd()
        self.project_name = Query.read_string("Project name?", self.project_name)
        self.create_subdir = Query.read_bool("Create subdirectory?",
                                             default=self.create_subdir)
        if (self.create_subdir):
            self.subdir_name = Query.read_string("Name of subdirectory?",
                                                 default=self.project_name)

        self.create_git = Query.read_bool("Initiate git repository?",
                                          default=self.create_git)

        if (self.create_git):
            self.create_gitignore = Query.read_bool("Create .gitignore?",
                                                    default=self.create_gitignore)
            self.create_readme = Query.read_bool("Create README.md?",
                                                 default=self.create_readme)
            self.create_history = Query.read_bool("Create HISTORY.md?",
                                                  default=self.create_history)

    def git_add(self, file: str) -> None:
        if self.create_git:
            self.repo.index.add(file)

    def create(self):
        if self.create_subdir:
            self.project_dir = f"{self.project_dir}/{self.subdir_name}"
            if not Bp.mkdir(self.project_dir):
                exit()

        f_readme = f"{self.project_dir}/README.md"
        f_history = f"{self.project_dir}/HISTORY.md"
        f_gitignore = f"{self.project_dir}/.gitignore"

        if self.create_git:
            self.repo = Repo.init(self.project_dir)

            if self.create_readme:
                Bp.cp(f"{template_dir}/README.md", f_readme)
                self.git_add(f_readme)

            if self.create_history:
                Bp.cp(f"{template_dir}/HISTORY.md", f_history)
                self.git_add(f_history)

            if self.create_gitignore:
                Bp.cp(f"{template_dir}/gitignore", f_gitignore)
                self.git_add(f_gitignore)

    def commit(self):
        if self.create_git:
            self.repo.index.commit("Initial commit")


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
# __DESCRIPTION__
#
# File:     __NAME__
# Author:   __AUTHOR__  __EMAIL__
# Org:      __ORGANISTATION__
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
class App:
    NAME = "__NAME__"
    VERSION = "0.01"
    DESCRIPTION = "__DESCRIPTION__"
    LICENSE = ""
    AUTHOR = "__AUTHOR__"
    EMAIL = "__EMAIL__"
    ORG = "__ORGANISATION__"
    HOME = ""
    ICON = ""

"""
)

t_argtable = TemplateX(
    imports_text="""\
import argparse
""",
    main_func_text="""\
    parser = argparse.ArgumentParser(
        prog=App.NAME,
        description=App.DESCRIPTION,
        epilog="",
        add_help=True)
    parser.add_argument("--debug", action="store_true", default=False,
                        help="Print debug messages")
    parser.add_argument("--version", action="version",
                        version=f"{App.NAME} {App.VERSION}",
                        help="Print version information")
    args = parser.parse_args()
    parser.print_help()
"""
)

t_argtable_cmd = TemplateX(
    imports_text="""\
import argparse
""",
    code_text="""
def cmd_cmd1():
    pass


""",
    main_func_text="""\
    p_parser = argparse.ArgumentParser(add_help=False)
    p_parser.add_argument("--debug", action="store_true", default=False,
                          help="Print debug messages")
    p_parser.add_argument("--version", action="version",
                          help="Print version information",
                          version=f"{App.NAME} {App.VERSION}")

    parser = argparse.ArgumentParser(
        prog=App.NAME,
        description=App.DESCRIPTION,
        epilog="",
        parents=[p_parser]
        )
    subparsers = parser.add_subparsers(title="Commands",
                                       help="",
                                       description="")

    cmd1 = subparsers.add_parser("cmd1", parents=[p_parser],
                                 help="Command 1")
    cmd1.set_defaults(func=cmd_cmd1)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func()
        exit(0)

    parser.print_help()
"""
)


t_logging = TemplateX(
    imports_text="""\
import logging
""",
    main_func_text="""\
    logging_format = "[%(levelname)s] %(lineno)d %(funcName)s() : %(message)s"
    logging.basicConfig(format=logging_format, level=logging.DEBUG)
"""
)


t_qt5 = TemplateX(
#    dependecies=[t_application],
    imports_text="""\
from PyQt5.QtCore import Qt, QTimer, QSettings, QIODevice
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar,\\
                            QAction, QStatusBar, QDialog, QVBoxLayout,\\
                            QHBoxLayout, QTextEdit, QDialogButtonBox,\\
                            QPushButton, QMessageBox, QWidget, QLabel,\\
                            QFileDialog, QSpacerItem, QSizePolicy
""",
    variables_text="""
# Qt main window settings
win_title = App.NAME
win_x_size = 320
win_y_size = 240
""",
    code_text="""\
about_html=f\"\"\"
<center><h2>{App.NAME}</h2></center>
<br>
<b>Version: </b>{App.VERSION}
<br>
<b>Author: </b>{App.AUTHOR}
<br>
<hr>
<br>
{App.DESCRIPTION}
<br>
\"\"\"


class AboutDialog(QDialog):
    def __init__(self, parent = None):
        super(AboutDialog, self).__init__(parent)

        self.setWindowTitle(App.NAME)
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(400, 300)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(2)
        self.setLayout(self.verticalLayout)

        # TextEdit
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.verticalLayout.addWidget(self.textEdit)
        self.textEdit.insertHtml(about_html)

        # Buttonbox
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStandardButtons( QDialogButtonBox.Ok )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.setCenterButtons(True)
        self.verticalLayout.addWidget(self.buttonBox)

    @staticmethod
    def about(parent = None):
        dialog = AboutDialog(parent)
        result = dialog.exec_()
        return (result == QDialog.Accepted)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.resize(win_y_size, win_y_size)
        self.setWindowTitle(win_title)
        #self.setWindowIcon(QIcon(App.ICON))

        # Create central widget
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(2)

        # TextEdit
        self.textEdit = QTextEdit(self.centralwidget)
        self.verticalLayout.addWidget(self.textEdit)

        # Menubar
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        # Menus
        self.menuFile = QMenu("File", self.menubar)
        self.menubar.addAction(self.menuFile.menuAction())

        self.menuHelp = QMenu("Help", self.menubar)
        self.menubar.addAction(self.menuHelp.menuAction())

        self.actionOpen = QAction("Open", self)
        self.actionOpen.setStatusTip("Open file")
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionOpen.triggered.connect(self.open)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()

        self.actionQuit = QAction("Quit", self)
        self.actionQuit.setStatusTip("Quit application")
        self.actionQuit.setShortcut("Ctrl+Q")
        self.actionQuit.triggered.connect(self.exit)
        self.menuFile.addAction(self.actionQuit)

        self.actionAbout = QAction("About", self)
        self.actionAbout.setStatusTip("About")
        self.actionAbout.triggered.connect(lambda: AboutDialog.about())
        self.menuHelp.addAction(self.actionAbout)

        # Statusbar
        self.statusbar = QStatusBar(self)
        self.statusbar.setLayoutDirection(Qt.LeftToRight)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

    def exit(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("Quit")
        msgBox.setText("Are you sure you want to quit?")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel )
        if msgBox.exec() == QMessageBox.Ok:
            self.close()

    def open(self):
        files = QFileDialog.getOpenFileNames(self, "Open file", ".", "*.*")

    def closeEvent(self, event: QCloseEvent) -> None:
        self.exit()
        return super().closeEvent(event)


""",
    main_func_text="""\
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
"""
)

t_gtk = TemplateX(
    imports_text="""\
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
""",
    code_text="""\
class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title=App.NAME)


""",
    main_func_text="""\
    main_win = MainWindow()
    main_win.connect("destroy", Gtk.main_quit)
    main_win.show_all()
    Gtk.main()
"""
)


def create_project(template: Template):

    if Query.read_bool("Do you want to create a project?", False):
        proj = ProjectGenerator()
        proj.project_name = template.conf.name
        proj.query()
        proj.create()
        proj.git_add(template.write(proj.project_dir))
        proj.commit()
        return True

    return False


def cmd_new(args):
    conf = TConf(args)
    conf.has_main = True
    conf.has_main_application = True
    conf.has_separators = True

    template = Template(conf, [], [])
    template.generate()

    if not create_project(template):
        template.write()


def cmd_newa(args):
    conf = TConf(args)
    conf.has_main = False
    conf.has_main_application = True
    conf.has_separators = True

    template = Template(conf, [t_application], [])
    template.generate()

    if not create_project(template):
        template.write()


def cmd_newmod(args):
    conf = TConf(args)
    conf.has_main = True
    conf.has_main_application = False

    template = Template(conf, [], [])
    template.generate()
    template.write()

    
def cmd_newmin(args):
    conf = TConf(args)
    conf.has_main = True
    conf.has_main_application = False

    template = Template(conf, [], [])
    template.generate()
    template.write()


def cmd_newqt(args):
    conf = TConf(args)
    conf.has_main = False
    conf.has_main_application = True
    conf.has_separators = True

    template = Template(conf, [t_application], [t_qt5])
    template.generate()

    if not create_project(template):
        template.write()


def cmd_newgtk(args):
    conf = TConf(args)
    conf.has_main = False
    conf.has_main_application = True
    conf.has_separators = True
    template = Template(conf, [t_application], [t_gtk])
    template.generate()

    if not create_project(template):
        template.write()


def cmd_newp(args):
    proj = ProjectGenerator()
    proj.query()
    proj.create()
    proj.commit()


class Settings:
    SETTINGS_DIR = "~/.config/pyplate"
    SETTINGS_FILE = "pyplate.json"

    def __init__(self) -> None:
        with open("pyplate/pyplate.json") as f:
            data = json.load(f)

        print(data)

    def create(self) -> None:
        # Create personal settings
        pass


def main() -> None:

    # logging.basicConfig(level=logging.DEBUG,
    #                     format="[%(levelname)s]%(asctime)s %(message)s")

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
                                help="Name of author"
                                )
    parrent_parser.add_argument("--email",
                                type=str,
                                help="Email of author"
                                )
    parrent_parser.add_argument("--project",
                                type=str,
                                help="Name of project"
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

    subparsers = parser.add_subparsers(title="Commands",
                                       help="",
                                       description="")
                                       
    parser_new = subparsers.add_parser("new", parents=[parrent_parser],
                                       help="Create a new python file")
    parser_new.set_defaults(func=cmd_new)

    parser_new = subparsers.add_parser("newm", parents=[parrent_parser],
                                       help="Create a new python module")
    parser_new.set_defaults(func=cmd_newmod)
    parser_new = subparsers.add_parser("newmin", parents=[parrent_parser],
                                       help="Create a new minimal python file")
    parser_new.set_defaults(func=cmd_newmin)
    parser_new = subparsers.add_parser("newa", parents=[parrent_parser],
                                       help="Create a new application")
    parser_new.set_defaults(func=cmd_newa)
    parser_new = subparsers.add_parser("newqt", parents=[parrent_parser],
                                       help="Create a new QT5 application")
    parser_new.set_defaults(func=cmd_newqt)
    parser_new = subparsers.add_parser("newgtk", parents=[parrent_parser],
                                       help="Create a new GTK3+ application")
    parser_new.set_defaults(func=cmd_newgtk)
    parser_new = subparsers.add_parser("newp", parents=[parrent_parser],
                                       help="Create python project")
    parser_new.set_defaults(func=cmd_newp)

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
