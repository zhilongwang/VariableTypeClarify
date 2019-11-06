 
def s16(value):
    return -(value & 0x80000000) | (value & 0x7fffffff)

def get_global_type(global_var, addr):
    
    for var in global_var :
        if var["address"] == addr:
            return var["type_name"]
    return None


def get_stack_type(functions, instruction):
    for fun in functions:
        if instruction["fun_name"] ==  fun["name"]:
            # print("%s :match: %s" % (instruction["fun_name"], fun["name"]))
            variables = fun.get("stack_variables")
            if variables == None:
                continue
            for var in variables:
                try:
                    if var["breg"] == "DW_OP_fbreg" :
                        # print("%x" % instruction["ctxt"]["ebp_offset"])

                        if 0 - var["offset"] == 0xffffffff - instruction["ctxt"]["ebp_offset"] + 8:
                            # print("ebp_offset:%d : offset: %d" % ((0xffffffff - instruction["ctxt"]["ebp_offset"] + 8), (0 - var["offset"])))
                            return var["type_name"]
                    elif var["breg"] == "DW_OP_breg4 (esp)" :
                        if var["offset"] == instruction["ctxt"]["esp_offset"] :
                            # print("esp_offset:%d : offset: %d" % ((instruction["ctxt"]["esp_offset"]), (var["offset"])))
                            return var["type_name"]
                except Exception as e:
                    print(var)
                    print(e)
                    
    return None

def get_global_type(global_var, addrinfo):
    for var in global_var :
        if var["offset"] == addrinfo["addr"]:
            print("%x == %x" % (var["offset"],addrinfo["addr"]))
            print("type_name:%s" % var["type_name"])
            return var["type_name"]
    return None