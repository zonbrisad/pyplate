#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
#
# template generator class 
#
# File:     pytemplates.py
# Author:   Peter Malmberg  <peter.malmberg@gmail.com>
# Org:      __ORGANISTATION__
# Date:     2023-09-11
# License:  
# Python:   >= 3.0
#
# ----------------------------------------------------------------------------

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from query import Query


@dataclass
class PyTemplate:
    text: str = ""
    preamble_text: str = ""
    header_text: str = ""
    imports_text: str = ""
    variables_text: str = ""
    code_text: str = ""
    main_func_declaration_text: str = ""
    main_func_text: str = ""
    main_text: str = ""
    query_text: str = ""
    class_decorators: str = ""
    class_vars: str = ""
    class_methods: str = ""
    # class_text: str = ""
    do_query: bool = False
    include: bool = True
    alt: List[PyTemplate] = field(default_factory=list)

    def add(self, other: PyTemplate):
        self.preamble_text += other.preamble_text
        self.header_text += other.header_text
        self.imports_text += other.imports_text
        self.variables_text += other.variables_text
        self.code_text += other.code_text
        self.main_func_declaration_text += other.main_func_declaration_text
        self.main_func_text += other.main_func_text
        self.main_text += other.main_text
        self.class_decorators += other.class_decorators
        self.class_vars += other.class_vars
        self.class_methods += other.class_methods

    def query(self) -> None:
        if self.do_query is False:
            return
        self.include = Query.read_bool(self.query_text, self.include)
        if self.include is True and len(self.alt) > 0:
            self.alt[0].query()

    def get(self) -> PyTemplate:
        if len(self.alt) > 0:
            if self.alt[0].include is True:
                return self.alt[0]

        return self


@dataclass
class ClassTemplate(PyTemplate):
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


@dataclass
class PyConf:
    """PyGenerator configuration class"""
    name: str = ""
    author: str = ""
    description: str = ""
    date: str = ""
    email: str = ""
    license: str = ""
    org: str = ""
    project: str = ""

    out_dir: str = ""
    has_separators: bool = False

    query_name: bool = True
    query_description: bool = True
    query_author: bool = True
    query_email: bool = True

    def __post_init__(self) -> None:
        self.date = datetime.now().strftime("%Y-%m-%d")
        #self.out_dir = os.getcwd()

    def query(self, args):
        self.query_attr(args, "name", "Enter module name", "")
        self.query_attr(args, "description", "Enter brief description", "")
        self.query_attr(args, "author", "Enter name of author", "BP_NAME")
        self.query_attr(args, "email", "Enter email of author", "BP_EMAIL")

    def query_attr(self, args, attribute: str, question: str, env: str):
        q = getattr(self, f"query_{attribute}")

        if q is not True:
            return

        if getattr(args, attribute) is not None:  # If command line arguments are present use them
            setattr(self, attribute, getattr(args, attribute))
        else:
            setattr(self, attribute,
                    Query.read_string(question, os.getenv(env)))


class PyGenerator(PyTemplate):
    """docstring for generator."""
    
    def __init__(self, conf: PyConf,  templates: List[PyTemplate]):
        super().__init__()
        self.conf = conf
        self.templates = templates

    def clear(self):
        self.text = ""

    def replace(self, old: str, new: str):
        self.text = self.text.replace(old, new)

    def add_separator(self, header):
        if self.conf.has_separators:
            self.text += f"# {header} {'-'*(75-len(header))}\n\n"

    def generate(self):
        self.clear()

        for template in self.templates:
            template.query()

        for template in self.templates:
            if template.include is True:
                ta = template.get()
                self.add(ta)

        self.text += self.preamble_text
        self.text += self.header_text
        self.add_separator("Imports")
        self.text += self.imports_text
        if len(self.imports_text) > 0:
            self.text += "\n\n"
        self.add_separator("Variables")
        self.text += self.variables_text
        self.add_separator("Code")
        self.text += self.code_text

        self.text += self.main_func_declaration_text
        if len(self.main_func_declaration_text) > 0 and len(self.main_func_text) == 0:
            self.text += "    pass\n"

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
        print(f"\nWrote {file_name} to disk.")
        # logging.info(f"Wrote {file_name} to disk.")
        return file_name

    def __str__(self) -> str:
        return self.text


t_init = PyTemplate(
    imports_text="""\
"""
)

t_preamble = PyTemplate(
    preamble_text="""\
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
)

t_header = PyTemplate(
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

t_main = PyTemplate(
    main_func_declaration_text="""\
def main() -> None:
""",

    main_text="""\
if __name__ == "__main__":
    main()
"""
)

t_main_application = PyTemplate(
    imports_text="""\
import traceback
import os
import sys
""",
    main_func_declaration_text="""\
def main() -> None:
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

t_application = PyTemplate(
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


t_argtable_cmd = PyTemplate(
    query_text="Include subcommand argument parser?",
    do_query=True,
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

t_argtable = PyTemplate(
    query_text="Include argument parser?",
    do_query=True,
    alt=[t_argtable_cmd],
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

t_logging = PyTemplate(
    query_text="Include logging?",
    do_query=True,
    imports_text="""\
import logging
""",
    main_func_text="""\
    logging_format = "[%(levelname)s] %(lineno)d %(funcName)s() : %(message)s"
    logging.basicConfig(format=logging_format, level=logging.DEBUG)
"""
)


t_qt5 = PyTemplate(
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
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
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

        self.resize(win_x_size, win_y_size)
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
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
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

t_gtk = PyTemplate(
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











def main() -> None:
    pass


if __name__ == "__main__":
    main()
