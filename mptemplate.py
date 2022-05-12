#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# 
# C/C++ template generator
#
# File:    ctemplate.py
# Author:  Peter Malmberg <peter.malmberg@gmail.com>
# Date:    2016-02-19
# Version: 0.3
# Python:  >=3
# Licence: MIT
# 
# -----------------------------------------------------------------------
# History
# - Ver 0.3 
# Major rewrite for better code generation
#
# Todo 
#
# Imports -------------------------------------------------------------------

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

# Code ----------------------------------------------------------------------

# 
# Configuration class
#
class CConf():
    main       = False
    sigint     = False
    author     = ""
    brief      = ""
    date       = ""
    org        = ""
    isCpp      = False
    moduleName = ""

    # Libraries
    gtk        = False
    qt         = False
    signals    = False
    argtable   = False
    glib       = False
    
    name       = ""
    email      = ""
    license    = ""
    org        = ""
    author     = ""
    
    makefile   = ""
    
    def __init__(self):
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.bp()

    # Get bashplates environment variables (if available)
    def bp(self):
        self.name    = os.getenv('BP_NAME',    "")
        self.email   = os.getenv('BP_EMAIL',   "")
        self.license = os.getenv('BP_LICENSE', "")
        self.org     = os.getenv('BP_ORG',     "")
        self.author  = self.name+" <"+self.email+">"
        
    def ask(self, module):
        print("Creating new "+module)
    
        if self.moduleName == "":
            self.moduleName = input("Enter "+module+" name(no extention):>")
        
        if self.brief == "":
            self.brief = input("Enter brief description:> ")

    
class CFile():
    moduleName = ""
    fileName   = ""
    
    # Source file sections
    header     = ""
    include    = ""
    defines    = ""
    variables  = ""
    prototypes = ""
    code       = ""
    # main() function subsections
    mainVars   = ""
    mainInit   = ""
    mainCode   = ""
    mainExit   = ""

    buf        = ""
    isHeader   = False 
    isCpp      = False
    
    def __init__(self, conf, isHeader):
        self.conf       = conf
        self.moduleName = conf.moduleName
        self.isHeader   = isHeader
        self.isCpp      = conf.isCpp
        
        if isHeader: 
            self.fileName = self.moduleName + ".h"
        else:
            if self.isCpp:
                self.fileName = self.moduleName + ".cpp"
            else:
                self.fileName = self.moduleName + ".c"
                
    def addHeader(self):
        hFileName = scriptPath + "/header.h"
        hFile = Path(hFileName)

        if hFile.is_file():            # Using external header file if existing
            try:
                f = open(hFileName, 'r+')
            except IOError:
                logging.debug("Could not open file %s" % (hFileName))
                exit()
            except:
                print ("Unexpected error:", sys.exc_info()[0])
                exit()
        
                self.header = f.read()
        else:                             # Using internal header example
            self.header = headerExample
        return
    
    def addInclude(self, fileName, local = False):
        if local:
            self.include += ("#include \""+fileName+"\"\n")
        else:
            self.include += ("#include <"+fileName+">\n")
    
    def addDefine(self, name, value):
        self.defines += ("#define  " + name + "  "+ value + "\n")

    def addVariable(self, name):
        self.variables += name + "\n"

    def addPrototype(self, prototype):
        self.prototypes += prototype
    
    def addSection(self, desc):
        line = '-' * (73 - len(desc))
        self.buf += "\n// " + desc + " " + line + "\n\n"
        
    def addSentinelBegin(self, sentinel):
        self.buf +=  \
        "#ifndef "+sentinel+"_H\n"      \
        "#define "+sentinel+"_H\n\n" 
    
    def addSentinelEnd(self):
        self.buf += "#endif\n\n"

    def addCppSentinel(self):
        self.buf += \
        "#ifdef __cplusplus\n"   \
        "extern \"C\" {\n"       \
        "#endif\n\n"
     
    def addCppSentinelEnd(self): 
        self.buf +=                        \
        "#ifdef __cplusplus\n"             \
        "} //end brace for extern \"C\"\n" \
        "#endif\n"

    def addAppDefines(self):
        self.addDefine("APP_NAME        ", "\""+self.moduleName+"\"")
        self.addDefine("APP_VERSION     ", "\"0.01\"")
        self.addDefine("APP_DESCRIPTION ", "\"\"")
        self.addDefine("APP_AUTHOR      ", "\""+self.conf.author+"\"")
        self.addDefine("APP_LICENSE     ", "\""+self.conf.license+ "\"")
        self.addDefine("APP_ORG         ", "\"\"")
#    addDefine("APP_LOGFILE",     "glib.log")
#    addDefine("APP_PIDFILE",     "/tmp/glibtest.pid")

    def addComment(self, comment):
        self.buf += "  // "+comment+"\n"

    def save(self, dir):
        # Open files to be generated
        try:
            file = open(dir+"/"+self.fileName, 'w')
            file.write(self.buf)
            file.close()
        except IOError:
            logging.debug("Could not open file %s" % (fileName))
            exit()
    
    def addSignal(self, signal, handler):
        self.prototypes += "void "+handler+"(int sig);\n"
        self.code       += "void "+handler+"(int sig) {\n\n}\n\n"
        self.mainInit   += "  signal("+signal+", "+handler+");\n"
    
    def addSignals(self):
        self.addInclude("signal.h")
        self.addSignal("SIGINT", "sigint")
        self.addSignal("SIGHUP", "sighup")
        self.addSignal("SIGUSR1", "sigusr1")
        self.addSignal("SIGUSR2", "sigusr2")
        self.addSignal("SIGTERM", "sigterm")
                
    def addQt(self):    
        #if (conf.qt):    
        self.addInclude("QApplication")
        self.addInclude("QCoreApplication")
        self.addInclude("QDebug")
        self.addInclude("QMainWindow")
        self.addInclude("QPushButton")
        self.addInclude("QLabel")
        
        self.mainCode += "  Q_INIT_RESOURCE(application);\n\n"
        self.mainCode += "  QApplication app(argc, argv);\n"
        self.mainCode += "  QCoreApplication::setOrganizationName(APP_ORG);\n"
        self.mainCode += "  QCoreApplication::setApplicationName(APP_NAME);\n"
        self.mainCode += "  QCoreApplication::setApplicationVersion(APP_VERSION);\n\n"
#        self.mainCode += "  QCommandLineParser parser;\n"
#        self.mainCode += "  parser.setApplicationDescription(QCoreApplication::applicationName());\n"
#        self.mainCode += "  parser.addHelpOption();\n"
#        self.mainCode += "  parser.addVersionOption();\n"
#        self.mainCode += "  parser.addPositionalArgument("file", "The file to open.");\n"
#        self.mainCode += "  parser.process(app);\n"
        
        self.mainCode += "  MainWindow mainWin;\n"
#        self.mainCode += "  if (!parser.positionalArguments().isEmpty())\n"
#        self.mainCode += "  mainWin.loadFile(parser.positionalArguments().first());\n"
        self.mainCode += "  mainWin.show();\n"
        self.mainCode += "  return app.exec();\n"
                
        
 #   def addMain(self):
 #       
 #       self.mainCode = "int main(int argc, char *argv[]) {\n" 
 #       + self.mainVars + self.mainCode
 #       self.mainCode += "  return 0;\n"
 #       self.mainCode += "}\n"
        
    def addStdIncludes(self):
        if self.isCpp:
            self.addInclude("iostream")
        else:
            self.addInclude("stdio.h")
            self.addInclude("stdlib.h")
            self.addInclude("stdint.h")
            self.addInclude("string.h")
            self.addInclude("unistd.h")
            self.addInclude("sys/types.h")
            self.addInclude("errno.h")
        
    def replace(self, str, newStr):
        self.buf = self.buf.replace(str, newStr)

    def newLine(self):
        self.buf += "\n"
    
    def addGlib(self):
        self.addInclude("glib-2.0/glib.h")
        self.addVariable("GMainLoop *mLoop;")
        self.addVariable("static gboolean opt_verbose;")
        self.addVariable(glibVars)
        self.mainVars += glibMainVars
        self.mainCode += glibMain
        self.code += glibCode
        self.prototypes += glibPrototypes
    
    def addGtk(self):
        self.addInclude("gtk/gtk.h")
    
        
    def create(self):
        
        self.addHeader()
        
        if self.conf.main and not self.isHeader:
            self.addStdIncludes()
            
        if self.conf.main and not self.isHeader and self.conf.glib:
            self.addGlib()
        
        if self.conf.signals and not self.isHeader:
            self.addSignals()
            
        if self.conf.argtable and not self.isHeader:
            self.addInclude('argtable3.h', True)
            self.variables +=  argtableVars
            self.mainVars  += argtableMainVars
            self.mainCode  += argtableMain
            
        if self.conf.qt:
            self.addQt()
        
        if self.conf.main and self.isHeader:
            self.addAppDefines()

        if not self.isHeader:
            self.addInclude(self.moduleName+".h", True)
            
        self.generate()    

        
    def generate(self):
        # Assemble all sections into one complete source file
        self.buf = ""
        self.buf = self.buf + self.header
        
        if self.isHeader:
            self.addSentinelBegin(self.moduleName.upper())

        if self.isHeader and not self.isCpp:
            self.addCppSentinel()
        
        self.newLine()
        self.addSection("Includes")
        self.buf += self.include
        
        self.addSection("Macros")
        self.buf += self.defines
                
        self.addSection("Datatypes")

        self.addSection("Variables")
        self.buf += self.variables

        self.addSection("Prototypes")
        self.buf += self.prototypes
        
        if self.conf.main  and not self.isHeader:
            self.addSection("Code")
            self.buf += self.code
        
            self.buf += "int main(int argc, char *argv[]) {\n"
            self.buf += self.mainVars
            self.buf += self.mainInit
            self.buf += self.mainCode
            self.buf += self.mainExit
            self.buf += "}\n"
        
        if self.isHeader and not self.isCpp:
            self.addCppSentinelEnd()
            
        if self.isHeader:
            self.addSentinelEnd()    

        self.replace("__FILENAME__", self.fileName     )
        self.replace("__BRIEF__",    self.conf.brief   )
        self.replace("__DATE__",     self.conf.date    )
        self.replace("__AUTHOR__",   self.conf.author  )    
        self.replace("__LICENSE__",  self.conf.license )
    
    def print(self):
        print(self.buf)

class CClass(CFile):
    className = ""
    parrent   = ""
    methods   = ""
    classBuf  = ""
    qt        = False
    
    def __init__(self, conf, parrent, isHeader):
        conf.isCpp = True
        super().__init__(conf, isHeader)
        self.className = self.moduleName
        self.parrent   = parrent
        
        
    def addMethod(self, dataType, methodName, arguments):
        if self.isHeader:
            if dataType=="":
                self.classBuf += "    " + methodName+"("+arguments+");\n"
            else:
                self.classBuf += "    " +dataType + " " + methodName+"("+arguments+");\n"
        else:
            self.code += self.className+"::"+methodName+"() {\n"
            self.code += "\n}\n\n"
            
    def create(self):
        
        self.addMethod("", self.className, "")
        self.addMethod("", "~"+self.className, "")

        if self.isHeader:
            if (self.parrent == ""):
                self.prototypes += "class "+self.className+" {\n"
            else:
                self.prototypes += "class "+self.className+": public "+self.parrent+" {\n"
            
            if self.qt:
                self.prototypes += "  Q_OBJECT\n"
            
            self.prototypes += "  public:\n"
            self.prototypes += self.classBuf
            self.prototypes += "  private slots:\n"
            self.prototypes += "  private:\n"
            self.prototypes += "}\n"
        
        
        super().create()
            
    def __str__(self):
        return
    
#    def print(self):
#        self.create()
#        print(self.buf)
#        print(self.code)
        
        
        
def newFile(dir, fileName):
    # Open files to be generated
    try:
        file = open(dir+"/"+fileName, 'w')
        return file
    except IOError:
        logging.debug("Could not open file %s" % (fileName))
        exit()
                                
def textToFile(args, fileName, text):
    file = newFile(args.dir, fileName)
    file.write(text)
    file.close()

def copyLib(lib, dst):
    print('Copying library \"'+lib+'\" to \"'+dst+'\"')
    print('Add  \"'+dst+'/'+lib+'\" to include path.')
    shutil.copytree(scriptPath+'/libs/'+lib, dst+'/'+lib)

    
def newModule(dir, conf):
    
    # ask for some information
    conf.ask("C/C++ module")
    
    if not conf.main:
        conf.main = query_yn("Add main() function", "no")
    
    if conf.main and not conf.isCpp:
        if not conf.glib:
            conf.glib     = query_yn("glib project",      "no")
            
        conf.gtk      = query_yn("GTK project",       "no")
        if conf.gtk:
            conf.glib = True
        
        conf.signals  = query_yn("Include signals",   "no")
        if not conf.glib:
            conf.argtable = query_yn("Include argtable3", "no")
          
    if conf.main and conf.isCpp:    
        conf.qt = query_yn("Qt project", "no")
    
    fileC = CFile(conf, False)
    fileH = CFile(conf, True)
    
    fileH.create()
    fileC.create()
    
    fileH.save(dir)
    fileC.save(dir)
     
    if conf.argtable: 
        copyLib('argtable3', dir)
        # Edit makefile
        
        os.system("cd "+conf.basedir+";make mp-add-include FILE=src/argtable3 Makefile; cd -")
        os.system("cd "+conf.basedir+";make mp-add-source  FILE=src/argtable3/argtable3.c ; cd -" )


def newClass(dir, conf):

    # ask for some information
    conf.ask("C++ class")

    fileH = CClass(conf, "", True)
    fileC = CClass(conf, "", False)
    
    fileH.create()
    fileC.create()
    
    fileH.save(dir)
    fileC.save(dir)

def printInfo():
    print("Script name    " + AppName)
    print("Script version " + AppVersion)
    print("Script path    " + os.path.realpath(__file__))

    
# Absolute path to script itself        
scriptPath = os.path.abspath(os.path.dirname(sys.argv[0]))
mpPath     = scriptPath+"/.."    


def cmd_qtmain(args, conf):
    print("qtmain")
    exit(0)   

def cmd_qtwin(args, conf):
    print("qtwin")
    exit(0)

def cmd_qtdia(args, conf):
    print("qtdia")
    exit(0)
    
def cmd_newc(args, conf):
    conf.isCpp = False
    newModule(args.dir, conf)
    exit(0)

def cmd_newcpp(args, conf):
    conf.isCpp = True
    newModule(args.dir, conf)
    exit(0)

def cmd_newclass(args, conf):
    newClass(args.dir, conf)    
    exit(0)
        
def cmd_giti(args, conf):
    textToFile(args, ".gitignore", gitIgnore)
    exit(0)

def main():
    
    conf = CConf()
    
    logging.basicConfig(level=logging.DEBUG)

    parrent_parser = argparse.ArgumentParser(add_help=False)         
    parrent_parser.add_argument("--license",  type=str,  help="License of new file",           default=conf.license)
    parrent_parser.add_argument("--author",   type=str,  help="Author of file",                default=conf.name+" <"+conf.email+">")

    parrent_parser.add_argument("--dir",      type=str,  help="Project source directory", default=".")
    parrent_parser.add_argument("--basedir",  type=str,  help="Project directory", default=".")
    
    parrent_parser.add_argument("--main",     action="store_true",  help="Include main() function into module", default=False)
    parrent_parser.add_argument("--cpp",      action="store_true",  help="Module is a C++ file", default=False)
    parrent_parser.add_argument("--name",     type=str,  help="Name of C/C++ module", default="")
    parrent_parser.add_argument("--brief",    type=str,  help="Brief description",    default="")
    parrent_parser.add_argument("--glib",     action="store_true",  help="Use glib library",     default=False)

    

    # options parsing
    parser = argparse.ArgumentParser(
             prog=AppName+'.py',
             description="Makeplate C/C++ template generator", 
             epilog = "",
             parents = [parrent_parser],
             )
             
    parser.add_argument("--version",  action='version',  help="Directory where to store file", version=AppVersion)
             
    subparsers = parser.add_subparsers(help="")
    parser_newc = subparsers.add_parser("newc",     parents=[parrent_parser],  help="Create a new C and H file set")
    parser_newc.set_defaults(func=cmd_newc)
    parser_newclass = subparsers.add_parser("newclass", parents=[parrent_parser],   help="Create a new C++ class")
    parser_newclass.set_defaults(func=cmd_newclass)
    parser_newcpp = subparsers.add_parser("newcpp", parents=[parrent_parser],  help="Create a new C++ file")
    parser_newcpp.set_defaults(func=cmd_newcpp)
#    parser_qtdia = subparsers.add_parser("qtdia",   parents=[parrent_parser],  help="Create a Qt5 dialog")
#    parser_qtdia.set_defaults(func=cmd_qtdia)
#    parser_qtmain = subparsers.add_parser("qtmain", parents=[parrent_parser],  help="Create a Qt5 main application")
#    parser_qtmain.set_defaults(func=cmd_qtmain)
#    parser_qtwin = subparsers.add_parser("qtwin",   parents=[parrent_parser],  help="Create a Qt5 main window")
#    parser_qtwin.set_defaults(func=cmd_qtwin)
#    parser_qtdia = subparsers.add_parser("qtdia",   parents=[parrent_parser],  help="Create a Qt5 dialog")
#    parser_qtdia.set_defaults(func=cmd_qtdia)
    parser_qtdia = subparsers.add_parser("giti",    parents=[parrent_parser],  help="Create .gitignore file")
    parser_qtdia.set_defaults(func=cmd_giti)
    
#    parser.add_argument("--header",   type=str,            help="External header file",  default="headerExample")
#    subparsers = parser.add_subparsers(title='subcommands', help="sfda fdsa fdsa afsd")

    args = parser.parse_args()
    if hasattr(args, 'author'):
        conf.author  = args.author
    if hasattr(args, 'license'):
        conf.license = args.license            
    if hasattr(args, 'main'):
        conf.main = args.main
    if hasattr(args, 'cpp'):
        conf.isCpp = args.cpp
    if hasattr(args, 'name'):
        conf.moduleName = args.name
    if hasattr(args, 'brief'):
        conf.brief = args.brief
    if hasattr(args, 'glib'):
        conf.glib = args.glib
    if hasattr(args, 'basedir'):
        conf.basedir = args.basedir
        
    if hasattr(args, 'func'):
        args.func(args, conf)
        exit(0)
    
    parser.print_help()
    exit(0)

def query_list(question, db, default="yes"):
    prompt = " >"

    #print(db)
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
    
    
headerExample="""/**
 *---------------------------------------------------------------------------
 * @brief    __BRIEF__
 *
 * @file     __FILENAME__
 * @author   __AUTHOR__
 * @date     __DATE__
 * @license  __LICENSE__
 *
 *---------------------------------------------------------------------------
 *
 *
 */
"""    

gtkMainExample="""

int main(int argc, char *argv[]) {
 
    signal(SIGINT, sigInt);
    signal(SIGHUP, sigHup);


// GTK Glade --------------------------------------------------------------------

    gtk_init(&argc, &argv);

    builder = gtk_builder_new();
    gtk_builder_add_from_file (builder, "gtkTest.glade", NULL);

    window = GTK_WIDGET(gtk_builder_get_object(builder, "window2"));
    gtk_builder_connect_signals(builder, NULL);

    //g_object_unref(builder);

    GtkWidget *w;
    GtkTextIter iter;
    w = gtk_builder_get_object(builder, "textview2");
    //gtk_text_view_set_buffer(w, buf);
    buf = gtk_text_view_get_buffer(w);
    gtk_text_buffer_get_iter_at_offset(buf, &iter, 0);
    gtk_text_buffer_insert(buf, &iter, "Kalle", -1);
    
    return 0;
}
"""

glibMainExample="""
"""

glibVars="""
static gint      opt_integer = 42;
static gdouble   opt_double  = 42.42;
static gchar    *opt_string  = "Kalle";
static gchar    *opt_file    = "F";
static gboolean  opt_bool    = FALSE;

static gboolean  opt_verbose = FALSE;
static gboolean  opt_version = FALSE;

static GOptionEntry entries[] = {
  { "bool",     'b', 0, G_OPTION_ARG_NONE,     &opt_bool,     "Boolean option",  NULL },
  { "integer",  'i', 0, G_OPTION_ARG_INT,      &opt_integer,  "Integer option",  "nr" },
  { "string",   's', 0, G_OPTION_ARG_STRING,   &opt_string,   "String option",   "nr" },
  { "double",   'd', 0, G_OPTION_ARG_DOUBLE,   &opt_double,   "Double option",   "d"  },
  { "file",     'f', 0, G_OPTION_ARG_FILENAME, &opt_file,     "File option",     NULL },
  { "callback", 'c', 0, G_OPTION_ARG_CALLBACK, opt_callback,  "Callback option", NULL },
  
  { "verbose",  'v', 0, G_OPTION_ARG_NONE,     &opt_verbose,  "Verbose output",  NULL },
  { "version",   0,  0, G_OPTION_ARG_NONE,     &opt_version,  "Version info",    NULL },
  { NULL }
};                                                                                                                                      
"""

glibPrototypes="""
gboolean opt_callback(const gchar *option_name, const gchar *value, gpointer data, GError **error);
"""
glibCode="""
gboolean opt_callback(const gchar *option_name, const gchar *value, gpointer data, GError **error) {
  printf("Callback function for option %s,  value=%s\\n", option_name, value);
  return 1;
}
"""

glibMainVars="""
  GError *error = NULL;
  GOptionContext *context;
"""

glibMain="""
  context = g_option_context_new ("- what the program does");
  g_option_context_add_main_entries (context, entries, NULL);
  
  g_option_context_set_summary(context, "My summary text...");
  g_option_context_set_description(context, "My description text");
  
  if (!g_option_context_parse (context, &argc, &argv, &error)) {
    g_print ("option parsing failed: %s\\n", error->message);
    exit (1);
  }
                  
  if (opt_version) {
    printf("Application version %s\\n", APP_VERSION);
    exit(0);
  }
"""

argtableVars="""
struct arg_lit  *opt_bool;
struct arg_int  *opt_int;
struct arg_dbl  *opt_dbl;
struct arg_str  *opt_str;
struct arg_file *opt_file;
struct arg_int  *opt_intn;

struct arg_lit  *opt_verbose;
struct arg_lit  *opt_version;
struct arg_lit  *opt_help;

struct arg_end  *end;
"""

argtableMainVars="""
  int i;
  int nerrors;
  int exitcode=0;
  
  void* argtable[] = {
    opt_bool  = arg_lit0("b", "bool",                    "Bool option"),
    opt_int   = arg_int0("i","int","<n>",                "Integer option"),
    opt_dbl   = arg_dbl0("d","double",NULL,              "Double option"),
    opt_str   = arg_str0("s","string",NULL,              "String option"),
    opt_file  = arg_file0("f","file","<filename>",       "Filename option"),
    opt_intn  = arg_intn("n","intn",NULL,0,10,           "Multiple Integer option"),
    
    opt_verbose = arg_lit0("v","verbose,debug",          "verbose messages"),
    opt_help    = arg_lit0(NULL,"help",                  "print this help and exit"),
    opt_version = arg_lit0(NULL,"version",               "print version information and exit"),
    end         = arg_end(20)
  };
"""

argtableMain="""  
  // verify the argtable[] entries were allocated sucessfully 
  if (arg_nullcheck(argtable) != 0) {
    // NULL entries were detected, some allocations must have failed 
    printf("%s: insufficient memory\\n",APP_NAME);
    exitcode=1;
    goto appexit;
  }
  
  // Parse the command line as defined by argtable[] 
  nerrors = arg_parse(argc,argv,argtable);
  
  // special case: '--help' takes precedence over error reporting 
  if (opt_help->count > 0) {
    printf("Usage: %s", APP_NAME);
    arg_print_syntax(stdout,argtable,"\\n");
    arg_print_glossary(stdout,argtable,"  %-25s %s\\n");
    exitcode=0;
    goto appexit;
  }
  
  // If the parser returned any errors then display them and exit 
  if (nerrors > 0) {
    // Display the error details contained in the arg_end struct.
    arg_print_errors(stdout,end,APP_NAME);
    printf("Try '%s --help' for more information.\\n", APP_NAME);
    exitcode=1;
    goto appexit;
  }
  
  // special case: '--version' takes precedence error reporting 
  if (opt_version->count > 0) {
    printf("'%s' version %s\\n",APP_NAME, APP_VERSION);
    exitcode=0;
    goto appexit;
  }
  
  if (opt_bool->count > 0) {
    printf("Bool argument\\n");
  }
        
  if (opt_int->count > 0) {
    printf("Integer argument %d\\n", *opt_int->ival);
  }
                
  if (opt_dbl->count > 0) {
    printf("Double argument %f\\n", *opt_dbl->dval);
  }
  
  if (opt_str->count > 0) {
    printf("String argument %s\\n", *opt_str->sval);
  }
                                
  if (opt_file->count > 0) {
    printf("File argument filename  %s\\n", *opt_file->filename);
    printf("File argument basename  %s\\n", *opt_file->basename);
    printf("File argument extension %s\\n", *opt_file->extension);
  }
                                                
  if (opt_intn->count > 0) {
    printf("Integer arguments %d\\n", opt_intn->count);
    for (i=0;i<opt_intn->count;i++) {
      printf("Arg %d = %d\\n", i, opt_intn->ival[i]);
    }
  }
                                                                      
  
  
appexit:
    
  // deallocate each non-null entry in argtable[] 
  arg_freetable(argtable,sizeof(argtable)/sizeof(argtable[0]));
  
  return exitcode;
"""





mainExample="""
int main(int argc, char *argv[]) {
        
    return 0;
}
"""

qtCoreMainExample="""
int main(int argc, char *argv[]) {
 
    QCoreApplication app(argc, argv);
         
    return app.exec();
}
"""

qtMainExample="""
int main(int argc, char *argv[]) {
 
    QApplication app(argc, argv);
//    MainWindow w;
//    w.show();
         
    return app.exec();
}
"""



gitIgnore="""
#
# Makeplate .gitignore file
#
# 
# 
#


# Makeplate specific files
#--------------------------------------------------------------------
archive
backup
output
personal*.mk

# Temporary files
#--------------------------------------------------------------------
*.tmp
*.old
*.orig
*~

# Revision control
#--------------------------------------------------------------------
.svn
.git

# C/C++
#--------------------------------------------------------------------

# Object files
*.o
*.ko
*.obj
*.elf
*.lo
*.slo

# Symbols etc
*.lst
*.sym
*.map
*.lss

# Precompiled Headers
*.gch
*.pch

# Static Libraries
*.lib
*.a
*.la
*.lo
*.lai

# Shared libraries (inc. Windows DLLs)
*.dll
*.so
*.so.*
*.dylib

# Executables
*.exe
*.out
*.app
*.i*86
*.x86_64
*.hex
*.bin
*.elf
*.a

# Debug files
*.dSYM/

# Makefile specific
#--------------------------------------------------------------------
*.d
.dep


# Qt 
#--------------------------------------------------------------------
*.moc
moc_*.h
moc_*.cpp
*_moc.h
*_moc.cpp
qrc_*.cpp
ui_*.h

# QtCreator Qml
*.qmlproject.user
*.qmlproject.user.*

# QtCtreator CMake
CMakeLists.txt.user*
"""


argTable="""
"""



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

        
