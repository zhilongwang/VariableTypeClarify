import logging
l = logging.getLogger("CU_process")

def get_compile_unit_types(compile_unit):
    # I need to reset them to {} (again) because this function is called for every compile_unit
    CU_TYPE = {}
    compile_unit_base_types = {}
    compile_unit_const_types = {}
    compile_unit_pointer_types = {}
    compile_unit_enumeration_types = {}
    compile_unit_union_types = {}
    compile_unit_array_types = {}
    compile_unit_subrange_types = {}
    compile_unit_structure_types = {}
    compile_unit_typedef_types = {}
    # A CU provides a simple API to iterate over all the DIEs in it.
    for DIE in compile_unit.iter_DIEs():
       
        type_die = DIE
        if DIE.tag == 'DW_TAG_base_type':
            # print(DIE)
            compile_unit_base_types[type_die.offset] = {}
            try:   
                compile_unit_base_types[type_die.offset]['size'] = type_die.attributes['DW_AT_byte_size'].value
                #print(type_die)
                compile_unit_base_types[type_die.offset]['name'] = type_die.attributes['DW_AT_name'].value
            except KeyError:
                print("KeyError: DW_AT_name")

        if DIE.tag == 'DW_TAG_const_type':
            compile_unit_const_types[type_die.offset] = {}
            if 'DW_AT_type' in type_die.attributes:
                compile_unit_const_types[type_die.offset]['dw_at_type'] = type_die.attributes['DW_AT_type']
            else:
                print("DW_TAG_const_type without attribute DW_AT_type. I saw this kind of type referenced by a DW_TAG_pointer_type, which is okay, because the pointer has its own DW_AT_byte size.")
                
        elif DIE.tag == 'DW_TAG_pointer_type':
            compile_unit_pointer_types[type_die.offset] = {}
            compile_unit_pointer_types[type_die.offset]['size'] = type_die.attributes['DW_AT_byte_size'].value 
            try:    
                compile_unit_pointer_types[type_die.offset]['name'] = type_die.attributes['DW_AT_name'].value 
            except KeyError:
                # FIXME in future.
                compile_unit_pointer_types[type_die.offset]['name'] = 'upointer'
                print("KeyError: DW_TAG_pointer_type")

        elif DIE.tag == 'DW_TAG_enumeration_type':
            compile_unit_enumeration_types[type_die.offset] = {}
            compile_unit_enumeration_types[type_die.offset]['size'] = type_die.attributes['DW_AT_byte_size'].value  
        
        elif DIE.tag == 'DW_TAG_union_type':
            compile_unit_union_types[type_die.offset] = {}
            compile_unit_union_types[type_die.offset]['size'] = type_die.attributes['DW_AT_byte_size'].value  
                
        elif DIE.tag == 'DW_TAG_array_type':
            compile_unit_array_types[type_die.offset] = {}
            compile_unit_array_types[type_die.offset]['die'] = type_die
            compile_unit_array_types[type_die.offset]['dw_at_type'] = type_die.attributes['DW_AT_type']
            
        elif DIE.tag == 'DW_TAG_typedef':
            if 'dw_at_type' in type_die.attributes:
                try:  
                    compile_unit_typedef_types[type_die.offset] = {}
                    compile_unit_typedef_types[type_die.offset]['die'] = type_die
                    compile_unit_typedef_types[type_die.offset]['dw_at_type'] = type_die.attributes['DW_AT_type']    
                except KeyError:
                    print("DW_TAG_typedef")
                
        elif DIE.tag == 'DW_TAG_structure_type':
            
            compile_unit_structure_types[type_die.offset] = {}
            if 'DW_AT_declaration' in type_die.attributes:
                # print(type_die.attributes['DW_AT_declaration'])
                l.debug("Spec says this means: 'Incomplete, non-defining, or separate entity declaration'")
                l.debug("Setting size to 0.")
                compile_unit_structure_types[type_die.offset]['size'] = 0
                # TODO: check if one can derive from the value if it is a separate decl. and implement sep. decl.
            else:
                compile_unit_structure_types[type_die.offset]['size'] = type_die.attributes['DW_AT_byte_size'].value
        
        elif DIE.tag == 'DW_TAG_subrange_type':
            compile_unit_subrange_types[type_die.offset] = {}
            
            if 'DW_AT_type' in type_die.attributes:
                '''The subrange entry may have a DW_AT_type attribute to describe the type of object,
                called the basis type, of whose values this subrange is a subset'''                
                compile_unit_subrange_types[type_die.offset]['dw_at_type'] = type_die.attributes['DW_AT_type']
            
            if 'DW_AT_upper_bound' in type_die.attributes:
                '''The subrange entry may have the attributes DW_AT_lower_bound and DW_AT_upper_bound
                to describe, respectively, the lower and upper bound values of the subrange'''                
                compile_unit_subrange_types[type_die.offset]['upper_bound'] = type_die.attributes['DW_AT_upper_bound']
                if 'DW_AT_lower_bound' in type_die.attributes:
                    compile_unit_subrange_types[type_die.offset]['lower_bound'] = type_die.attributes['DW_AT_lower_bound']            
                            
                else:
                    '''If the lower bound value is missing, the value is assumed to be a language-dependent default
                    constant. The default lower bound value for C or C++ is 0.'''                     
                    compile_unit_subrange_types[type_die.offset]['lower_bound'] = 0
            
                    
            elif 'DW_AT_count' in type_die.attributes:
                '''The DW_AT_upper_bound attribute may be replaced by a DW_AT_count attribute, whose value
                describes the number of elements in the subrange rather than the value of the last element'''                 
                compile_unit_subrange_types[type_die.offset]['count'] = type_die.attributes['DW_AT_count']
                
        else:
            pass


    CU_TYPE["base"] = compile_unit_base_types
    CU_TYPE["const"] = compile_unit_const_types
    CU_TYPE["pointer"] = compile_unit_pointer_types
    CU_TYPE["enumeration"] = compile_unit_enumeration_types
    CU_TYPE["union"] = compile_unit_union_types
    CU_TYPE["array"] = compile_unit_array_types
    CU_TYPE["subrange"] = compile_unit_subrange_types
    CU_TYPE["structure"] = compile_unit_structure_types
    CU_TYPE["typedef"] = compile_unit_typedef_types 

    return CU_TYPE