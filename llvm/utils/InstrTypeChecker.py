class Type_Check:
    """
    type checker
    "line":     read one line
    "instr":    one instruction(instr) parsed from line
    """
    def is_func( line ):
        """
        Check This is Function
        """
        if line.find("define") >= 0:
            return True
        if line.find("entry") >= 0:
            return True
        return False

    def is_bblock( line ):
        """
        Check This is Basic-Block
        """
        if line.find(":") >= 0:
            return True
        return False

    def is_instr( instr ):
        """
        Check This is Instruction
        """
        return len(instr) > 1 and "}" not in instr

    def is_br( instr ):
        """
        Check This is Branch Instr
        """
        return "br" in instr and not "label" in instr[1]

    def is_jmp( instr ):
        """
        Check This is Jump Instr
        """
        return "br" in instr and "label" in instr[1]

    def is_switch( instr ):
        """
        Check This is Switch Instr
        """
        return "switch" in instr

    def is_cmp( instr ):
        """
        Check This is Compare Instr
        """
        return "icmp" not in instr and "fcmp" not in instr and "cmp" in instr

    def is_icmp( instr ):
        """
        Check This is Int-Compare Instr
        """
        return "icmp" in instr

    def is_fcmp( instr ):
        """
        Check This is Float-Compare Instr
        """
        return "fcmp" in instr

    def is_load( instr ):
        """
        Check This is Load Instr
        """
        return "load" in instr

    def is_store( instr ):
        """
        Check This is Store Instr
        """
        return "store" in instr

    def is_call( instr ):
        """
        Check This is Call Instr
        """
        return "call" in instr

    def is_ret( instr ):
        """
        Check This is Return Instr
        """
        return "ret" in instr

    def is_trunc( instr ):
        """
        Check This is Int Trunc Instr
        """
        return "trunc" in instr

    def is_fptrunc( instr ):
        """
        Check This is Float Trunc Instr
        """
        return "fptrunc" in instr

    def is_sext( instr ):
        """
        Check This is Sign-Extension Instr
        """
        return "sext" in instr

    def is_fpext( instr ):
        """
        Check This is Float to Double Instr
        """
        return "fpext" in instr

    def is_sitofp( instr ):
        """
        Check This is Signed Int to Float Instr
        """
        return "sitofp" in instr

    def is_ptr( instr ):
        """
        Check Arg have Pointer
        """
        for a in instr:
            if "*" in a:
                return True
        return False

    def is_alloca( instr ):
        """
        Check This is Allocator
        """
        return "alloca" in instr

    def is_getelementptr( instr ):
        """
        Check This is Array Pointer
        """
        return "getelementptr" in instr

    def is_unreachable( instr ):
        """
        Check This is Unreachable Instr
        """
        return "unreachable" in instr
