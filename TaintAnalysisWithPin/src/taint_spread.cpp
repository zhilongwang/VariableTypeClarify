#include "taint_spread.h"
#include <asm/unistd.h>
#include "pin.H"
#include "debug.h"
#include "instruction.h"
using std::endl;
#ifdef __DEGUG_TRACE
#define D(x) x
#else 
#define D(x)
#endif


extern RegionInfo* region_info;
extern ShadowMem* shadow_mem;
extern ShadowReg* shadow_reg;
VOID print_context(const CONTEXT * ctxt, VOID * addr){
	ADDRINT esp, ebp;
    PIN_GetContextRegval(ctxt, REG_ESP, reinterpret_cast<UINT8*>(&esp));
	PIN_GetContextRegval(ctxt, REG_EBP, reinterpret_cast<UINT8*>(&ebp));
	signed int offset2esp = (signed int)addr - (signed int)esp;
	signed int offset2ebp = (signed int)addr - (signed int)ebp;
	D(cout << "[CTXT]:("<< offset2esp <<")(" << offset2ebp << ")" << endl;)
}
VOID MemTo1Reg(VOID * ip, string funname, string assemble, const CONTEXT * ctxt, VOID * addr, UINT32 size, REG w_reg_1){
	RegionType region_type =  region_info->AddrRegion(addr);

	if(region_type == STACK){
		D(cout << hex << "[LOAD]:(<S><"<< (UINT32)addr << ">){" << (unsigned int)(w_reg_1) << "}|" << funname << "|"<< endl;)
		print_context(ctxt, addr);
	}else{
		D(cout << hex << "[LOAD]:(<N><"<< (UINT32)addr << ">){" << (unsigned int)(w_reg_1) << "}|" << funname << "|"<< endl;)
	}
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}
VOID MemTo2Reg(VOID * ip, string funname, string assemble, const CONTEXT * ctxt, VOID * addr, UINT32 size, REG w_reg_1, REG w_reg_2){
	RegionType region_type =  region_info->AddrRegion(addr);
	if(region_type == STACK){
		D(cout << hex << "[LOAD]:(<S><"<< (UINT32)addr << ">){" << (unsigned int)(w_reg_1) << "}{" << (unsigned int)(w_reg_2) << "}|" << funname << "|" << endl;)
		print_context(ctxt, addr);
	}else{
		D(cout << hex << "[LOAD]:(<N><"<< (UINT32)addr << ">){" << (unsigned int)(w_reg_1) << "}{" << (unsigned int)(w_reg_2) << "}|" << funname << "|" << endl;)
	}
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}
VOID MemTo3Reg(VOID * ip, string funname, string assemble, const CONTEXT * ctxt, VOID * addr, UINT32 size, REG w_reg_1, REG w_reg_2, REG w_reg_3){
	RegionType region_type =  region_info->AddrRegion(addr);
	if(region_type == STACK){
		D(cout << hex << "[LOAD]:(<S><"<< (UINT32)addr << ">){" << (unsigned int)(w_reg_1) << "}{" << (unsigned int)(w_reg_2) << "}{" << (unsigned int)(w_reg_3) << "}|" << funname << "|" << endl;)
		print_context(ctxt, addr);
	}{
		D(cout << hex << "[LOAD]:(<N><"<< (UINT32)addr << ">){" << (unsigned int)(w_reg_1) << "}{" << (unsigned int)(w_reg_2) << "}{" << (unsigned int)(w_reg_3) << "}|" << funname << "|" << endl;)
	}
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}
VOID ZeroReg2Mem(VOID * ip, string funname, string assemble, const CONTEXT * ctxt, VOID * addr, UINT32 size){

	RegionType region_type =  region_info->AddrRegion(addr);
	if(region_type == STACK){
		D(cout << hex << "[STOR]:("<< 0 << "){<S><" << (UINT32)addr << ">}|" << funname << "|" << endl;)
		print_context(ctxt, addr);
	}else{ 
		D(cout << hex << "[STOR]:("<< 0 << "){<N><" << (UINT32)addr << ">}|" << funname << "|" << endl;)
	}
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}

VOID OneReg2Mem(VOID * ip, string funname, string assemble, const CONTEXT * ctxt, VOID * addr, UINT32 size, REG r_reg_1){
	RegionType region_type =  region_info->AddrRegion(addr);
	if(region_type == STACK){
		D(cout << hex << "[STOR]:("<< (unsigned int)(r_reg_1) << "){<S><" << (UINT32)addr << ">}|" << funname << "|" << endl;)
		print_context(ctxt, addr);
	}else{
		D(cout << hex << "[STOR]:("<< (unsigned int)(r_reg_1) << "){<N><" << (UINT32)addr << ">}|" << funname << "|" << endl;)
	}
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}

VOID TwoReg2Mem(VOID * ip,string funname,  string assemble, const CONTEXT * ctxt, VOID * addr, UINT32 size, REG r_reg_1, REG r_reg_2){
	RegionType region_type =  region_info->AddrRegion(addr);
	if(region_type == STACK){
		D(cout << hex << "[STOR]:("<< (unsigned int)(r_reg_1) << ")(" << (unsigned int)(r_reg_2) <<"){<S><" << (UINT32)addr << ">}|" << funname << "|" << endl;)
		print_context(ctxt, addr);
	}else{
		D(cout << hex << "[STOR]:("<< (unsigned int)(r_reg_1) << ")(" << (unsigned int)(r_reg_2) <<"){<N><" << (UINT32)addr << ">}|" << funname << "|" << endl;)
	}
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}

VOID ThreeReg2Mem(VOID * ip, string funname, string assemble, const CONTEXT * ctxt, VOID * addr, UINT32 size, REG r_reg_1, REG r_reg_2, REG r_reg_3){
	RegionType region_type =  region_info->AddrRegion(addr);
	if(region_type == STACK){
		D(cout << hex << "[STOR]:("<< (unsigned int)(r_reg_1) << ")(" << (unsigned int)(r_reg_2) << ")(" << (unsigned int)(r_reg_3) << "){<S><" << (UINT32)addr << ">}|" << funname << "|" << endl;)
		print_context(ctxt, addr);
	}else{
		D(cout << hex << "[STOR]:("<< (unsigned int)(r_reg_1) << ")(" << (unsigned int)(r_reg_2) << ")(" << (unsigned int)(r_reg_3) << "){<N><" << (UINT32)addr << ">}|" << funname << "|" << endl;)
	}
	
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}

VOID OneRegs(VOID * ip,  string funname, string assemble, UINT32 read_reg_num, REG reg_1){
	D(cout << hex<< "[IMMI]:{"<< (unsigned int)(reg_1) <<"}|"<< funname <<"|" << endl;)
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}

VOID TwoRegs(VOID * ip,  string funname, string assemble, UINT32 read_reg_num, REG reg_1, REG reg_2){
	D(cout << hex<< "[SPED]:");
	switch(read_reg_num){
		case 2:
			D(cout << hex<< "(" << reg_1 << ")(" << reg_2 << ")|" << funname << "|" << endl;)
			break;
		case 1:
			D(cout << hex<< "(" << reg_1 << "){" << reg_2 << "}|" << funname << "|" << endl;)
			break;
		case 0:
			D(cout << hex<< "{" << reg_1 << "}{" << reg_2 << "}|" << funname << "|" << endl;)
			break;
		default:
			cout << "error" << endl;
	}
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}

VOID ThreeRegs(VOID * ip,  string funname, string assemble, UINT32 read_reg_num, REG reg_1, REG reg_2, REG reg_3){
	D(cout << hex<< "[SPED]:");
	switch(read_reg_num){
		case 3:
			D(cout << hex<< "(" << reg_1 << ")(" << reg_2 << ")(" << reg_3 << ")|" << funname << "|" << endl;)
			break;
		case 2:
			D(cout << hex<< "(" << reg_1 << ")(" << reg_2 << "){" << reg_3 << "}|" << funname << "|" << endl;)
			break;
		case 1:
			D(cout << hex<< "(" << reg_1 << "){" << reg_2 << "}{" << reg_3 << "}|" << funname << "|" << endl;)
			break;
		case 0:
			D(cout << hex<< "{" << reg_1 << "}{" << reg_2 << "}{" << reg_3 << "}|" << funname << "|" << endl;)
			break;
		default:
			cout << "error" << endl;
	}
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}

VOID FourRegs(VOID * ip,  string funname, string assemble, UINT32 read_reg_num, REG reg_1, REG reg_2, REG reg_3, REG reg_4){
	D(cout << hex<< "[SPED]:");
	switch(read_reg_num){
		case 4:
			D(cout << hex<< "(" << reg_1 << ")(" << reg_2 << ")(" << reg_3 << ")(" << reg_4 << ")|" << funname << "|" << endl;)
			break;
		case 3:
			D(cout << hex<< "(" << reg_1 << ")(" << reg_2 << ")(" << reg_3 << "){" << reg_4 << "}|" << funname << "|" << endl;)
			break;
		case 2:
			D(cout << hex<< "(" << reg_1 << ")(" << reg_2 << "){" << reg_3 << "}{" << reg_4 << "}|" << funname << "|" << endl;)
			break;
		case 1:
			D(cout << hex<< "(" << reg_1 << "){" << reg_2 << "}{" << reg_3 << "}{" << reg_4 << "}|" << funname << "|" << endl;)
			break;
		case 0:
			D(cout << hex<< "{" << reg_1 << "}{" << reg_2 << "}{" << reg_3 << "}{" << reg_4 << "}|" << funname << "|" << endl;)
			break;
		default:
			cout << "error" << endl;
	}
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}
VOID Mem2Mem(VOID * ip, string funname, string assemble, const CONTEXT * ctxt, VOID * read_addr, UINT32 read_size, VOID * write_addr, UINT32 write_size){
	D(cout << hex << "[LOAD]:";)
	RegionType region_type =  region_info->AddrRegion(read_addr);
	if(region_type == STACK){
		D(cout << hex << "(<S><"<< read_addr << ">)";)
	}else{
		D(cout << hex << "(<G><"<< read_addr << ">)";)
	}
	region_type =  region_info->AddrRegion(write_addr);
	if(region_type == STACK){
		D(cout << hex << "{<S><"<< write_addr << ">}|" << funname << "|" << endl;)
		print_context(ctxt, write_addr);
	}else{
		D(cout << hex << "{<N><"<< write_addr << ">}|" << funname << "|" << endl;)
		print_context(ctxt, write_addr);
	}
	D(cout << hex << ip << "\t"<< assemble  << endl;)
	return;
}

