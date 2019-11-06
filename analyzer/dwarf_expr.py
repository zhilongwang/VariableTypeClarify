import logging
l = logging.getLogger("dwarf_expr")

from elftools.dwarf.descriptions import (
    describe_DWARF_expr, set_global_machine_arch, ExprDumper)

_DWARF_EXPR_DUMPER_CACHE = {}

def extract_DWARF_expr(expr, structs):
    """ Textual description of a DWARF expression encoded in 'expr'.
        structs should come from the entity encompassing the expression - it's
        needed to be able to parse it correctly.
    """
    # Since this function can be called a lot, initializing a fresh new
    # ExprDumper per call is expensive. So a rudimentary caching scheme is in
    # place to create only one such dumper per instance of structs.
    cache_key = id(structs)
    if cache_key not in _DWARF_EXPR_DUMPER_CACHE:
        _DWARF_EXPR_DUMPER_CACHE[cache_key] = \
            ExprDumper(structs)
    dwarf_expr_dumper = _DWARF_EXPR_DUMPER_CACHE[cache_key]
    dwarf_expr_dumper.clear()
    dwarf_expr_dumper.process_expr(expr)
    return dwarf_expr_dumper
        
def get_type_size_and_name(absolute_type_reference_number, compile_unit, CU_TYPE):
    try:
        if absolute_type_reference_number in CU_TYPE["base"]:
            size = CU_TYPE["base"][absolute_type_reference_number]['size']
            name = CU_TYPE["base"][absolute_type_reference_number]['name']
            return size, name
        elif absolute_type_reference_number in CU_TYPE["const"]:
            absolute_const_type_reference_number = CU_TYPE["const"][absolute_type_reference_number]['dw_at_type'].value + compile_unit.cu_offset
            size, name =  get_type_size_and_name(absolute_const_type_reference_number, compile_unit, CU_TYPE)
            return size, name
        elif absolute_type_reference_number in CU_TYPE["pointer"]:
            # print(self.compile_unit_pointer_types[absolute_type_reference_number])
            size = CU_TYPE["pointer"][absolute_type_reference_number]['size']
            name = None
            try:
                name = CU_TYPE["pointer"][absolute_type_reference_number]['name']
            except KeyError:
                name = "pointer"
                # print("No name KeyError")
            return size, name 
        elif absolute_type_reference_number in CU_TYPE["enumeration"]:
            size = CU_TYPE["enumeration"][absolute_type_reference_number]['size']
            name = CU_TYPE["enumeration"][absolute_type_reference_number]['name']
            return size, name
        elif absolute_type_reference_number in CU_TYPE["union"]:
            size = CU_TYPE["union"][absolute_type_reference_number]['size']
            name = CU_TYPE["union"][absolute_type_reference_number]['name']
            return name    
        elif absolute_type_reference_number in CU_TYPE["array"]:
            absolute_array_element_type_reference_number = CU_TYPE["array"][absolute_type_reference_number]['dw_at_type'].value + compile_unit.cu_offset
            size, name =  get_type_size_and_name(absolute_array_element_type_reference_number, compile_unit, CU_TYPE)
            return size, name
        elif absolute_type_reference_number in CU_TYPE["structure"]:
            # print(CU_TYPE["structure"][absolute_type_reference_number])
            size = CU_TYPE["structure"][absolute_type_reference_number]['size']
            name = None
            try:
                name = CU_TYPE["structure"][absolute_type_reference_number]['name']
            except KeyError:
                name = "Unknow"
                print("No name KeyError")
            return size, name
        elif absolute_type_reference_number in CU_TYPE["typedef"]:
            absolute_typedef_type_reference_number = CU_TYPE["typedef"][absolute_type_reference_number]['dw_at_type'].value + compile_unit.cu_offset
            size, name = get_type_size_and_name(absolute_typedef_type_reference_number, compile_unit, CU_TYPE)
            return size, name
        else:
            print("Type with absolute reference number %d not implemented." % absolute_type_reference_number)
            #sys.exit(1)
            return None, None
    except KeyError:
        return None, None

def get_array_size_name(dw_tag_variable, array_type_reference_number, compile_unit, CU_TYPE):
        array_element_type_reference_number = dw_tag_variable.attributes['DW_AT_type'].value
        absolute_array_element_type_reference_number = array_element_type_reference_number + compile_unit.cu_offset
        
        for child in CU_TYPE["array"][absolute_array_element_type_reference_number]['die'].iter_children():
            if child.tag == 'DW_TAG_subrange_type':
                upper_bound = child.attributes['DW_AT_upper_bound'].value
                number_of_elements = upper_bound + 1
        
        element_size, name = get_type_size_and_name(absolute_array_element_type_reference_number, compile_unit, CU_TYPE)
        if element_size is None:
            return None
        else:
            return number_of_elements * element_size, name

def get_variable_size_and_name(dw_tag_variable, compile_unit, CU_TYPE):  
    try:
        type_reference_number = dw_tag_variable.attributes['DW_AT_type'].value  # the ref to the type, e.g. <0xb1>
    except KeyError:
        print("Variable has no DW_AT_type, maybe some strange DW_AT_abstract_origin thing?")
        return None, None
    
    absolute_type_reference_number = compile_unit.cu_offset + type_reference_number
    if absolute_type_reference_number in CU_TYPE["base"]:
        size, name = get_type_size_and_name(absolute_type_reference_number, compile_unit, CU_TYPE)
        # print(size)
        # print(name)
        return size, name
    elif absolute_type_reference_number in CU_TYPE["pointer"]:
        size, name = get_type_size_and_name(absolute_type_reference_number, compile_unit, CU_TYPE)
        return size, name
    elif absolute_type_reference_number in CU_TYPE["enumeration"]:
        size, name = get_type_size_and_name(absolute_type_reference_number, compile_unit, CU_TYPE)
        return size, name
    elif absolute_type_reference_number in CU_TYPE["union"]:
        size, name = get_type_size_and_name(absolute_type_reference_number, compile_unit, CU_TYPE)
        return size, name
    elif absolute_type_reference_number in CU_TYPE["const"]:
        size, name = get_type_size_and_name(absolute_type_reference_number, compile_unit, CU_TYPE)
        return size, name
    elif absolute_type_reference_number in CU_TYPE["array"]:
        absolute_array_element_type_reference_number = CU_TYPE["array"][absolute_type_reference_number]['dw_at_type'].value + compile_unit.cu_offset
        size, name = get_array_size_name(dw_tag_variable, absolute_type_reference_number, compile_unit, CU_TYPE)
        # print("size:%d, name:%s" % (size, name))
        return size, name
    elif absolute_type_reference_number in CU_TYPE["structure"]:
        size, name = get_type_size_and_name(absolute_type_reference_number, compile_unit, CU_TYPE)
        return size, name
    elif absolute_type_reference_number in CU_TYPE["typedef"]:
        size, name = get_type_size_and_name(absolute_type_reference_number, compile_unit, CU_TYPE)
        return size, name
    else:
        print()
        l.debug("Not implemented type with absolute reference 0x%x for variable [%s]" )
        return None, None