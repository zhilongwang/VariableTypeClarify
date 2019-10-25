#ifndef _TRACE_H_
#define _TRACE_H_
#include<string>
#include<list>
#include<instruction.h>
using std::string;


class InstructionTrace{
    private:
        std::list<InsInfo> ins_list_;
        VAR_TYPE type;
    public:
        InstructionTrace(VAR_TYPE type){
            this.type = type;
        }
        bool addType(VAR_TYPE type);
        bool addIns(UINT32 addr, string disas);
        bool printList();
};
#endif