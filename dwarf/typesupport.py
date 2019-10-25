 
def s16(value):
    return -(value & 0x80000000) | (value & 0x7fffffff)

def get_global_type(global_var, addr):
    
    for var in global_var :
        if var["address"] == addr:
            return var["type_name"]
    return None


def get_stack_type(functions, funname, offset):
    correction = 20
    for fun in functions:
        if funname ==  fun["name"]:
            # print("%s :match: %s" % (funname, fun["name"]))
            variables = fun["stack_variables"]
            for var in variables:
                print("%d :addrmatch: %d" % (offset, var["dw_at_location_offset"] + correction))
                if offset  ==  var["dw_at_location_offset"] + correction:
                    return var["type_name"]
    return None
     