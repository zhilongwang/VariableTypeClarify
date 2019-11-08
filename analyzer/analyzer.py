import re
import os
import sys
import time
import getopt
import string
import logging
import subprocess
import showprocess
from dwarf_variable_location import *

logging.getLogger('CU_process').setLevel(logging.ERROR)
logging.getLogger('dwarf_expr').setLevel(logging.ERROR)
logging.getLogger('dwarf_variable_location').setLevel(logging.DEBUG)
logging.getLogger('typesupport').setLevel(logging.WARNING)

def parse(cpppath, update, resultdir):
    compiler = None
    suffix = None
    if cpppath.endswith('.cpp'):
        compiler = "g++-4.8"
        suffix = ".cpp"
    elif cpppath.endswith('.c') :
        compiler = "gcc-4.8"
        suffix = ".c"
    if compiler != None:
        srcname = cpppath.split(b'/')[-1]
        # resultfile = resultdir +'/' + srcname[0:srcname.find(suffix)]
        elffile = cpppath[0:cpppath.find(suffix)]
        # print(srcname[0:srcname.find('.cpp')])
        # print(elffile)
        # print(resultfile)
        result = resultdir + '/' + elffile.split(b'/')[-1] + ".out" 
        if os.path.exists(result):
            print("Skip processed file: %s" % result)
            return
        print(cpppath)
        compilercmd = [compiler, '-fno-pie', '-fno-pic', '-fno-stack-protector', '-g3', '-o', elffile, cpppath, '-static', '-m32']
        try:
            print(compilercmd)
            trace = subprocess.check_output(compilercmd)
            print(trace)
            if trace.find("error:") == -1:
                elf = ElfDwarf(elffile, None, resultdir)

        except subprocess.CalledProcessError as e:
            print("run gcc error(%s)")
            return None
    
        
def dirlist(path, update, result, process_bar): 
    allfile = []

    filelist =  os.listdir(path)  
    for filename in filelist:  
        filepath = os.path.join(path, filename)  
        if os.path.isdir(filepath):  
            dirlist(filepath, update, result, process_bar)  
        else:  
            allfile.append(filepath)
            #print filepath
            if os.path.exists(filepath):
                process_bar.show_process(filepath)
                parse(filepath, update, result)
            else:
                print("[%s] file does not exist" %(filepath))

def dir_size_calculation(path):
    filenum = 0
    filelist =  os.listdir(path)  
    for filename in filelist:  
        filepath = os.path.join(path, filename)  
        if os.path.isdir(filepath):  
            filenum += dir_size_calculation(filepath)  
        else:  
            if os.path.exists(filepath):
                filenum += 1
    
    return filenum

def usage():
    print("usage: %s [options]" % __file__)
    print("   -p, --program  the program to be run")
    print("   -i, --input    input of the program")
    print("   -r, --result   dir to save the result")
    print("")
    print("Example: python %s -p ./target_program -i ./inputfile -r resultdir" % __file__)                    

def checkpath(path):
    if not os.path.exists(path):
        try:
           os.makedirs(path)
        except OSError as exc: # Guard against race condition
            raise

def getopts():
    try:
        usage_opt = [
                        "srcdir", "program", "inputfile", "result", "update",
                    ]

        opts, args = getopt.getopt(sys.argv[1:], "s:p:i:r:u", usage_opt)
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    filename = None
    inputfile = None
    resultdir = None
    srcdir = None
    update = False
    for opt, arg in opts:
        if opt in ("-s", "--srcdir"):
            srcdir = arg
        elif opt in ("-p", "--program"):
            filename = arg
        elif opt in ("-i", "--input"):
            inputfile = arg
        elif opt in ("-r", "--result"):
            resultdir = arg
        elif opt in ("-u", "--update"):
            update = True
        else:
            print(opt)
            assert False, "unhandled option"  

    print(srcdir)
    process_bar = showprocess.ShowProcess(dir_size_calculation(srcdir), 'OK')

    if srcdir != None and os.path.exists(srcdir):
        dirlist(srcdir, update, resultdir, process_bar)
    else:
        print("[%s] dir does not exist" %(objdir))
         

if __name__ == '__main__':
     # debug
    # process_bar = showprocess.ShowProcess(dir_size_calculation("/home/zzw169/Desktop/VariableTypeClarify/testcases/leetcode/algorithms/cpp"), 'OK')
    # dirlist("/home/zzw169/Desktop/VariableTypeClarify/testcases/leetcode/algorithms/cpp", True, "/home/zzw169/Desktop/VariableTypeClarify/results", process_bar)

    if len(sys.argv) <= 1:
        usage()
    else:
        getopts()
       
    # if sys.argv[1] == '--p':
    #     for filename in sys.argv[2:]:
    #         elf = ElfDwarf(filename)