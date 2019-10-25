# Relevant attributes
LOC  = 'DW_AT_location'
TYPE = 'DW_AT_type'
NAME = 'DW_AT_name'
LINE = 'DW_AT_decl_line'
BASE = 'DW_AT_frame_base'
LOPC = 'DW_AT_low_pc'
HIPC = 'DW_AT_high_pc'
FILE = 'DW_AT_decl_file'
CVAL = 'DW_AT_const_value'

# Forms
EXPR = 'DW_FORM_exprloc'
SECO = 'DW_FORM_sec_offset'

# Relevant conversions
OP_CFA = 0x91
OP_REG = 0x50
OP_BREG = 0x71
regs = [    # Register names in order
    'rax', 'rcx', 'rdx', 'rbx',
    'rsp', 'rbp', 'rsi', 'rdi',
    'r8' , 'r9' , 'r10', 'r11',
    'r12', 'r14', 'r14', 'r15'
]

def get_leb128(leb, signed=True):
    """ Decode a LEB128 signed integer represented as a list of bytes.
    Adapted from pseudocode provided in https://en.wikipedia.org/wiki/LEB128
    """
    try:
        value = 0
        i = 0

        while leb[i] & 128 > 0:
            value |= (leb[i] & 127) << 7*i
            i += 1

        if signed:
            value |= ((leb[i] & 63) - (leb[i] & 64)) << 7*i
        else:
            value |= (leb[i] & 127) << 7*i

        return value
    except:
        # Give info about crash
        print('LEB128 decoding error: \n\t%s could not be decoded.' % leb)
        raise

def parse_location(die):
    """ Take the value of a location attribute (DW_AT_location) loc
    and return a string corresponding to its location in memory in
    x86-assembly (usually either a register or offset from one).
    """


    if LOC in die.attributes:
        loc = die.attributes[LOC]
    elif CVAL in die.attributes:
        return '$' + str(die.attributes[CVAL].value)
    else:
        return ''

    if loc.form != EXPR:
        print('Unrecognized location encoding:')
        print('\t%s\t%s' % (die.attributes[LOC].form, die.attributes[LOC].value))
        return '???'

    print("step1")
    try:
        if hasattr(loc, 'value'):
            loc = loc.value

        # shitty hack
        if type(loc) is int:
            loc = [loc]

        if loc[0] == OP_CFA:
            print("step2")
            if len(loc) > 1:
                # Indicates (signed) LEB128 offset from base pointer
           
                return get_leb128(loc[1:])
            else:
                # Not sure what this means, maybe just %rbp ?
                return '%rbp'

        if loc[0] >= OP_REG and loc[0] < OP_BREG:
            print("step3")
            # Indicates in-register location

            # TODO: figure out size of operand and change register name accordingly
            result = regs[loc[0] - OP_REG]
            return '%' + result

        if loc[0] >= OP_BREG:
            print("step4")
            if len(loc) > 1:
                # Get offset from register
                offset = get_leb128(loc[1:])
            else:
                offset = ''

            try:
                # Get register
                reg = regs[loc[0] - OP_BREG]
                return [offset, reg]
            except:
                return '???'

    except:
        print('Unable to resolve location: %s' % loc)
        try: print('\t(decoded: %s)' % get_leb128(loc))
        except: pass
        raise