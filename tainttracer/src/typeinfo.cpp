#include "typeinfo.h"
#include "debug.h"
#include<string>
#include<iostream>
using std::string;
using std::iostream;
using std::endl;



string GetTypeName(VAR_TYPE type){
  	string type_name; 
	type_name="UNKnowType:"+reg; 
	switch(reg){
		case CHR:  type_name="char"; 
			break;
		case INT:  type_name="int"; 
			break;
		case SINT:  type_name="short int"; 
			break;
		case LONG:  type_name="long"; 
			break;
		case FLOAT:  type_name="float"; 
			break;
		case DOUBLE:  type_name="double"; 
			break;
		case POINTER:  type_name="pointer"; 
			break;
		default:
		type_name="UNKnowType";  
  }
  return type_name;
}

string ImageInfo::get_global_type(unsigned int addr){
    std::list<FunctionInfo>::iterator functions_iter;
    for (functions_iter = functions_info_list.begin(); functions_iter != functions_info_list.end(); ++functions_iter){
        std::list<InsInfo>::iterator instruction_iter;
        for (instruction_iter = functions_iter->begin(); instruction_iter != functions_iter->end(); ++instruction_iter){
            VariableInfo * var_info = instruction_iter;
            if (addr>=var_info->addr & addr<var_info->addr + var_info->size){
                return var_info->type;
            }
        } 
    } 
}
string ImageInfo::get_stack_type(signed int offset){
    std::list<InsInfo>::iterator instruction_iter;
    for (instruction_iter = global_vars_list->begin(); instruction_iter != global_vars_list->end(); ++instruction_iter){
        VariableInfo * var_info = instruction_iter;
        if (addr>=var_info->offset & addr<var_info->offset + var_info->size){
            return var_info->type;
        }
    } 
}