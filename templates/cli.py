# Imports -------------------------------------------------------------------
import sys
import os
import traceback
import logging
import argparse
from datetime import datetime, date, time

# Settings ------------------------------------------------------------------

AppName     = "__NAME__"
AppVersion  = "0.1"
AppLicense  = "__LICENSE__"
AppAuthor   = "__AUTHOR__"
AppDesc     = "__DESC__"
AppOrg      = "__ORG__"

# Absolute path to script itself        
scriptPath = os.path.abspath(os.path.dirname(sys.argv[0]))

# Uncomment to use logfile
#LogFile     = "pyplate.log"


# Code ----------------------------------------------------------------------

def main():
    logging.basicConfig(level=logging.DEBUG)

    # options parsing
    parser = argparse.ArgumentParser(
             prog=AppName+'.py', 
             add_help = True, 
             usage=AppName+'.py command [options]' ,
             description=AppDesc,
             epilog=''
             )
             
    parser.add_argument('--version', action='version', version='%(prog)s '+AppVersion)
    parser.add_argument("--info",  action="store_true", help="Information about script")

    # Some examples of parameters (rename or remove unwanted parameters)
    parser.add_argument('-a',    action="store_true",        help="Boolean type argument")
    parser.add_argument('-b',    action="store",  type=str,  help="String type argument",  default="HejHopp")
    parser.add_argument('-c',    action="store",  type=int,  help="Integer type argument with default value", default=42)
    parser.add_argument('-d',    action="append", type=int,  help="Append values to list", dest='dlist', default=[] )
    parser.add_argument('-e',    action="store", type=int,   help="Integer type argument, no default")
    parser.add_argument('-f',    choices=['aa', 'bb', 'cc'], help="String choices argument")
    parser.add_argument('-g',    type=int, choices=range(1,10), help="Integer choices argument")
    
    args = parser.parse_args()

    if args.info:
        printInfo()
        return
    
    if args.a:
        print("Boolean argument")
        
    if args.b:
        print("String argument = " + args.b)
        
    if args.e:
        print("Integer argument no default = " + str(args.e) )
            
    if args.c:
        print("Integer argument default = " + str(args.c) )

    if args.dlist:
        print("List = ", args.dlist )
    
    return

    # Print options default
    parser.print_help()
    
#
#
def printInfo():
    print("Application name:   " + AppName    )
    print("Application Ver.:   " + AppVersion )
    print("Application desc.:  " + AppDesc    )
    print("File path:          " + scriptPath )
        

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
                

