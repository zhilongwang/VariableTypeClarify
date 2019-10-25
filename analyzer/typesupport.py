 
def s16(value):
    return -(value & 0x80000000) | (value & 0x7fffffff)

def get_global_type(global_var, addr):
    
    for var in global_var :
        if var["address"] == addr:
            return var["type_name"]
    return None


def get_stack_type(functions, instruction, addrinfo):
    correction = 20
    for fun in functions:
        if instruction["fun_name"] ==  fun["name"]:
            # print("%s :match: %s" % (instruction["fun_name"], fun["name"]))
            variables = fun["stack_variables"]
            for var in variables:
                try:
                    # print(var["breg"])
                    if var["breg"] == "DW_OP_fbreg" :
                        # print(instruction["ctxt"])
                        # print("%x" % instruction["ctxt"]["ebp_offset"])

                        if 0 - var["offset"] == 0xffffffff - instruction["ctxt"]["ebp_offset"] + 8:
                            # print("ebp_offset:%d : offset: %d" % ((0xffffffff - instruction["ctxt"]["ebp_offset"] + 8), (0 - var["offset"])))
                            return var["type_name"]
                    elif var["breg"] == "DW_OP_breg4 (esp)" :
                        # print("%d" % addrinfo["esp_offset"])
                        # print("esp_offset:%d : offset: %d" % ((addrinfo["esp_offset"]), (var["offset"])))
                        if var["offset"] == instruction["ctxt"]["esp_offset"] :
                            # print("esp_offset:%d : offset: %d" % ((instruction["ctxt"]["esp_offset"]), (var["offset"])))
                            return var["type_name"]
                    # addrinfo["esp_offset"]
                    # addrinfo["ebp_offset"]
                    # # print("%d :addrmatch: %d" % (offset, var["offset"] + correction))
                    # if offset  ==  var["offset"] + correction:
                    #     return var["type_name"]
                except Exception as e:
                    print(var)
                    print(e)
                    
    return None
     