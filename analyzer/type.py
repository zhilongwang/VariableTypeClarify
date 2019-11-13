from enum import Enum
class AddrType (Enum):
      STK=1 # stack
      GBL=2 # global
      HEP=3 # heap
      REG=4 # register

class InsType (Enum):
      LOAD=1 # stack
      SPRD=2 # global
      STOR=3 # heap


