#include "register.h"
#include "debug.h"
#include<string>
#include<iostream>
using std::string;
using std::iostream;
using std::endl;

#ifdef __DEBUG_ANALYIZE
#define D(x) x
#else 
#define D(x)
#endif
string GetREGName(REG reg){
  string reg_name; 
	reg_name="UNKnowReg:"+reg; 
	switch(reg){

    //case REG_RAX:  regsTainted.push_front(REG_RAX);
    case REG_EAX:  reg_name="REG_EAX"; 
    	break;
    case REG_AX:   reg_name="REG_AX"; 
    	break;
    case REG_AH:   reg_name="REG_AH"; 
    	break;
    case REG_AL:   reg_name="REG_AL"; 
         break;

    //case REG_RBX:  regsTainted.push_front(REG_RBX);
    case REG_EBX:  reg_name="REG_EBX"; 
    	break;
    case REG_BX:   reg_name="REG_BX"; 
    	break; 
    case REG_BH:   reg_name="REG_BH"; 
    	break; 
    case REG_BL:   reg_name="REG_BL"; 
         break;

    //case REG_RCX:  regsTainted.push_front(REG_RCX); 
    case REG_ECX:  reg_name="REG_ECX"; 
    	break;
    case REG_CX:   reg_name="REG_CX"; 
    	break;
    case REG_CH:   reg_name="REG_CH"; 
    	break;
    case REG_CL:   reg_name="REG_CL"; 
    	break;

    //case REG_RDX:  regsTainted.push_front(REG_RDX); 
    case REG_EDX:  reg_name="REG_EDX"; 
    	break; 
    case REG_DX:   reg_name="REG_DX"; 
    	break;
    case REG_DH:   reg_name="REG_DH"; 
    	break;
    case REG_DL:   reg_name="REG_DL"; 
    	break;

    //case REG_RDI:  regsTainted.push_front(REG_RDI); 
    case REG_EDI:  reg_name="REG_EDI"; 
    	break; 
    case REG_DI:   reg_name="REG_DI"; 
    	break;

    //case REG_RSI:  regsTainted.push_front(REG_RSI); 
    case REG_ESI:  reg_name="REG_ESI"; 
    	break;
    case REG_SI:   reg_name="REG_SI"; 
    	break;
    case REG_EFLAGS: reg_name="REG_EFLAGS"; 
    	break;

    case REG_XMM0: reg_name="REG_XMM0"; 
    	break;
    case REG_XMM1: reg_name="REG_XMM1"; 
    	break;
    case REG_XMM2: reg_name="REG_XMM2"; 
    	break;
    case REG_XMM3: reg_name="REG_XMM3"; 
    	break;
    case REG_XMM4: reg_name="REG_XMM4"; 
    	break;
    case REG_XMM5: reg_name="REG_XMM5"; 
    	break;
    case REG_XMM6: reg_name="REG_XMM6"; 
    	break;
    case REG_XMM7: reg_name="REG_XMM7"; 
    	break;
    default:
      reg_name="UNKnowReg";  
  }
  return reg_name;
}

/* ===================================================================== */
/* funcions for Tainting */
/* ===================================================================== */
UINT32 ShadowReg::checkREG(REG reg)
{
	return shadow_reg_[reg];
}

bool ShadowReg::taintREG(REG reg, UINT32 addr)
{
	if (shadow_reg_[reg] == addr){
		D(cout << "\t\t\t--" << REG_StringShort(reg) << " is already tainted" << endl;)
	}

	switch(reg){

		//case REG_RAX:  regsTainted.push_front(REG_RAX);
		case REG_EAX:  shadow_reg_[REG_EAX]=addr; 
		case REG_AX:   shadow_reg_[REG_AX]=addr; 
		case REG_AH:   shadow_reg_[REG_AH]=addr;
		case REG_AL:   shadow_reg_[REG_AL]=addr; 
			       break;

			       //case REG_RBX:  regsTainted.push_front(REG_RBX);
		case REG_EBX:  shadow_reg_[REG_EBX]=addr; 
		case REG_BX:   shadow_reg_[REG_BX]=addr; 
		case REG_BH:   shadow_reg_[REG_BH]=addr; 
		case REG_BL:   shadow_reg_[REG_BL]=addr; 
			       break;

			       //case REG_RCX:  regsTainted.push_front(REG_RCX); 
		case REG_ECX:  shadow_reg_[REG_ECX]=addr; 
		case REG_CX:   shadow_reg_[REG_CX]=addr; 
		case REG_CH:   shadow_reg_[REG_CH]=addr; 
		case REG_CL:   shadow_reg_[REG_CL]=addr; 
			       break;

			       //case REG_RDX:  regsTainted.push_front(REG_RDX); 
		case REG_EDX:  shadow_reg_[REG_EDX]=addr;  
		case REG_DX:   shadow_reg_[REG_DX]=addr; 
		case REG_DH:   shadow_reg_[REG_DH]=addr;  
		case REG_DL:   shadow_reg_[REG_DL]=addr;  
			       break;

			       //case REG_RDI:  regsTainted.push_front(REG_RDI); 
		case REG_EDI:  shadow_reg_[REG_EDI]=addr;  
		case REG_DI:   shadow_reg_[REG_DI]=addr; 
			       //case REG_DIL:  regsTainted.push_front(REG_DIL); 
			       break;

			       //case REG_RSI:  regsTainted.push_front(REG_RSI); 
		case REG_ESI:  shadow_reg_[REG_ESI]=addr; 
		case REG_SI:   shadow_reg_[REG_SI]=addr;  
			       //case REG_SIL:  regsTainted.push_front(REG_SIL); 
			       break;
		case REG_EFLAGS: shadow_reg_[REG_EFLAGS]=addr; 
				 break;

		case REG_XMM0: shadow_reg_[REG_XMM0]=addr; 
			       break;
		case REG_XMM1: shadow_reg_[REG_XMM1]=addr; 
			       break;
		case REG_XMM2: shadow_reg_[REG_XMM2]=addr; 
			       break;
		case REG_XMM3: shadow_reg_[REG_XMM3]=addr; 
			       break;
		case REG_XMM4: shadow_reg_[REG_XMM4]=addr; 
			       break;
		case REG_XMM5: shadow_reg_[REG_XMM5]=addr; 
			       break;
		case REG_XMM6: shadow_reg_[REG_XMM6]=addr; 
			       break;
		case REG_XMM7: shadow_reg_[REG_XMM7]=addr; 
			       break;

		default:
			       D(cout << "\t\t\t--" << REG_StringShort(reg) << " can't be tainted" << endl;)
			       return false;
	}
	D(cout << "\t\t\t--" << REG_StringShort(reg) << " is now tainted" << endl;)
	return true;
}

bool ShadowReg::removeREG(REG reg)
{
	switch(reg){

		//case REG_RAX:  regsTainted.remove(REG_RAX);
		case REG_EAX:  shadow_reg_[REG_EAX]=0x0;
		case REG_AX:   shadow_reg_[REG_AX]=0x0;
		case REG_AH:   shadow_reg_[REG_AH]=0x0;
		case REG_AL:   shadow_reg_[REG_AL]=0x0;
			       break;

			       //case REG_RBX:  regsTainted.remove(REG_RBX);
		case REG_EBX:  shadow_reg_[REG_EBX]=0x0;
		case REG_BX:   shadow_reg_[REG_BX]=0x0;
		case REG_BH:   shadow_reg_[REG_BH]=0x0;
		case REG_BL:   shadow_reg_[REG_BL]=0x0;
			       break;

			       //case REG_RCX:  regsTainted.remove(REG_RCX); 
		case REG_ECX:  shadow_reg_[REG_ECX]=0x0;
		case REG_CX:   shadow_reg_[REG_CX]=0x0;
		case REG_CH:   shadow_reg_[REG_CH]=0x0;
		case REG_CL:   shadow_reg_[REG_CL]=0x0;
			       break;

			       //case REG_RDX:  regsTainted.remove(REG_RDX); 
		case REG_EDX:  shadow_reg_[REG_EDX]=0x0;
		case REG_DX:   shadow_reg_[REG_DX]=0x0;
		case REG_DH:   shadow_reg_[REG_DH]=0x0;
		case REG_DL:   shadow_reg_[REG_DL]=0x0;
			       break;

			       //case REG_RDI:  regsTainted.remove(REG_RDI); 
		case REG_EDI:  shadow_reg_[REG_EDI]=0x0;
		case REG_DI:   shadow_reg_[REG_DI]=0x0;
			       //case REG_DIL:  regsTainted.remove(REG_DIL); 
			       break;

			       //case REG_RSI:  regsTainted.remove(REG_RSI); 
		case REG_ESI:  shadow_reg_[REG_ESI]=0x0;
		case REG_SI:   shadow_reg_[REG_SI]=0x0;
			       //case REG_SIL:  regsTainted.remove(REG_SIL); 
			       break;

		case REG_EFLAGS: shadow_reg_[REG_EFLAGS]=0x0;
				 break;

		case REG_XMM0: shadow_reg_[REG_XMM0]=0x0;
			       break;
		case REG_XMM1: shadow_reg_[REG_XMM1]=0x0;
			       break;
		case REG_XMM2: shadow_reg_[REG_XMM2]=0x0;
			       break;
		case REG_XMM3: shadow_reg_[REG_XMM3]=0x0;
			       break;
		case REG_XMM4: shadow_reg_[REG_XMM4]=0x0;
			       break;
		case REG_XMM5: shadow_reg_[REG_XMM5]=0x0;
			       break;
		case REG_XMM6: shadow_reg_[REG_XMM6]=0x0;
			       break;
		case REG_XMM7: shadow_reg_[REG_XMM7]=0x0;
			       break;

		default:
			       return false;
	}
	D(cout << "\t\t\t--" << REG_StringShort(reg) << " is now freed" << endl;)
	return true;
}
