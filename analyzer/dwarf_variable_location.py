from __future__ import print_function
import subprocess
from subprocess import *
import getopt
import sys
import pdb
import os

# If pyelftools is not installed, the example can also run from the root or
# examples/ dir of the source distribution.
sys.path[0:0] = ['.', '..', '../pyelftools']

from elftools.common.py3compat import itervalues
from elftools.elf.elffile import ELFFile
from elftools.dwarf.descriptions import (
    describe_DWARF_expr, set_global_machine_arch, ExprDumper)
from elftools.dwarf.locationlists import (
    LocationEntry, LocationExpr, LocationParser)

from dwarf_expr import *
from CU_process import *
from extract import *
from type import *

class ElfDwarf:
    """
    :elf_file_path(must): the path of elf file
    :addr2type_map: map address to type
    :base_type_map: map id to type 
    """
    def __init__(self, elf_file_path, inputfile, resultdir):
        self.elf_file_path = elf_file_path
        self.result_file_path = self.elf_file_path + ".type"
        self.inputfile = inputfile
        self.resultdir = resultdir
        # To save the basic information.
        self.base_type_map = {}
        self.addr2type_map = {}
        self.CU_TYPE = None
        # self.compile_unit_base_types = {}
        # self.compile_unit_const_types = {}
        # self.compile_unit_pointer_types = {}
        # self.compile_unit_enumeration_types = {}
        # self.compile_unit_union_types = {}
        # self.compile_unit_array_types = {}
        # self.compile_unit_subrange_types = {}
        # self.compile_unit_structure_types = {}
        # self.compile_unit_typedef_types = {}
        self.functions = []
        self.global_var = []

        # To support extract the dwarf
        self.loc_parser = None
        self.CU = None
        self.dwarfinfo = None
        #
        print('Processing file:', self.elf_file_path)
        with open(self.elf_file_path, 'rb') as f:
            elffile = ELFFile(f)

            if not elffile.has_dwarf_info():
                print('  file has no DWARF info')
                return

            # get_dwarf_info returns a DWARFInfo context object, which is the
            # starting point for all DWARF-based processing in pyelftools.
            self.dwarfinfo = elffile.get_dwarf_info()

            # The location lists are extracted by DWARFInfo from the .debug_loc
            # section, and returned here as a LocationLists object.
            location_lists = self.dwarfinfo.location_lists()

            # This is required for the descriptions module to correctly decode
            # register names contained in DWARF expressions.
            set_global_machine_arch(elffile.get_machine_arch())

            # Create a LocationParser object that parses the DIE attributes and
            # creates objects representing the actual location information.
            self.loc_parser = LocationParser(location_lists)

            for CU in self.dwarfinfo.iter_CUs():
                # DWARFInfo allows to iterate over the compile units contained in
                # the .debug_info section. CU is a CompileUnit object, with some
                # computed attributes (such as its offset in the section) and
                # a header which conforms to the DWARF standard. The access to
                # header elements is, as usual, via item-lookup.
                print('  Found a compile unit at offset %s, length %s' % (
                    CU.cu_offset, CU['unit_length']))
                self.CU = CU
                self.CU_TYPE = get_compile_unit_types(self.CU)
                # print(self.CU_TYPE)

                # A CU provides a simple API to iterate over all the DIEs in it.
                for die in CU.iter_DIEs():
                    # Go over all attributes of the DIE. Each attribute is an
                    # AttributeValue object (from elftools.dwarf.die), which we
                    # can examine.
                    if die.tag == 'DW_TAG_subprogram':
                        self.process_subprogram(die)
                    elif die.tag == 'DW_TAG_variable' and 'DW_AT_external' in die.attributes:
                        self.process_global_var(die)
                
            pincmd = ['../pin/pin', '-t', '../TaintAnalysisWithPin/obj-ia32/taint.so', '--', elf_file_path, "<", self.inputfile]
            print(pincmd)
            result = self.resultdir + '/' + elf_file_path+'.out'
            print(result)
            try:
                # trace = subprocess.check_output(pincmd)
                process = subprocess.Popen(pincmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                with open(self.inputfile, 'rb') as inputfile:
                    for line in inputfile.readlines():
                        print("Give Std Input:%s" % line)
                        process.stdin.write(line)
                trace = process.communicate()[0]
                process.stdin.close()
                tracelist = loadtrace(trace)
                extractfromtrace(tracelist, self.global_var, self.functions, result)
                
            except subprocess.CalledProcessError, e:
                print("run pin error(%s)")
                return None

    def show_loclist(self, loclist, dwarfinfo, indent):
        """ Display a location list nicely, decoding the DWARF expressions
            contained within.
        """
        d = []
        for loc_entity in loclist:
            if isinstance(loc_entity, LocationEntry):
                d.append('%s <<%s>>' % (
                    loc_entity,
                    describe_DWARF_expr(loc_entity.loc_expr, dwarfinfo.structs)))
            else:
                d.append(str(loc_entity))
        return '\n'.join(indent + s for s in d)

        
    def process_global_var(self, DIE):
        self.global_var.append({})
        try:
            self.global_var[-1]["name"] = DIE.attributes['DW_AT_name'].value
        except KeyError:
            #print "DIE has no attribute 'DW_AT_name'"
            self.global_var["name"] = None

        variable_size, variable_type_name = get_variable_size_and_name(DIE, self.CU, self.CU_TYPE)
        print(" name:%s, size:%d, type_name:%s" % (self.global_var[-1]["name"],variable_size, variable_type_name))
        self.global_var[-1]["size"] = variable_size
        self.global_var[-1]["type_name"] = variable_type_name

        for attr in itervalues(DIE.attributes):
            # Check if this attribute contains location information
            # pdb.set_trace()
            if self.loc_parser.attribute_has_location(attr, self.CU['version']):
                # print('   DIE %s. attr %s.' % (DIE.tag, attr.name))
                loc = self.loc_parser.parse_from_attribute(attr,
                                                    self.CU['version'])
                # We either get a list (in case the attribute is a
                # reference to the .debug_loc section) or a LocationExpr
                # object (in case the attribute itself contains location
                # information).
                if isinstance(loc, LocationExpr):
                    dwarf_expr_dumper = extract_DWARF_expr(loc.loc_expr, self.dwarfinfo.structs)
                    exp_info = dwarf_expr_dumper._str_parts
                    for item in exp_info:
                        baseregister = item[0:item.find(':')]
                        offset = int(item[item.find(':')+2:], 16)
                        print("%s:%s:%d:%s" % (self.global_var[-1]["name"], baseregister, offset,self.global_var[-1]["type_name"]))
                        self.global_var[-1]["offset"] = offset
                        self.global_var[-1]["breg"] = baseregister 


    
    def process_subprogram(self, subprogram_die):

        # Print name, start_address and DW_AT_frame_base of the current function
        # print(subprogram_die)
        self.functions.append({})
        if 'DW_AT_name' in subprogram_die.attributes:
            self.functions[-1]["name"] = subprogram_die.attributes['DW_AT_name'].value
            print(self.functions[-1]["name"] )
        else:
            self.functions[-1]["name"] = None
            
        try:
            dw_at_frame_base = subprogram_die.attributes['DW_AT_frame_base']
        except:
            # I am not sure if every subprogram has a DW_AT_frame_base
            print("subprogram [%s]  has no a DW_AT_frame_base (and thus no stack variables (?)). Skipping." % self.functions[-1]['name'])
            self.functions.pop()
            return

        if subprogram_die.has_children:    
            #print "subprogram [%s] has children!" % self.functions[-1]['name']
            
            self.functions[-1]["stack_variables"] = []
            
            # Print names of all variables that are children of the current DIE (the current function)
            for child in subprogram_die.iter_children():
                if child.tag == 'DW_TAG_variable' or child.tag == 'DW_TAG_formal_parameter' :
                    self.process_subprogram_variable(child)
                    

    def process_subprogram_variable(self, DIE):
        if self.functions[-1].get("stack_variables") is None:
            return
        self.functions[-1]["stack_variables"].append({})
        try:
            self.functions[-1]["stack_variables"][-1]["name"] = DIE.attributes['DW_AT_name'].value
        except KeyError:
            #print "subprogram_variable_die has no attribute 'DW_AT_name'"
            self.functions[-1]["stack_variables"][-1]["name"] = None

        variable_size, variable_type_name = get_variable_size_and_name(DIE, self.CU, self.CU_TYPE)
        self.functions[-1]["stack_variables"][-1]["size"] = variable_size
        self.functions[-1]["stack_variables"][-1]["type_name"] = variable_type_name
            
        for attr in itervalues(DIE.attributes):
            # Check if this attribute contains location information
            # pdb.set_trace()
            if self.loc_parser.attribute_has_location(attr, self.CU['version']):
                # print('   DIE %s. attr %s.' % (DIE.tag, attr.name))
                loc = self.loc_parser.parse_from_attribute(attr,
                                                    self.CU['version'])
                # We either get a list (in case the attribute is a
                # reference to the .debug_loc section) or a LocationExpr
                # object (in case the attribute itself contains location
                # information).
                if isinstance(loc, LocationExpr):
                    dwarf_expr_dumper = extract_DWARF_expr(loc.loc_expr, self.dwarfinfo.structs)
                    exp_info = dwarf_expr_dumper._str_parts
                    for item in exp_info:
                        baseregister = item[0:item.find(':')]
                        offset = int(item[item.find(':')+1:])
                        print("%s:%s:%s:%d:%s" % (self.functions[-1]["name"], self.functions[-1]["stack_variables"][-1]["name"],baseregister, offset,self.functions[-1]["stack_variables"][-1]["type_name"]))
                        self.functions[-1]["stack_variables"][-1]["offset"] = offset
                        self.functions[-1]["stack_variables"][-1]["breg"] = baseregister 
        
        if "breg" not in self.functions[-1]["stack_variables"][-1]:
            self.functions[-1]["stack_variables"].pop()

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
                        "program", "inputfile", "result"
                    ]

        opts, args = getopt.getopt(sys.argv[1:], "p:i:r:", usage_opt)
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    filename = None
    inputfile = None
    resultdir = None
    for opt, arg in opts:
        if opt in ("-p", "--program"):
            filename = arg
            checkpath(filename)
        elif opt in ("-i", "--input"):
            inputfile = arg
            checkpath(inputfile)
        elif opt in ("-r", "--result"):
            resultdir = arg
            checkpath(resultdir)
        else:
            assert False, "unhandled option"  

    print(filename)
    print(inputfile)
    print(resultdir)
    elf = ElfDwarf(filename, inputfile, resultdir)            

        

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        usage()
    else:
        getopts()

    # if sys.argv[1] == '--p':
    #     for filename in sys.argv[2:]:
    #         elf = ElfDwarf(filename)