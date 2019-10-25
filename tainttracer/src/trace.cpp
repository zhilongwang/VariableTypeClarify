#include "trace.h"
#include "instruction.h"
#include "debug.h"
#include<string>
#include<iostream>
using std::string;
using std::iostream;
using std::endl;
using std::cerr;
#ifdef __DEBUG_TRACE
#define D(x) x
#else 
#define D(x)
#endif

bool InstructionTrace::addType(VAR_TYPE type){
    this.type = type;
}
bool InstructionTrace::addIns(UINT32 addr, string disas){
    ins_list_.push_back(InsInfo(addr, disas));
}
bool InstructionTrace::printList(){
    cout << GetTypeName(type) << endl;
    std::list<InsInfo>::iterator iter;
    for (iter = ins_list_.begin(); iter != ins_list_.end(); ++iter){
        cout << iter.disas << endl;
    } 
}