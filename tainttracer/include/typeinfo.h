#ifndef _TYPEINFO_H_
#define _TYPEINFO_H_
#include "pin.H"
#include "region.h" 
#include "trace.h"
#include<list>
#include<hash_map>

typedef enum VAR_TYPE
{
	CHR,
    INT,
	SINT,
	LONG,
    FLOAT,
    DOUBLE,
	POINTER
}VAT_TYPE;
string GetTypeName(VAR_TYPE type);


typedef struct VariableInfo
{
    RegionType regin;
    string type;
    string name;
    unsigned int addr;
	signed int offset;
    unsigned int size;
    VariableInfo(RegionType regin, VAR_TYPE type, string name, unsigned int addr, signed int offset, unsigned int size){
		this.regin = regin;
		this.type = type;
        this.name = name;
        this.addr = addr;
        this.offset = offset;
        this.size = size;
	}
}VariableInfo;
typedef struct FunctionInfo
{
    string name;
    std::list<InsInfo> func_vars_list;
    FunctionInfo(string name, std::list<InsInfo> func_vars_list){
		this.name = name;
        this.func_vars_list= func_vars_list;
	}
}FunctionInfo;

class ImageInfo{
private:
    std::list<FunctionInfo> functions_info_list;
    std::list<InsInfo> present_func_vars_list;
    std::list<InsInfo> global_vars_list; 
public:
    ImageInfo(string filename){
            ifstream file(filename);
            char buffer[256];
            char packet_type[10];
            char funname[256];
            char varname[256];
            unsigned int addr;
            char var_type[20];
            unsigned int size;
            RegionType regin = NO_REGION;
            while(getline(file, buffer)){
                sscanf(buffer,"%s",packet_type);
                if(strcmp(packet_type, "VAR")==0){
                    getline(file, buffer);
                    if(regin == GLOBAL){
                        sscanf(buffer,"\t%s %x %s %x",varname, addr, var_type, size);
                        global_vars_list.push_back(VariableInfo(regin, new string(var_type), varname, addr, 0, size));
                    }else if(regin == STACK){
                        sscanf(buffer,"\t%s %x %s %x",varname, addr, var_type, size);
                        present_func_vars_list.push_back(VariableInfo(regin, new string(var_type), varname, addr, 0, size));
                    }
                }else if(strcmp(packet_type, "FUN")==0){
                    if(regin == STACK){
                        functions_info_list.push_back(FunctionInfo(new string(funname),present_func_vars_list));
                        functions_info_list.clear();
                    }
                    regin = STACK;
                    getline(file, funname)
                }else if(strcmp(packet_type, "GOB")==0){
                    regin = GLOBAL;
                }
            }   
    }
    string get_global_type(unsigned int addr);
    string get_stack_type(signed int offset);
};
#endif