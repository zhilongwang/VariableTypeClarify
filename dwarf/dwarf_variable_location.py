from __future__ import print_function
import sys
import pdb

# If pyelftools is not installed, the example can also run from the root or
# examples/ dir of the source distribution.
sys.path[0:0] = ['.', '..']

from elftools.common.py3compat import itervalues
from elftools.elf.elffile import ELFFile
from elftools.dwarf.descriptions import (
    describe_DWARF_expr, set_global_machine_arch, ExprDumper)
from elftools.dwarf.locationlists import (
    LocationEntry, LocationExpr, LocationParser)

from dwarf_expr import *

class ElfDwarf:
    """
    :elf_file_path(must): the path of elf file
    :addr2type_map: map address to type
    :base_type_map: map id to type 
    """
    def __init__(self,elf_file_path):
        self.elf_file_path = elf_file_path
        self.result_file_path = self.elf_file_path + ".type"
        # To save the basic information.
        self.base_type_map = {}
        self.addr2type_map = {}
        self.compile_unit_base_types = {}
        self.compile_unit_const_types = {}
        self.compile_unit_pointer_types = {}
        self.compile_unit_enumeration_types = {}
        self.compile_unit_union_types = {}
        self.compile_unit_array_types = {}
        self.compile_unit_subrange_types = {}
        self.compile_unit_structure_types = {}
        self.compile_unit_typedef_types = {}
        self.functions = []
        self.global_var = []

        # To support extract the dwarf
        self.loc_parser = None
        self.CU = None
        self.dwarfinfo = None
        #

        self.elfFilePath = filename
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
            location_lists = dwarfinfo.location_lists()

            # This is required for the descriptions module to correctly decode
            # register names contained in DWARF expressions.
            set_global_machine_arch(elffile.get_machine_arch())

            # Create a LocationParser object that parses the DIE attributes and
            # creates objects representing the actual location information.
            loc_parser = LocationParser(location_lists)

            for CU in dwarfinfo.iter_CUs():
                # DWARFInfo allows to iterate over the compile units contained in
                # the .debug_info section. CU is a CompileUnit object, with some
                # computed attributes (such as its offset in the section) and
                # a header which conforms to the DWARF standard. The access to
                # header elements is, as usual, via item-lookup.
                print('  Found a compile unit at offset %s, length %s' % (
                    CU.cu_offset, CU['unit_length']))
                self.CU = CU

                # A CU provides a simple API to iterate over all the DIEs in it.
                for die in CU.iter_DIEs():
                    # Go over all attributes of the DIE. Each attribute is an
                    # AttributeValue object (from elftools.dwarf.die), which we
                    # can examine.
                    if die.tag == 'DW_TAG_subprogram':
                        self.process_subprogram(die)
                    # elif die.tag == 'DW_TAG_variable' and 'DW_AT_external' in die.attributes:
                    #     self.process_global_var(die, structs, compile_unit)

    
    def process_subprogram(self, subprogram_die):

        # Print name, start_address and DW_AT_frame_base of the current function
        # print(subprogram_die)
        self.functions.append({})
        if 'DW_AT_name' in subprogram_die.attributes:
            self.functions[-1]["name"] = subprogram_die.attributes['DW_AT_name'].value
            print(self.functions[-1]["name"] )
        else:
            self.functions[-1]["name"] = None
            
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

        # variable_size, variable_type_name = self.get_variable_size_and_name(subprogram_variable_die, compile_unit)
        # self.functions[-1]["stack_variables"][-1]["size"] = variable_size
        # self.functions[-1]["stack_variables"][-1]["type_name"] = variable_type_name
            
        for attr in itervalues(DIE.attributes):
            # Check if this attribute contains location information
            # pdb.set_trace()
            if self.loc_parser.attribute_has_location(attr, self.CU['version']):
                print('   DIE %s. attr %s.' % (DIE.tag, attr.name))
                loc = loc_parser.parse_from_attribute(attr,
                                                    self.CU['version'])
                # We either get a list (in case the attribute is a
                # reference to the .debug_loc section) or a LocationExpr
                # object (in case the attribute itself contains location
                # information).
                if isinstance(loc, LocationExpr):
                    dwarf_expr_dumper = extract_DWARF_expr(loc.loc_expr, self.dwarfinfo.structs)
                    exp_info = dwarf_expr_dumper._str_parts
                    # print('      %s' % (
                    #     extract_DWARF_expr(loc.loc_expr,
                    #                         self.dwarfinfo.structs)))
                    # print('      %s' % (
                    #     describe_DWARF_expr(loc.loc_expr,
                    #                         self.dwarfinfo.structs)))
                # elif isinstance(loc, list):
                #     print(self.show_loclist(loc,
                #                     self.dwarfinfo,
                #                     indent='      '))

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

        

if __name__ == '__main__':
    if sys.argv[1] == '--test':
        for filename in sys.argv[2:]:
            elf = ElfDwarf(filename)