# VariableTypeClarify

To Clarify variable type in bianry through machine learning.

- How to mapping the binary code to source code.
 
   ```
   gcc -g3 -o <binary> <source code>
   objdump --dwarf=decodedline <binary>
   ```.  
- Get local variable information.
   
   ```   
   gcc -g3 -o <binary> <source code>
   objdump --dwarf=decodedline <binary>
   ```
   
 
