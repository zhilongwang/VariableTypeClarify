import logging
l = logging.getLogger("typesupport")

def s16(value):
    return -(value & 0x80000000) | (value & 0x7fffffff)

def get_global_type(global_var, addr):
    
    for var in global_var :
        if var["address"] == addr:
            return var["type_name"]
    return None


def get_stack_type(functions, instruction, addrinfo):
    for fun in functions:
        if instruction["fun_name"] ==  fun["name"]:
            #print("%s :match: %s" % (instruction["fun_name"], fun["name"]))
            # print(instruction["disas"])
            variables = fun.get("stack_variables")
            if variables == None:
                continue
            for var in variables:
                try:
                    if var["breg"] == "DW_OP_fbreg" :
                        #print("DW_OP_fbreg\t %d:%d :%s" % (0 - var["offset"], 0xffffffff - instruction["ctxt"]["ebp_offset"] + 9, var["name"]))
                        
                        if 0 - var["offset"] == 0xffffffff - instruction["ctxt"]["ebp_offset"] + 9:
        
                            return var["type_name"]
                    elif var["breg"] == "DW_OP_breg4 (esp)" :
                        #print("DW_OP_breg4 (esp)\t %d:%d" %(var["offset"], instruction["ctxt"]["esp_offset"]) )
                        if var["offset"] == instruction["ctxt"]["esp_offset"] :
                            return var["type_name"]
                    elif var["breg"] == "DW_OP_addr" :
                        #print("DW_OP_addr\t %d:%d" % (var["offset"],addrinfo["addr"]))
                        if var["offset"] == addrinfo["addr"]:
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