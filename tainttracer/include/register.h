#ifndef _REGISTER_H_
#define _REGISTER_H_
#include "pin.H"
#include<string>
#include<trace.h>
#include<instruction.h>
#include<shadowmem.h>
using std::string;

string GetREGName(REG reg);
class ShadowReg{
private:
    UINT32 shadow_reg_[287]={0x0};
public:

    UINT32 checkREG(REG reg);
    bool taintREG(REG reg, UINT32 addr);
    UINT32 removeREG(REG reg);
};

#endif