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
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from git import Repo

from bashplates import Bp

# Settings ------------------------------------------------------------------


# Code ----------------------------------------------------------------------


@dataclass
class TConf:
    """PythonGenerator configuration class"""

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
            self.header = PythonTemplate()
            with self.args.header as f:
                self.header.header_text = f.read()
        else:
            self.header = t_header

    def set_attribute(self, attribute: str, question: str, env: str):
        if (
            getattr(self.args, attribute) is not None
        ):  # If command line arguments are present use them
            setattr(self, attribute, getattr(self.args, attribute))
        else:
            setattr(self, attribute, Bp.read_string(question, os.getenv(env)))


@dataclass
class PythonTemplate:
    text: str = ""
    preamble_text: str = ""
    header_text: str = ""
    imports_text: str = ""
    variables_text: str = ""
    code_text: str = ""
    main_func_text: str = ""
    main_text: str = ""

    query_text: str = ""
    do_query: bool = True
    include: bool = True

    sub_alt: bool = False
    sub: list[PythonTemplate] = field(default_factory=list)

    class_name: str = ""
    class_decorator_text: str = ""
    class_is_dataclass: bool = False
    class_parrent: str = ""
    class_methods: str = ""
    class_vars_text: str = ""
    class_methods_text: str = ""
    class_init_text: str = ""
    class_text: str = ""

    def clear(self):
        self.text = ""

    def replace(self, old: str, new: str):
        self.text = self.text.replace(old, new)

    def add(self, other: PythonTemplate):
        self.preamble_text += other.preamble_text
        self.header_text += other.header_text
        self.imports_text += other.imports_text
        self.variables_text += other.variables_text
        self.code_text += other.code_text
        self.main_func_text += other.main_func_text
        self.main_text += other.main_text

        self.class_name += other.class_name
        self.class_parrent += other.class_parrent
        self.class_vars_text += other.class_vars_text
        self.class_methods_text += other.class_methods_text
        self.class_init_text += other.class_init_text

    def sumarize(self):
        self.text += self.preamble_text
        self.text += self.header_text
        #self.add_separator("Imports")
        self.text += self.imports_text
        #self.add_separator("Variables")
        self.text += self.variables_text

        if self.class_name != "":
            self.text += f"class {self.class_name}({self.class_parrent}):\n"
        self.text += self.class_vars_text
        self.text += self.class_methods_text
        self.text += self.class_init_text
        
        #self.add_separator("Code")
        self.text += self.code_text

        self.text += self.main_func_text
        self.text += self.main_text

    def query(self):
        if self.do_query is True:
            self.include = Bp.read_bool(self.query_text, self.include)

        if self.include is True:
            for tmpl in self.sub:
                tmpl.query()

    def gen(self) -> PythonTemplate:

        if self.sub_alt is True:
            for x in self.sub:
                if x.include is True:
                    x.gen()
                    return x
            return self

        for x in self.sub:
            if x.include is True:
                x.gen()
                self.add(x)

        return self

    def writef(self, file_name) -> str:

        with open(file_name, "w") as file:
            file.write(self.text)
        os.chmod(file_name, 0o770)
        return file_name

    def __str__(self) -> str:
        return self.text


class PythonGenerator(PythonTemplate):
    """docstring for template."""

    def __init__(self, conf: TConf, pre: List[PythonTemplate]):
        super().__init__()
        self.conf = conf
        self.pre = pre

    def add_separator(self, header):
        if self.conf.has_separators:
            self.text += f"\n# {header} {'-'*(75-len(header))}\n\n"
        # else:
        #     self.text += "\n\n"

    def generate(self):
        self.clear()

        for x in self.pre:
            x.query()
            if x.include is True:
                t = x.gen()
                self.add(t)

        self.sumarize()

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

        self.writef(file_name)

        return file_name

    def __str__(self) -> str:
        return self.text


@dataclass
class ClassTemplate:
    name: str = ""
    parrent: str = ""
#    methods: str = ""
    is_dataclass: bool = False
    decorator_text: str = ""
    vars_text: str = ""
    methods_text: str = ""
    init_text: str = ""
    text: str = ""

    query_text: str = ""
    do_query: bool = True
    include: bool = False

    sub: list[ClassTemplate] = field(default_factory=list)

    def __add__(self, other):
        self.vars_text += other.vars_text
        self.methods_text += other.methods_text
        self.init_text += other.init_text
        return self

    def __str__(self) -> str:
        return self.text

    def query(self):
        if self.do_query is True:
            self.include = Bp.read_bool(self.query_text, self.include)

        if self.include is True:
            for tmpl in self.sub:
                tmpl.query()

    def gen(self):
        if self.include is True:
            for tmpl in self.sub:
                tmpl.gen()
                if tmpl.include is True:
                    self += tmpl

    def generate(self) -> PythonTemplate:
        self.text = f"class {self.name}({self.parrent}):\n"

        for tmpl in self.sub:
            # tmpl.query()
            if tmpl.include is True:
                tmpl.gen()
                self += tmpl

        self.text += self.vars_text
        self.text += self.init_text
        self.text += self.methods_text
        self.text += "\n\n"
        return PythonTemplate(code_text=self.text)


dataclass_decorator = ClassTemplate(
    decorator_text="""\
@dataclass
"""
)

t_preamble = PythonTemplate(
    do_query=False,
    query_text="Include preamble?",
    preamble_text="""\
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""",
)

t_header = PythonTemplate(
    do_query=False,
    query_text="Include header?",
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
""",
)

t_main_simple = PythonTemplate(
    query_text="Include main function?",
    do_query=False,
    main_func_text="""\


def main() -> None:
    pass
""",
    main_text="""\


if __name__ == "__main__":
    main()


""",
)


t_main = PythonTemplate(
    query_text="Include main function?",
    do_query=False,
    imports_text="""\
import traceback
import os
import sys
""",
    main_func_text="""\


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


""",
)


t_application = PythonTemplate(
    do_query=False,
    query_text="Include application data?",
    variables_text="""\
class App:
    NAME = "__NAME__"
    VERSION = "0.01"
    DESCRIPTION = "__DESCRIPTION__"
    LICENSE = ""
    COPYRIGHT = ""
    AUTHOR = "__AUTHOR__"
    EMAIL = "__EMAIL__"
    ORG = "__ORGANISATION__"
    HOME = ""
    ICON = ""


""",
)


t_argtable_cmd = PythonTemplate(
    query_text="Argparse with subcommands?",
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

    #parser.print_help()

""",
)

t_argtable = PythonTemplate(
    query_text="Include argparser?",
    sub_alt=True,
    sub=[t_argtable_cmd],
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
    #parser.print_help()

""",
)

t_logging = PythonTemplate(
    query_text="Include logging?",
    imports_text="""\
import logging
""",
    main_func_text="""\
    logging_format = "[%(levelname)s] %(lineno)d %(funcName)s() : %(message)s"
    logging.basicConfig(format=logging_format, level=logging.DEBUG)

""",
)

# about_html=f\"\"\"
# <center><h2>{App.NAME}</h2></center>
# <br>
# <b>Version: </b>{App.VERSION}
# <br>
# <b>Author: </b>{App.AUTHOR}
# <br>
# <hr>
# <br>
# {App.DESCRIPTION}
# <br>
# \"\"\"


# class AboutDialog(QDialog):
#     def __init__(self, parent = None):
#         super(AboutDialog, self).__init__(parent)

#         self.setWindowTitle(App.NAME)
#         self.setWindowModality(Qt.ApplicationModal)
#         self.resize(400, 300)

#         self.verticalLayout = QVBoxLayout(self)
#         self.verticalLayout.setSpacing(2)
#         self.setLayout(self.verticalLayout)

#         # TextEdit
#         self.textEdit = QTextEdit(self)
#         self.textEdit.setReadOnly(True)
#         self.verticalLayout.addWidget(self.textEdit)
#         self.textEdit.insertHtml(about_html)

#         # Buttonbox
#         self.buttonBox = QDialogButtonBox(self)
#         self.buttonBox.setStandardButtons( QDialogButtonBox.Ok )
#         self.buttonBox.accepted.connect(self.accept)
#         self.buttonBox.setCenterButtons(True)
#         self.verticalLayout.addWidget(self.buttonBox)

#     @staticmethod
#     def about(parent = None):
#         dialog = AboutDialog(parent)
#         result = dialog.exec_()
#         return (result == QDialog.Accepted)


qt5_menuitems = PythonTemplate(
    query_text="Qt5: Include menu items?",
    class_init_text="""\

        # Menuitems
        self.menuFile = QMenu("File", self.menubar)
        self.menubar.addAction(self.menuFile.menuAction())

        self.actionOpen = QAction("Open", self)
        self.actionOpen.setStatusTip("Open file")
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionOpen.triggered.connect(self.open)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()

        self.actionQuit = QAction("Quit", self)
        self.actionQuit.setStatusTip("Quit application")
        self.actionQuit.setShortcut("Ctrl+Q")
        self.actionQuit.triggered.connect(self.quit)
        self.menuFile.addAction(self.actionQuit)
""",
    class_methods_text="""\
    def open(self):
        files = QFileDialog.getOpenFileNames(self, "Open file", ".", "*.*")

    def quit(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("Quit")
        msgBox.setText("Are you sure you want to quit?")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel )
        if msgBox.exec() == QMessageBox.Ok:
            self.close()
        
""",
)

qt5_menues = PythonTemplate(
    query_text="Qt5: Include menubar?",
    sub=[qt5_menuitems],
    class_init_text="""\

        # Menu bar
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)
    """,
)

qt5_statusbar = PythonTemplate(
    query_text="Qt5: Include statusbar?",
    class_init_text="""\

        # Status bar
        self.statusbar = QStatusBar(self)
        self.statusbar.setLayoutDirection(Qt.LeftToRight)
        self.setStatusBar(self.statusbar)
""",
)

qt5_mainwin = PythonTemplate(
    do_query=True,
    include=True,
    query_text="Qt5: Main window?",
    class_name="MainWindow",
    class_parrent="QMainWindow",
    sub=[qt5_menues, qt5_statusbar],
    class_init_text="""\
    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)
        self.resize(300,300)
        self.setWindowTitle("Title")
        #self.setWindowIcon(QIcon("my_icon_file"))
        self.setIconSize(QSize(512, 512))

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.mainLayout = QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.mainLayout.setSpacing(2)
""",
    class_methods_text="""\

    def closeEvent(self, ev: QCloseEvent) -> None:
        return super().closeEvent(ev)
""",
)


t_qt5 = PythonTemplate(
    query_text="Qt5: Create application?",
    sub=[qt5_mainwin],
    imports_text="""\
from PyQt5.QtCore import QIODevice, QSettings, QSize, Qt, QTimer
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QDialogButtonBox,
                             QFileDialog, QHBoxLayout, QLabel, QMainWindow,
                             QMenu, QMenuBar, QMessageBox, QPushButton,
                             QSizePolicy, QSpacerItem, QStatusBar, QTextEdit,
                             QVBoxLayout, QWidget)
""",
    main_func_text="""\
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
""",
)


t_gtk = PythonTemplate(
    query_text="GTK3 application?",
    imports_text="""\
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GObject
""",

    code_text="""\
class MainWindow(Gtk.Window):

    def add_menu_item(self, name: str, menu: Gtk.Menu) -> Gtk.MenuItem:
        menu_item = Gtk.MenuItem(label=name)
        menu.append(menu_item)
        return menu_item

    def add_menu(self, name: str, menubar: Gtk.MenuBar) -> Gtk.Menu:
        menu = Gtk.Menu()
        item = Gtk.MenuItem(label=name)
        item.set_submenu(menu)
        menubar.append(item)
        return menu

    def message(self, msg: str):
        # Display a message in the status bar
        context_id = self.statusbar.get_context_id("Status")
        self.statusbar.push(context_id, msg)
        if msg != "":
            GObject.timeout_add(1000, lambda: self.message(""))

    def __init__(self):
        super().__init__(title=App.NAME)
        self.set_default_size(200, 200)

        # Main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.add(main_box)

        # Menubar
        menubar = Gtk.MenuBar()
        main_box.pack_start(menubar, False, False, 0)

        # Main menu
        file_menu = self.add_menu("File", menubar)
        new_item = self.add_menu_item("New", file_menu)
        open_item = self.add_menu_item("Open", file_menu)
        open_item.connect("activate", self.on_open_dialog)
        quit_item = self.add_menu_item("Quit", file_menu)
        quit_item.connect("activate", self.quit)

        help_menu = self.add_menu("Help", menubar)
        about_item = self.add_menu_item("About", help_menu)
        about_item.connect("activate", self.on_about_dialog)

        # Create a status bar
        self.statusbar = Gtk.Statusbar()
        main_box.pack_end(self.statusbar, False, True, 0)

    def quit(self, w):
        Gtk.main_quit()

    def on_open_dialog(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        #self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            logging.debug("Open clicked")
            logging.debug("File selected: " + dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            logging.debug("Cancel clicked")

        dialog.destroy()
 
    def on_about_dialog(self, widget):
        about = Gtk.AboutDialog()
        #about.set_logo()
        about.set_program_name(App.NAME)
        about.set_version(App.VERSION)
        about.set_authors(App.AUTHOR)
        about.set_copyright(App.COPYRIGHT)
        about.set_comments(App.DESCRIPTION)
        about.set_website(App.HOME)
        about.run()
        about.destroy()
       

""",
    main_func_text="""\
    main_win = MainWindow()
    main_win.connect("destroy", Gtk.main_quit)
    main_win.show_all()
    Gtk.main()
""",
)
