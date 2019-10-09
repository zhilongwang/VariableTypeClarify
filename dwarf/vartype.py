#-------------------------------------------------------------------------------
# elftools example: examine_dwarf_info.py
#
# An example of examining information in the .debug_info section of an ELF file.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from __future__ import print_function
from elftools.dwarf.structs import DWARFStructs
from elftools.construct.lib.container import ListContainer
from type import AddrType
from elftools.dwarf.descriptions import ExprDumper
import sys
import pdb

# If pyelftools is not installed, the example can also run from the root or
# examples/ dir of the source distribution.
sys.path[0:0] = ['.', '..']

from elftools.elf.elffile import ELFFile

class ElfDwarf:
    """
    :elf_file_path(must): the path of elf file
    :addr2type_map: map address to type
    :base_type_map: map id to type 
    """
    def __init__(self,elf_file_path):
        self.elf_file_path = elf_file_path
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
        
            self.call_frame_information_entries = self.dwarfinfo.CFI_entries()  
            

            for CU in self.dwarfinfo.iter_CUs():
                # DWARFInfo allows to iterate over the compile units contained in
                # the .debug_info section. CU is a CompileUnit object, with some
                # computed attributes (such as its offset in the section) and
                # a header which conforms to the DWARF standard. The access to
                # header elements is, as usual, via item-lookup.
                print('  Found a compile unit at offset %s, length %s' % (
                    CU.cu_offset, CU['unit_length']))

                self.process_compile_unit(self.dwarfinfo, elffile, CU)

        print("Global Variable[%d]:",len(self.global_var))
        for var in self.global_var :
            print("\tname:%s, address:%x, type:%s, size: %d" % (var["name"],var["address"],var["type_name"],var["size"]))

        for fun in self.functions:
            
            print("Function: %s" % fun["name"])
            variables = fun["stack_variables"]
            for var in variables:
                print("\tname:%s, offset:%x, type:%s, size: %d" % (var["name"],var["dw_at_location_offset"],var["type_name"],var["size"]))
            

                # # The first DIE in each compile unit describes it.
                # top_DIE = CU.get_top_DIE()
                # print('    Top DIE with tag=%s' % top_DIE.tag)

                # # We're interested in the filename...
                # print('    name=%s' % top_DIE.get_full_path())

                # # Display DIEs recursively starting with top_DIE
                # self.die_info_rec(top_DIE)

    def process_compile_unit(self, dwarf_info, pyelftools_elf_file, compile_unit):    
        # We need this to parse the DW_TAG_variable DW_AT_location
        # This has to be done for each compile unit (I think I got errors otherwise)
        structs = DWARFStructs(
            little_endian=pyelftools_elf_file.little_endian,
            dwarf_format=compile_unit.dwarf_format(),
            address_size=compile_unit['address_size']
        )
        
        self.get_compile_unit_types(compile_unit)
        
            # A CU provides a simple API to iterate over all the DIEs in it.
        for DIE in compile_unit.iter_DIEs():        
            self.process_die(DIE, structs, compile_unit)

    def process_die(self, die, structs, compile_unit):    
        if die.tag == 'DW_TAG_subprogram':
            self.process_subprogram(die, structs, compile_unit)
        elif die.tag == 'DW_TAG_variable' and 'DW_AT_external' in die.attributes:
            self.process_global_var(die, structs, compile_unit)
            #self.process_subprogram_variable(child, structs, compile_unit)
            

    def get_dw_op_call_frame_cfa(self, function_address):
        #assert dwarf_info.has_CFI()
        
        # Call Frame Information (CFI): 
        # A Common Information Entry (CIE) data block for each compilation (unit?),
        # followed by one or more Frame Definition Entries (FDEs), one for each function in the compilation.
        # ==> The call_frame_information_entries list contains e.g.
        # [cie, fde, fde, fde, cie, fde, cie, fde, fde, fde, fde, fde, ...]
        # call_frame_information_entries[2].get_decoded()[0][0]['cfa'].reg
        # 13
        # call_frame_information_entries[2].get_decoded()[0][0]['cfa'].offset
        # 0
        # call_frame_information_entry is of type CIE if its property 'cie' is None
        # it is of type FDE if its property 'cie' is an CIE Object
        # Alternatively, one could look at the type
        
        #call_frame_information_entries = dwarf_info.CFI_entries()  # TODO: this should be moved out of this func to not re-do it so often
        
        for e in self.call_frame_information_entries:
            if e.get_decoded()[0][0]['pc'] == function_address:  # In case it is still too slow, create a dict first and avoid re-searching the call_frame_information_entries again and again
                #print "Found matching CIE (?)"
                break
        else:
            print("Did not find matching CIE for function at address %d" % function_address)
            sys.exit()
            
        return self.call_frame_information_entries[2].get_decoded()[0][0]['cfa']
        


    def process_subprogram(self, subprogram_die, structs, compile_unit):

        # Print name, start_address and DW_AT_frame_base of the current function
        print(subprogram_die)
        self.functions.append({})
        if 'DW_AT_name' in subprogram_die.attributes:
            self.functions[-1]["name"] = subprogram_die.attributes['DW_AT_name'].value
            print(self.functions[-1]["name"] )
        else:
            self.functions[-1]["name"] = None
            
        '''A subroutine entry may have either a DW_AT_low_pc and DW_AT_high_pc pair of attributes
        or a DW_AT_ranges attribute whose values encode the contiguous or non-contiguous address
        ranges, respectively, of the machine instructions generated for the subroutine'''    
        if 'DW_AT_low_pc' in subprogram_die.attributes:
            self.functions[-1]["address"] = subprogram_die.attributes['DW_AT_low_pc'].value
            self.functions[-1]["address_high"] = subprogram_die.attributes['DW_AT_high_pc'].value
        elif 'DW_AT_ranges' in subprogram_die.attributes:
            # TODO
            pass
        
        elif 'DW_AT_external' in subprogram_die.attributes and self.functions[-1]["name"] != "main" :
            #print "External subroutine. Popping it."
            self.functions.pop()
            print("skip external function")
            return
        
        elif 'DW_AT_inline' in subprogram_die.attributes and \
            subprogram_die.attributes['DW_AT_inline'].value in [constants.DW_INL_inlined, constants.DW_INL_declared_inlined]:
                #print "This is an inlined function. Popping it."
                self.functions.pop()
                print("skip inline function")
                return
        
        elif 'DW_AT_specification' in subprogram_die.attributes:
            # Incomplete, non-defining, or separate declaration corresponding to a declaration
            #print "This function is an incomplete, non-defining, or separate declaration corresponding to a declaration. Popping it."
            self.functions.pop() 
            print("skip specification function")
            return
        
        elif 'DW_AT_abstract_origin' in subprogram_die.attributes:
            #print "Spec says about this function: 'Inline instances of inline subprograms out-of-line instances of inline subprograms'. Popping it."
            self.functions.pop()
            print("skip abstract function")
            return
        
        #elif 'DW_AT_prototyped' in subprogram_die.attributes and \
        #subprogram_die.attributes['DW_AT_prototyped'].value not in ['', 0]:
        #''' In C there is a difference between the types of self.functions declared
        #using function prototype style declarations and those declared using
        #non-prototype declarations. A subroutine entry declared with a function
        #prototype style declaration may have a DW_AT_prototyped attribute,
        #which is a flag. '''
        #print "Function is subroutine prototype. Don't know what this means. Popping it."
        #self.functions.pop()
        #return
        
        else:
            print("Function is neither of the above cases. What is it?")
        
        try:
            dw_at_frame_base = subprogram_die.attributes['DW_AT_frame_base']
        except:
            # I am not sure if every subprogram has a DW_AT_frame_base
            print("subprogram [%s]  has no a DW_AT_frame_base (and thus no stack variables (?)). Skipping." % self.functions[-1]['name'])
            self.functions.pop()
            
            return
            
        print(dw_at_frame_base)
        if self.attribute_has_location_list(dw_at_frame_base):
            if dw_at_frame_base.form == 'DW_FORM_exprloc':
                print(subprogram_die.attributes['DW_AT_frame_base'].value)
                self.functions[-1]["location_list_offset"] = subprogram_die.attributes['DW_AT_frame_base'].value[0]
            else:
                # Location list offset
                print("Function's location list offset: ")
                print("0x%x" % subprogram_die.attributes['DW_AT_frame_base'].value)
                self.functions[-1]["location_list_offset"] = subprogram_die.attributes['DW_AT_frame_base'].value
                self.functions[-1]["dw_op_call_frame_cfa"] = self.get_dw_op_call_frame_cfa(self.functions[-1]["address"])
                print(dw_at_frame_base)
        
        elif dw_at_frame_base.form == 'DW_FORM_exprloc' :  #TODO: Maybe this check is not precise enough
            #DW_OP_call_frame_cfa
            if dw_at_frame_base.value[0] == 0x9c:
                #print 'DW_OP_call_frame_cfa implementation has to go here for function [%s]' % self.functions[-1]['name']
                self.functions[-1]["dw_op_call_frame_cfa"] = get_dw_op_call_frame_cfa(self.functions[-1]["address"])
            else:
                print('Unsupported DW_AT_frame_base value:', dw_at_frame_base.value)
                #sys.exit(-1)
        elif dw_at_frame_base.form == 'DW_FORM_block1' and dw_at_frame_base.value == [125, 0]:
                #print "AAA"
                self.functions[-1]["dw_op_call_frame_cfa"] = get_dw_op_call_frame_cfa(self.functions[-1]["address"])
                #print self.functions[-1]
                #print "BBB"

        else:
            print('Unsupported DW_AT_frame_base.form [%s] for Function [%s]' % (dw_at_frame_base.form, self.functions[-1]['name']))
            #sys.exit(-1)

            
        if subprogram_die.has_children:    
            #print "subprogram [%s] has children!" % self.functions[-1]['name']
            
            self.functions[-1]["stack_variables"] = []
            
            # Print names of all variables that are children of the current DIE (the current function)
            for child in subprogram_die.iter_children():
                if child.tag == 'DW_TAG_variable' or child.tag == 'DW_TAG_formal_parameter' :
                    self.process_subprogram_variable(child, structs, compile_unit)



    def attribute_has_location_list(self, attr):
        """ Only some attributes can have location list values, if they have the
            required DW_FORM (loclistptr "class" in DWARF spec v3)
        """
        if (attr.name in (  'DW_AT_location', 'DW_AT_string_length',
                            'DW_AT_const_value', 'DW_AT_return_addr',
                            'DW_AT_data_member_location', 'DW_AT_frame_base',
                            'DW_AT_segment', 'DW_AT_static_link',
                            'DW_AT_use_location', 'DW_AT_vtable_elem_location')):
            if attr.form in ('DW_FORM_data4', 'DW_FORM_data8', 'DW_FORM_exprloc'):
                return True
        return False

        
    def get_type_size_and_name(self, absolute_type_reference_number, compile_unit):
        if absolute_type_reference_number in self.compile_unit_base_types:
            size = self.compile_unit_base_types[absolute_type_reference_number]['size']
            name = self.compile_unit_base_types[absolute_type_reference_number]['name']
            return size, name
        elif absolute_type_reference_number in self.compile_unit_const_types:
            absolute_const_type_reference_number = self.compile_unit_const_types[absolute_type_reference_number]['dw_at_type'].value + compile_unit.cu_offset
            size, name =  self.get_type_size_and_name(absolute_const_type_reference_number, compile_unit)
            return size, name
        elif absolute_type_reference_number in self.compile_unit_pointer_types:
            # print(self.compile_unit_pointer_types[absolute_type_reference_number])
            size = self.compile_unit_pointer_types[absolute_type_reference_number]['size']
            name = None
            try:
                name = self.compile_unit_pointer_types[absolute_type_reference_number]['name']
            except KeyError:
                name = "pointer"
                print("No name KeyError")

            return size, name 
        elif absolute_type_reference_number in self.compile_unit_enumeration_types:
            size = self.compile_unit_enumeration_types[absolute_type_reference_number]['size']
            name = self.compile_unit_enumeration_types[absolute_type_reference_number]['name']
            return size, name
        elif absolute_type_reference_number in self.compile_unit_union_types:
            size = self.compile_unit_union_types[absolute_type_reference_number]['size']
            name = self.compile_unit_union_types[absolute_type_reference_number]['name']
            return name    
        elif absolute_type_reference_number in self.compile_unit_array_types:
            absolute_array_element_type_reference_number = self.compile_unit_array_types[absolute_type_reference_number]['dw_at_type'].value + compile_unit.cu_offset
            size, name =  self.get_type_size_and_name(absolute_array_element_type_reference_number, compile_unit)
            return size, name
        elif absolute_type_reference_number in self.compile_unit_structure_types:
            print(self.compile_unit_structure_types[absolute_type_reference_number])
            size = self.compile_unit_structure_types[absolute_type_reference_number]['size']
            name = None
            try:
                name = self.compile_unit_structure_types[absolute_type_reference_number]['name']
            except KeyError:
                name = "Unknow"
                print("No name KeyError")
            return size, name
        elif absolute_type_reference_number in self.compile_unit_typedef_types:
            absolute_typedef_type_reference_number = self.compile_unit_typedef_types[absolute_type_reference_number]['dw_at_type'].value + compile_unit.cu_offset
            size, name = self.get_type_size_and_name(absolute_typedef_type_reference_number, compile_unit)
            return size, name
        else:
            print("Type with absolute reference number %d not implemented." % absolute_type_reference_number)
            #sys.exit(1)
            return None

    def get_array_size_name(self, dw_tag_variable, array_type_reference_number, compile_unit):
        array_element_type_reference_number = dw_tag_variable.attributes['DW_AT_type'].value
        absolute_array_element_type_reference_number = array_element_type_reference_number + compile_unit.cu_offset
        
        for child in self.compile_unit_array_types[absolute_array_element_type_reference_number]['die'].iter_children():
            if child.tag == 'DW_TAG_subrange_type':
                upper_bound = child.attributes['DW_AT_upper_bound'].value
                number_of_elements = upper_bound + 1
        
        element_size, name = self.get_type_size_and_name(absolute_array_element_type_reference_number, compile_unit)
        if element_size is None:
            return None
        else:
            return number_of_elements * element_size, name

    def get_variable_size_and_name(self, dw_tag_variable, compile_unit):  
        print(dw_tag_variable)  
        try:
            type_reference_number = dw_tag_variable.attributes['DW_AT_type'].value  # the ref to the type, e.g. <0xb1>
        except KeyError:
            print("Variable has no DW_AT_type, maybe some strange DW_AT_abstract_origin thing?")
            return 0
        
        absolute_type_reference_number = compile_unit.cu_offset + type_reference_number
        if absolute_type_reference_number in self.compile_unit_base_types:
            size, name = self.get_type_size_and_name(absolute_type_reference_number, compile_unit)
            print(size)
            print(name)
            return size, name
        elif absolute_type_reference_number in self.compile_unit_pointer_types:
            size, name = self.get_type_size_and_name(absolute_type_reference_number, compile_unit)
            return size, name
        elif absolute_type_reference_number in self.compile_unit_enumeration_types:
            size, name = self.get_type_size_and_name(absolute_type_reference_number, compile_unit)
            return size, name
        elif absolute_type_reference_number in self.compile_unit_union_types:
            size, name = self.get_type_size_and_name(absolute_type_reference_number, compile_unit)
            return size, name
        elif absolute_type_reference_number in self.compile_unit_const_types:
            size, name = self.get_type_size_and_name(absolute_type_reference_number, compile_unit)
            return size, name
        elif absolute_type_reference_number in self.compile_unit_array_types:
            absolute_array_element_type_reference_number = self.compile_unit_array_types[absolute_type_reference_number]['dw_at_type'].value + compile_unit.cu_offset
            size, name = self.get_array_size_name(dw_tag_variable, absolute_type_reference_number, compile_unit)
            print("size:%d, name:%s" % (size, name))
            return size, name
        elif absolute_type_reference_number in self.compile_unit_structure_types:
            size, name = self.get_type_size_and_name(absolute_type_reference_number, compile_unit)
            return size, name
        elif absolute_type_reference_number in self.compile_unit_typedef_types:
            size, name = self.get_type_size_and_name(absolute_type_reference_number, compile_unit)
            return size, name
        else:
            print("Not implemented type with absolute reference 0x%x for variable [%s]" % (absolute_type_reference_number, dw_tag_variable.attributes['DW_AT_name'].value))
            return None
            #sys.exit(1)

    def get_dw_at_location_offset(self, structs, expression):
        visitor = ExprDumper(structs)
        visitor.process_expr(expression)
        print("Full DW_AT_location as string: ")
        print(visitor.get_str())
        dw_at_location_as_string = visitor.get_str()
        first_part, second_part = dw_at_location_as_string.split()
        print("first_part:")
        print(first_part)
        print("second_part:")
        print(second_part)
        #print first_part   # 'DW_OP_fbreg:'
        print(first_part)
        print(second_part)
        assert first_part == 'DW_OP_fbreg:' or first_part == 'DW_OP_addr:'
        #print "Second part of DW_AT_location: ",
        #print second_part  # e.g. '-20'
        print(type(second_part))
        return int(second_part, 16)

    def calculate_position(self, functions):
        
        #if "location_list_offset" in functions[-1]:
            #dw_at_location_offset = functions[-1]["stack_variables"][-1]["dw_at_location_offset"]
            #location_list_offset = functions[-1]["location_list_offset"]
            #location_list = location_lists.get_location_list_at_offset(location_list_offset)
            #first_part, second_part = location_list[0].loc_expr
            #return second_part + dw_at_location_offset
        if "dw_op_call_frame_cfa" in functions[-1]:
            return "r" + str(functions[-1]['dw_op_call_frame_cfa'].reg) + "+" + str(functions[-1]['dw_op_call_frame_cfa'].offset)
            #sys.exit()
        else:
            print("Case not implemented yet. [%s]" % functions[-1])
            return None
    
    def process_global_var(self, subprogram_variable_die, structs, compile_unit):
        print(len(self.global_var))
        self.global_var.append({})

        variable_size, variable_type_name = self.get_variable_size_and_name(subprogram_variable_die, compile_unit)
        print("size:%d, name:%s" % (variable_size, variable_type_name))
        self.global_var[-1]["size"] = variable_size
        self.global_var[-1]["type_name"] = variable_type_name
        try:
            self.global_var[-1]["name"] = subprogram_variable_die.attributes['DW_AT_name'].value
        except KeyError:
            #print "subprogram_variable_die has no attribute 'DW_AT_name'"
            self.global_var["name"] = None
            

        try:
            dw_at_location_value = subprogram_variable_die.attributes['DW_AT_location'].value
            dw_at_location_form = subprogram_variable_die.attributes['DW_AT_location'].form
            print("location")
            print(dw_at_location_value)
            print(dw_at_location_form)
        except KeyError:
            print("variable declared but not defined")
            self.global_var.pop(-1)
            return
            #sys.exit(1)
            

        if dw_at_location_form == 'DW_FORM_data4':

            #print "Unhandled var"
            #print subprogram_variable_die
            #print self.functions[-1]["stack_variables"][-1]
            #dw_at_location_offset = location_lists.get_location_list_at_offset(dw_at_location_value)
            part1, part2 = calculate_position_dw_form_sec_offset(structs, subprogram_variable_die)
            
            if part2 is not None:
                self.global_var[-1]["position"] = part1
                self.global_var[-1]["dw_at_location_offset"] = part2
            else:
                self.global_var.pop()
            #self.functions[-1]["stack_variables"][-1]["dw_at_location_offset"] = dw_at_location_offset
            #self.functions[-1]["stack_variables"][-1]["position"] = calculate_position(self.functions)    



        # In the case of base type stack variables,
        # we need to combine dw_at_location_offset and a location list entry, or a CFA value (?)
        elif type(dw_at_location_value) == ListContainer and dw_at_location_value[0] == 0x3:
            dw_at_location_offset = self.get_dw_at_location_offset(structs, dw_at_location_value)
            self.global_var[-1]["address"] = dw_at_location_offset
            print(self.global_var[-1]["address"])
        
        elif subprogram_variable_die.attributes['DW_AT_location'].form == 'DW_FORM_sec_offset':
            part1, part2 = calculate_position_dw_form_sec_offset(structs, subprogram_variable_die)
            if part2 is not None:
                self.global_var[-1]["position"] = part1
                self.global_var[-1]["dw_at_location_offset"] = part2
            else:
                self.global_var.pop()
                
            
        #elif type(dw_at_location_value) == ListContainer and \
        #len(dw_at_location_value) > 2 and \
        #subprogram_variable_die.attributes['DW_AT_location'].form  == 'DW_FORM_exprloc':
            #print "Ignoring variable %s with expr_loc opcode 0x%x" % \
                #(self.global_var[-1]["name"], subprogram_variable_die.attributes['DW_AT_location'].value[0])
        
        elif dw_at_location_value in range(0x50, 0x6f+1) or \
            type(dw_at_location_value) == ListContainer and dw_at_location_value[0] in range(0x50, 0x6f+1):
            #print "Variable stored in a register. We can safely ignore that."
            self.global_var.pop()
            
        elif dw_at_location_value[0] in range(0x71, 0x8f+1) or \
            type(dw_at_location_value) == ListContainer and dw_at_location_value[0] in range(0x71, 0x8f+1):
            # This is case DW_OP_bregn
            #print "The single operand of the DW_OP_bregn operations provides a signed LEB128 offset from the specified register."
                
            self.global_var.pop()
            
            # We need to be sure that there are no stack locations encoded this way
            if type(dw_at_location_value) == ListContainer:
                assert dw_at_location_value[0] != 0x7e
            else:
                assert dw_at_location_value[0] != 0x7e  # 0x7e corresponds to r13, i.e. the stack register on ARM.
            
            
        elif dw_at_location_value == 0x3 or \
            type(dw_at_location_value) == ListContainer and dw_at_location_value[0] == 0x3:
            #print "Variable stored at a constant address. We can safely ignore that."
            self.global_var.pop()        
            
        else:
            print("Not yet implemented (maybe not relevant to us):")
            print("Variable_name: %s, type(dw_at_location_value): %s, value: %s" % \
                (subprogram_variable_die.attributes['DW_AT_name'].value,  type(dw_at_location_value), str(dw_at_location_value)))
            # TODO: pop variable as it is no stack variable?
            # self.global_var[-1].pop()
            #sys.exit(-1)


    def process_subprogram_variable(self, subprogram_variable_die, structs, compile_unit):

        if self.functions[-1].get("stack_variables") is None:
            return
        self.functions[-1]["stack_variables"].append({})
        variable_size, variable_type_name = self.get_variable_size_and_name(subprogram_variable_die, compile_unit)
        self.functions[-1]["stack_variables"][-1]["size"] = variable_size
        self.functions[-1]["stack_variables"][-1]["type_name"] = variable_type_name
        try:
            self.functions[-1]["stack_variables"][-1]["name"] = subprogram_variable_die.attributes['DW_AT_name'].value
        except KeyError:
            #print "subprogram_variable_die has no attribute 'DW_AT_name'"
            self.functions[-1]["stack_variables"][-1]["name"] = None
            

        try:
            dw_at_location_value = subprogram_variable_die.attributes['DW_AT_location'].value
            dw_at_location_form = subprogram_variable_die.attributes['DW_AT_location'].form
            print("location")
            print(dw_at_location_value)
            print(dw_at_location_form)
        except KeyError:
            print("variable declared but not defined")
            self.functions[-1]["stack_variables"].pop(-1)
            return
            #sys.exit(1)
            

        if dw_at_location_form == 'DW_FORM_data4':

            #print "Unhandled var"
            #print subprogram_variable_die
            #print self.functions[-1]["stack_variables"][-1]
            #dw_at_location_offset = location_lists.get_location_list_at_offset(dw_at_location_value)
            part1, part2 = calculate_position_dw_form_sec_offset(structs, subprogram_variable_die)
            
            if part2 is not None:
                self.functions[-1]["stack_variables"][-1]["position"] = part1
                self.functions[-1]["stack_variables"][-1]["dw_at_location_offset"] = part2
            else:
                self.functions[-1]["stack_variables"].pop()
            #self.functions[-1]["stack_variables"][-1]["dw_at_location_offset"] = dw_at_location_offset
            #self.functions[-1]["stack_variables"][-1]["position"] = calculate_position(self.functions)    



        # In the case of base type stack variables,
        # we need to combine dw_at_location_offset and a location list entry, or a CFA value (?)
        elif type(dw_at_location_value) == ListContainer and dw_at_location_value[0] == 0x91:
            dw_at_location_offset = self.get_dw_at_location_offset(structs, dw_at_location_value)
            self.functions[-1]["stack_variables"][-1]["dw_at_location_offset"] = dw_at_location_offset
            self.functions[-1]["stack_variables"][-1]["position"] = self.calculate_position(self.functions)    
            print(self.functions[-1]["stack_variables"][-1]["position"])
        
        elif subprogram_variable_die.attributes['DW_AT_location'].form == 'DW_FORM_sec_offset':
            part1, part2 = calculate_position_dw_form_sec_offset(structs, subprogram_variable_die)
            if part2 is not None:
                self.functions[-1]["stack_variables"][-1]["position"] = part1
                self.functions[-1]["stack_variables"][-1]["dw_at_location_offset"] = part2
            else:
                self.functions[-1]["stack_variables"].pop()
                
            
        #elif type(dw_at_location_value) == ListContainer and \
        #len(dw_at_location_value) > 2 and \
        #subprogram_variable_die.attributes['DW_AT_location'].form  == 'DW_FORM_exprloc':
            #print "Ignoring variable %s with expr_loc opcode 0x%x" % \
                #(self.functions[-1]["stack_variables"][-1]["name"], subprogram_variable_die.attributes['DW_AT_location'].value[0])
        
        elif dw_at_location_value in range(0x50, 0x6f+1) or \
            type(dw_at_location_value) == ListContainer and dw_at_location_value[0] in range(0x50, 0x6f+1):
            #print "Variable stored in a register. We can safely ignore that."
            self.functions[-1]["stack_variables"].pop()
            
        elif dw_at_location_value[0] in range(0x71, 0x8f+1) or \
            type(dw_at_location_value) == ListContainer and dw_at_location_value[0] in range(0x71, 0x8f+1):
            # This is case DW_OP_bregn
            #print "The single operand of the DW_OP_bregn operations provides a signed LEB128 offset from the specified register."
                
            self.functions[-1]["stack_variables"].pop()
            
            # We need to be sure that there are no stack locations encoded this way
            if type(dw_at_location_value) == ListContainer:
                assert dw_at_location_value[0] != 0x7e
            else:
                assert dw_at_location_value[0] != 0x7e  # 0x7e corresponds to r13, i.e. the stack register on ARM.
            
            
        elif dw_at_location_value == 0x3 or \
            type(dw_at_location_value) == ListContainer and dw_at_location_value[0] == 0x3:
            #print "Variable stored at a constant address. We can safely ignore that."
            self.functions[-1]["stack_variables"].pop()        
            
        else:
            print("Not yet implemented (maybe not relevant to us):")
            print("Variable_name: %s, type(dw_at_location_value): %s, value: %s" % \
                (subprogram_variable_die.attributes['DW_AT_name'].value,  type(dw_at_location_value), str(dw_at_location_value)))
            # TODO: pop variable as it is no stack variable?
            # self.functions[-1]["stack_variables"][-1].pop()
            #sys.exit(-1)


    def get_compile_unit_types(self, compile_unit):
        # I need to reset them to {} (again) because this function is called for every compile_unit
        
        # A CU provides a simple API to iterate over all the DIEs in it.
        for DIE in compile_unit.iter_DIEs():
            type_die = DIE
            if DIE.tag == 'DW_TAG_base_type':
                self.compile_unit_base_types[type_die.offset] = {}
                try:   
                    self.compile_unit_base_types[type_die.offset]['size'] = type_die.attributes['DW_AT_byte_size'].value
                    #print(type_die)
                    self.compile_unit_base_types[type_die.offset]['name'] = type_die.attributes['DW_AT_name'].value
                except KeyError:
                    print("KeyError: DW_AT_name")

            if DIE.tag == 'DW_TAG_const_type':
                self.compile_unit_const_types[type_die.offset] = {}
                if 'DW_AT_type' in type_die.attributes:
                    self.compile_unit_const_types[type_die.offset]['dw_at_type'] = type_die.attributes['DW_AT_type']
                else:
                    print("DW_TAG_const_type without attribute DW_AT_type. I saw this kind of type referenced by a DW_TAG_pointer_type, which is okay, because the pointer has its own DW_AT_byte size.")
                    
            elif DIE.tag == 'DW_TAG_pointer_type':
                self.compile_unit_pointer_types[type_die.offset] = {}
                self.compile_unit_pointer_types[type_die.offset]['size'] = type_die.attributes['DW_AT_byte_size'].value 
                try:    
                    self.compile_unit_pointer_types[type_die.offset]['name'] = type_die.attributes['DW_AT_name'].value 
                except KeyError:
                    print("KeyError: DW_TAG_pointer_type")
            elif DIE.tag == 'DW_TAG_enumeration_type':
                self.compile_unit_enumeration_types[type_die.offset] = {}
                self.compile_unit_enumeration_types[type_die.offset]['size'] = type_die.attributes['DW_AT_byte_size'].value  
            
            elif DIE.tag == 'DW_TAG_union_type':
                self.compile_unit_union_types[type_die.offset] = {}
                self.compile_unit_union_types[type_die.offset]['size'] = type_die.attributes['DW_AT_byte_size'].value  
                    
            elif DIE.tag == 'DW_TAG_array_type':
                self.compile_unit_array_types[type_die.offset] = {}
                self.compile_unit_array_types[type_die.offset]['die'] = type_die
                self.compile_unit_array_types[type_die.offset]['dw_at_type'] = type_die.attributes['DW_AT_type']
                
            elif DIE.tag == 'DW_TAG_typedef':
                if 'dw_at_type' in type_die.attributes:
                    try:  
                        self.compile_unit_typedef_types[type_die.offset] = {}
                        self.compile_unit_typedef_types[type_die.offset]['die'] = type_die
                        self.compile_unit_typedef_types[type_die.offset]['dw_at_type'] = type_die.attributes['DW_AT_type']    
                    except KeyError:
                        print("DW_TAG_typedef")
                   
            elif DIE.tag == 'DW_TAG_structure_type':
                print(type_die)
                self.compile_unit_structure_types[type_die.offset] = {}
                if 'DW_AT_declaration' in type_die.attributes:
                    print(type_die.attributes['DW_AT_declaration'])
                    print("Spec says this means: 'Incomplete, non-defining, or separate entity declaration'")
                    print("Setting size to 0.")
                    self.compile_unit_structure_types[type_die.offset]['size'] = 0
                    # TODO: check if one can derive from the value if it is a separate decl. and implement sep. decl.
                else:
                    self.compile_unit_structure_types[type_die.offset]['size'] = type_die.attributes['DW_AT_byte_size'].value
            
            elif DIE.tag == 'DW_TAG_subrange_type':
                self.compile_unit_subrange_types[type_die.offset] = {}
                
                if 'DW_AT_type' in type_die.attributes:
                    '''The subrange entry may have a DW_AT_type attribute to describe the type of object,
                    called the basis type, of whose values this subrange is a subset'''                
                    self.compile_unit_subrange_types[type_die.offset]['dw_at_type'] = type_die.attributes['DW_AT_type']
                
                if 'DW_AT_upper_bound' in type_die.attributes:
                    '''The subrange entry may have the attributes DW_AT_lower_bound and DW_AT_upper_bound
                    to describe, respectively, the lower and upper bound values of the subrange'''                
                    self.compile_unit_subrange_types[type_die.offset]['upper_bound'] = type_die.attributes['DW_AT_upper_bound']
                    if 'DW_AT_lower_bound' in type_die.attributes:
                        self.compile_unit_subrange_types[type_die.offset]['lower_bound'] = type_die.attributes['DW_AT_lower_bound']            
                                
                    else:
                        '''If the lower bound value is missing, the value is assumed to be a language-dependent default
                        constant. The default lower bound value for C or C++ is 0.'''                     
                        self.compile_unit_subrange_types[type_die.offset]['lower_bound'] = 0
                
                        
                elif 'DW_AT_count' in type_die.attributes:
                    '''The DW_AT_upper_bound attribute may be replaced by a DW_AT_count attribute, whose value
                    describes the number of elements in the subrange rather than the value of the last element'''                 
                    self.compile_unit_subrange_types[type_die.offset]['count'] = type_die.attributes['DW_AT_count']
                    
            else:
                pass

        #return compile_unit_base_types, compile_unit_array_types  # TODO: this can be removed, right?

    def die_info_rec(self,die, indent_level="    "):
        """ A recursive function for showing information about a DIE and its
            children.
        """
        #print(indent_level + 'DIE tag=%s' % die.tag)
        self.get_die_info(die, indent_level)
        child_indent = indent_level + '  '
        for child in die.iter_children():
            self.die_info_rec(child, child_indent)


    def get_die_info(self,die, indent_level):
        print(indent_level + 'DIE tag=%s' % die.tag)
        print(die)
        if die.tag == 'DW_TAG_base_type':
            try:  
                type_name = die.attributes['DW_AT_name'].value
                type_id = die.abbrev_code
                print("%x :DW_TAG_base_type %s" % (type_id,type_name))
                self.base_type_map[type_id] = type_name
            except KeyError:
                print("Variable has no DW_AT_name, maybe some strange DW_AT_abstract_origin thing?")
            
            # pdb.set_trace()
        elif die.tag == 'DW_TAG_subprogram':
            fun_name = die.attributes['DW_AT_name'].value
            self.addr2type_map[fun_name] = {}
            print("fun name:%s" % fun_name)

        elif die.tag == 'DW_TAG_variable':
            try:     
                var_type = die.attributes['DW_AT_type'].value
                var_loc = decode_LEB18(die.attributes['DW_AT_location'].value[1:0])
                var_name = die.attributes['DW_AT_name'].value
                print("name:%s, type:%x, loc:" % (var_name, var_type))
                print(var_loc)
                print(type(var_loc))
            except KeyError:
                print("Variable has no DW_AT_name, maybe some strange DW_AT_abstract_origin thing?")
            


def decode_LEB18(streamlist):
    """Read a varint from `stream`"""
    value = 0
    for b in reversed(streamlist):
        value = (value << 7) + (b & 0x7F)
    if streamlist[-1] & 0x40:
        # negative -> sign extend
        value |= - (1 << (7 * len(streamlist)))
    return value

        # get base type
        

if __name__ == '__main__':
    if sys.argv[1] == '--test':
        for filename in sys.argv[2:]:
        #     streamlist = [0x91, 0xa8, 0x7f]
        #     print("%d" % decode_LEB18(streamlist[1:]))
            elf = ElfDwarf(filename)
