import pdb
import re
from typesupport import *

from type import AddrType,InsType
p1 = re.compile(r'[(](.*?)[)]', re.S)
p2 = re.compile(r'[{](.*?)[}]', re.S)
p3 = re.compile(r'[<](.*?)[>]', re.S)
p4 = re.compile(r'[|](.*?)[|]', re.S)

trace_max_length = 20
                
def extractfromtrace(tracelist, global_var, functions, result):
    with open(result, 'w') as output:
        for i in range(len(tracelist)):
            if tracelist[i]["type"] == InsType.LOAD:
                read_addrs = tracelist[i]["read"]
                trace_length = 1
                for addrinfo in read_addrs:
                    if addrinfo["type"] == AddrType.STK:
                        type_name =  get_stack_type(functions, tracelist[i], addrinfo)
                        if type_name != None:
                            # print(tracelist[i]["disas"]) 
                            # print(addrinfo["addr"])
                            ins_trace = ""
                            print(type_name)
                            ins_trace = ins_trace + type_name + "\n"
                            print(tracelist[i]["disas"])
                            ins_trace = ins_trace + tracelist[i]["disas"] + "\n"
                            taint_dic = set()
                        
                            # dict.has_key('Age')
                            write_addrs = tracelist[i]["write"]
                            for writeinfo in write_addrs:
                                taint_dic.add(writeinfo["addr"])
                            for j in range(i+1, len(tracelist)):
                                # taint_dic.discard(11)
                                # taint_dic.discard(12)
                                # taint_dic.discard(18)
                                read_addrs = tracelist[j]["read"]
                                ins_tainted = False
                                for readinfo in read_addrs:
                                    if readinfo["addr"] in taint_dic:
                                        ins_tainted = True
                                if ins_tainted == True:
                                    trace_length = trace_length + 1
                                    print(tracelist[j]["disas"])
                                    ins_trace = ins_trace + tracelist[j]["disas"] + "\n"
                                    write_addrs = tracelist[j]["write"]
                                    for writeinfo in write_addrs:
                                        taint_dic.add(writeinfo["addr"])
                                        # ins_trace = ins_trace + tracelist[j]["disas"] + "\n"
                                        # print(taint_dic)
                                else:
                                    write_addrs = tracelist[j]["write"]
                                    for writeinfo in write_addrs:
                                        taint_dic.discard(writeinfo["addr"])
                                if trace_length >= trace_max_length :
                                    break
                            if trace_length >= trace_max_length:
                                output.write(ins_trace)  
          
                    



def extract_op(line, tracelist):
    # get funname
    fun_names = re.findall(p4, line)
    if len(fun_names) == 1:
        tracelist[-1]["fun_name"] = fun_names[0]

    tracelist[-1]["read"] = []
    read_addrs = re.findall(p1, line)
    for addr in read_addrs:
        tracelist[-1]["read"].append({})
        addrinfo = re.findall(p3, addr)
        if len(addrinfo) != 0 :
            if  addrinfo[0] == 'S' :
                tracelist[-1]["read"][-1]["addr"] = int(addrinfo[1],16)
                tracelist[-1]["read"][-1]["type"] = AddrType.STK
            else:
                tracelist[-1]["read"][-1]["addr"] = int(addrinfo[1],16)
                tracelist[-1]["read"][-1]["type"] = AddrType.GBL
        else:
            tracelist[-1]["read"][-1]["addr"] = int(addr,16)
            tracelist[-1]["read"][-1]["type"] = AddrType.REG
        

    tracelist[-1]["write"] = []
    write_addrs = re.findall(p2, line)
    for addr in write_addrs:
        tracelist[-1]["write"].append({})
        addrinfo = re.findall(p3, addr)
        if len(addrinfo) != 0 :
            if  addrinfo[0] == 'S' :
                tracelist[-1]["write"][-1]["addr"] = int(addrinfo[1],16)
                tracelist[-1]["write"][-1]["type"] = AddrType.STK
            elif addrinfo[0] == 'N' :
                tracelist[-1]["write"][-1]["addr"] = int(addrinfo[1],16)
                tracelist[-1]["write"][-1]["type"] = AddrType.GBL

        else:
            tracelist[-1]["write"][-1]["addr"] = int(addr,16)
            tracelist[-1]["write"][-1]["type"] = AddrType.REG
    


def loadtrace(trace):

    lines=trace.split("\n", -1)
    tracelist = []
    nextdis = False
    for line in lines:
        if line.startswith('[LOAD]'):
            nextdis = True
            tracelist.append({})
            tracelist[-1]["type"] = InsType.LOAD
            extract_op(line, tracelist)
        elif line.startswith('[SPED]'):
            nextdis = True
            tracelist.append({})
            tracelist[-1]["type"] = InsType.SPRD
            extract_op(line, tracelist)
        elif line.startswith('[STOR]'):
            nextdis = True
            tracelist.append({})
            tracelist[-1]["type"] = InsType.STOR
            extract_op(line, tracelist)
        elif line.startswith('[CTXT]'):
            offsets = re.findall(p1, line)
            tracelist[-1]["ctxt"] = {} 
            tracelist[-1]["ctxt"]["esp_offset"] = int(offsets[0],16)
            tracelist[-1]["ctxt"]["ebp_offset"] = int(offsets[1],16)
            # print("esp_offset:%x" % tracelist[-1]["read"][-1]["esp_offset"])
            # print("ebp_offset:%x" % tracelist[-1]["read"][-1]["ebp_offset"])
        
        # print(tracelist[-1])

         
        elif line.startswith('0x') and nextdis:
            nextdis = False
            tracelist[-1]["disas"] = line
            # print(tracelist[-1])

    return tracelist

