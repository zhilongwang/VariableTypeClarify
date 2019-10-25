import pdb
import re
from typesupport import *

from type import AddrType,InsType
p1 = re.compile(r'[(](.*?)[)]', re.S)
p2 = re.compile(r'[{](.*?)[}]', re.S)
p3 = re.compile(r'[<](.*?)[>]', re.S)
p4 = re.compile(r'[|](.*?)[|]', re.S)

                
def extractfromtrace(tracelist, global_var, functions, result):
    for i in range(len(tracelist)):
        if tracelist[i]["type"] == InsType.LOAD:
            read_addrs = tracelist[i]["read"]
            for addrinfo in read_addrs:
                if addrinfo["type"] == AddrType.STK:
                    # print("\t\t %s" % tracelist[i]["disas"]) 
                    # print("%s:  %x %x" % (tracelist[i]["fun_name"] , addrinfo["addr"]  , s16(addrinfo["addr"] )))
                    type_name =  get_stack_type(functions, tracelist[i]["fun_name"], s16(addrinfo["addr"]))
                    if type_name != None:
                        print(tracelist[i]["disas"]) 
                        print(addrinfo["addr"])
                        print(type_name)
                    



            

def extract_op(line, tracelist)
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
        if line.startswith('['):
            nextdis = True
            tracelist.append({})
            if line.startswith('[LOAD]'):
                tracelist[-1]["type"] = InsType.LOAD
                extract_op(line, tracelist)
            elif line.startswith('[SPED]'):
                tracelist[-1]["type"] = InsType.SPRD
                extract_op(line, tracelist)
            elif line.startswith('[STOR]'):
                tracelist[-1]["type"] = InsType.STOR
                extract_op(line, tracelist)
            

            
            # print(tracelist[-1])

         
        elif line.startswith('0x') and nextdis:
            nextdis = False
            tracelist[-1]["disas"] = line
            # print(tracelist[-1]["disas"])

    return tracelist

