import .utils.InstrTypeCheck.Type_Check
import utils.ProgramReader

DEBUG = True

def instr_parser(instr):
    """
    Instruction Parser
    """
    type_chk = Type_Check()

    operands = []
    if type_chk.is_br(instr):
        # Conditional Branch Instruction
        """
        br i1 %6, label %7, label %32
        """
        instr_type = instr[0]
        dst = None
        d_type = None
        src_a = instr[2].replace(",", "")
        src_b = None
        operands.append(src_a)
        func = instr[1]
        br_t = "label:<" + instr[4].replace(",", "").replace("%", "")+">"
        br_f = "label:<" + instr[6].replace(",", "").replace("%", "")+">"
        imm = False
        sw = False

    elif type_chk.is_jmp(instr):
        # Jump Instruction
        """
        br label %31
        """
        instr_type = "jmp"
        dst = None
        d_type = None
        src_a = None
        src_b = None
        func = None
        br_t = "label:<" + instr[2].replace("%", "")+">"
        br_f = "label:<" + instr[2].replace("%", "")+">"
        imm = False
        sw = False

    elif type_chk.is_switch(instr):
        # Switch Instruction
        """
        switch i32 %7, label %38 [
            i32 48, label %8
            i32 43, label %11
            i32 42, label %15
            i32 45, label %19
            i32 47, label %24
            i32 10, label %35
        ]
        """
        instr_type = instr[0]
        dst = instr[2].replace(",", "")
        d_type = instr[1]
        src_a = None
        src_b = None
        func = None
        br_t = None
        br_f = instr[4]
        imm = False
        sw = True

    elif type_chk.is_cmp(instr):
        # Integer Compare Instruction
        """
        %10 = cmp eq i32 %9, i32 %10
        """
        instr_type = instr[2]
        dst = instr[0].replace(",", "")
        d_type = None
        src_a = instr[4] + " " + instr[5].replace(",", "")
        src_b = instr[6] + " " + instr[7].replace(",", "")
        operands.append(src_a)
        operands.append(src_b)
        func = instr[3]
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_icmp(instr):
        # Integer Immediate Compare Instruction
        """
        %10 = icmp eq i32 %9, 9
        """
        instr_type = instr[2]
        dst = instr[0].replace(",", "")
        d_type = None
        src_a = instr[5].replace(",", "")
        src_b = instr[6].replace(",", "")
        operands.append(src_a)
        operands.append(src_b)
        func = instr[3]
        br_t = None
        br_f = None
        imm = True
        sw = False

    elif type_chk.is_fcmp(instr):
        # Float Compare Instruction
        """
        %27 = fcmp une double %26, 0.000000e+00
        """
        instr_type = instr[2]
        dst = instr[0].replace(",", "")
        d_type = instr[4]
        src_a = instr[5].replace(",", "")
        src_b = instr[6].replace(",", "")
        operands.append(src_a)
        operands.append(src_b)
        func = instr[3]
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_load(instr):
        # Load Instruction
        """
        %38 = load i32, i32* %2, align 4
        %8 = load i8* %c, align 1
        """
        instr_type = instr[2]
        dst = instr[0].replace(",", "")
        d_type = instr[3].replace(",", "")
        if len(instr) > 6:
            src_a = instr[5].replace(",", "")
        else:
            src_a = instr[4].replace(",", "")
        src_b = None
        operands.append(src_a)
        func = instr[5:6]
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_store(instr):
        # Store Instruction
        """
        store i32 0, i32* %1
        """
        instr_type = instr[0]
        dst = None
        d_type = instr[3]
        src_a = instr[2].replace(",", "")
        src_b = instr[4].replace(",", "")
        operands.append(src_a)
        operands.append(src_b)
        func = None
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_call(instr):
        # Call Instruction
        if "call" == instr[0]:
            # Return is void
            """
            call void @push(double %10)
            """
            instr_type = instr[0]
            dst = instr[0].replace(",", "")
            d_type = instr[2].split("(")[1]
            src_a = instr[3].replace(")", "")
            src_b = None
            operands.append(src_a)
            func = instr[2].split("(")[0]
            br_t = None
            br_f = None
            imm = False
            sw = False
        else:
            # Return have some Value
            """
            %3  = call i32 @getchar()
            %21 = call double @pop()
            %49 = call i32 @putchar(i32 %48)
            %33 = call i32 (i8*, ...)*..., double %18, double %20)
            %2  = call i32 @squeeze(i8* getelementptr inbounds ([7 x i8]* @test, i32 0, i32 0)
            %75 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([5 x i8]* @.str, i32 0, i32 0), i32 %74)
            """
            instr_type = instr[2]
            dst = instr[0].replace(",", "")
            d_type = instr[3]
            if 18 < len(instr) and "%" in instr[4:]:
                src_a = instr[18].replace(",", "")
                src_b = instr[20].replace(")", "")
                operands.append(src_a)
                operands.append(src_b)

            elif 18 <= len(instr):
                src_a = instr[18].replace(",", "").replace(")", "")
                src_b = None
                operands.append(src_a)

            elif "@squeeze" in instr[4]:
                src_a = instr[12].replace(",", "").replace(")", "")
                src_b = instr[14].replace(",", "").replace(")", "")
                operands.append(src_a)
                operands.append(src_b)

            elif 6 == len(instr):
                src_a = instr[5].replace(",", "").replace(")", "")
                src_b = None
                operands.append(src_a)

            else:
                src_a = None
                src_b = None

            func = instr[4].replace("(", "").replace(",", "")
            br_t = instr[4].replace("(", "").replace(",", "")
            if "@" in instr[4]:
                func = instr[4]
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_ret(instr):
        # Return Instruction
        """
        ret i32 0
        ret void
        ret i32 %27
        """
        instr_type = instr[0]
        dst = None
        if (len(instr) == 3):
            d_type = instr[1]
            src_a = instr[2].replace(",", "")
            operands.append(src_a)
        else:
            d_type = instr[1]
            src_a = None
            src_b = None
        func = None
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_trunc(instr):
        # Truncation (Int)
        """
        %4 = trunc i32 %3 to i8
        """
        instr_type = instr[2]
        dst = instr[0].replace(",", "")
        d_type = instr[6]
        src_a = instr[4].replace(",", "")
        src_b = None
        operands.append(src_a)
        func = None
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_fptrunc(instr):
        # Truncation (FP)
        """
        %16 = fptrunc double %15 to float
        """
        instr_type = instr[2]
        dst = instr[0].replace(",", "")
        d_type = instr[6]
        src_a = instr[4].replace(",", "")
        src_b = None
        operands.append(src_a)
        func = None
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_sext(instr):
        # Sign Extension (Int)
        """
        %27 = sext i8 %26 to i32
        """
        instr_type = instr[2]
        dst = instr[0].replace(",", "")
        d_type = None
        src_a = instr[4].replace(",", "")
        src_b = None
        operands.append(src_a)
        func = instr[3].replace(",", "") + " to " + instr[6].replace(",", "")
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_fpext(instr):
        # Precision-Extend
        """
        %13 = fpext float %12 to double
        """
        instr_type = instr[2]
        dst = instr[0].replace(",", "")
        d_type = None
        src_a = instr[4].replace(",", "")
        src_b = None
        operands.append(src_a)
        func = instr[3].replace(",", "") + " to " + instr[6].replace(",", "")
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_sitofp(instr):
        # Signed Int to FP
        """
        %3 = sitofp i32 %2 to float
        """
        instr_type = instr[2]
        dst = instr[0].replace(",", "")
        d_type = None
        src_a = instr[4].replace(",", "")
        src_b = None
        operands.append(src_a)
        func = instr[3].replace(",", "") + " to " + instr[6].replace(",", "")
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_alloca(instr):
        # Memory Allocation
        """
        %1 = alloca i32, align 4
        """
        instr_type = instr[2]
        dst = instr[0].replace(",", "")
        d_type = None
        src_a = None
        src_b = None
        func = instr[3].replace(",", "") + " " + instr[4] + " " + instr[5]
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_getelementptr(instr):
        # Pointer
        """
        %18 = getelementptr inbounds [256 x [256 x i32]], [256 x [256 x i32]]* @A, i64 0, i64 %17
        %30 = getelementptr inbounds [256 x i32], [256 x i32]* @C, i64 0, i64 %29
        %21 = getelementptr inbounds [256 x i32], [256 x i32]* %18, i64 0, i64 %20
        %3 = getelementptr inbounds [100 x i8]* %s, i32 0, i32 0
        %82 = getelementptr inbounds [10 x i32]* %ndigit, i32 0, i64 %81
        %46 = getelementptr inbounds i8* %45, i64 %4
        %7 = getelementptr inbounds i8* %6, i64 0
        """
        instr_type = instr[2]
        dst = instr[0].replace(",", "")
        if len(instr) == 19:
            d_type = instr[8].replace("]", "").replace(",", "")
            src_a = instr[18].replace(",", "")
            src_b = None
            operands.append(src_a)
            func = instr[4] + " " + instr[5] + " " + instr[6]

        elif len(instr) == 15:
            d_type = instr[6].replace("]", "").replace(",", "")
            if "%" in instr[10]:
                src_a = instr[10].replace(",", "")
                src_b = instr[14]
                operands.append(src_a)
                operands.append(src_b)
            else:
                src_a = instr[14].replace(",", "")
                operands.append(src_a)
            func = instr[4] + " " + instr[5] + " " + instr[6]

        elif "[" in instr[4]:
            d_type = instr[6].replace("]", "").replace(",", "")
            src_a = instr[7].replace(",", "")
            operands.append(src_a)
            if "%" in instr[11]:
                src_b = instr[11]
                operands.append(src_b)
            else:
                src_b = None
            func = instr[4] + " " + instr[5] + " " + instr[6] + " " + instr[8] + " " + instr[9].replace(",", "") + " " + instr[10] + " " + instr[11]

        else:
            d_type = instr[4]
            src_a = instr[5].replace(",", "")
            src_b = instr[7].replace(",", "")
            operands.append(src_a)
            operands.append(src_b)
            func = instr[4] + " " + instr[5].replace(",", "") + " " + instr[6] + " " + instr[7]
        br_t = None
        br_f = None
        imm = False
        sw = False

    elif type_chk.is_instr(instr) and not type_chk.is_unreachable(instr):
        # Aux Instruction
        """
        %11 = add nsw i32 %10, 1
        %14 = fadd double %12, %13
        """
        if "i32" == instr[4]:
            instr_type = instr[2]
            dst = instr[0].replace(",", "")
            d_type = instr[4]
            src_a = instr[5].replace(",", "")
            src_b = instr[6]
            operands.append(src_a)
            operands.append(src_b)
            func = instr[3]
        else:
            instr_type = instr[2]
            dst = instr[0].replace(",", "")
            d_type = instr[3]
            src_a = instr[4].replace(",", "")
            src_b = instr[5]
            operands.append(src_a)
            operands.append(src_b)
            func = None
        br_t = None
        br_f = None
        imm = (len(instr) == 6)
        sw = False

    elif type_chk.is_unreachable(instr):
        instr_type = None
        dst = None
        d_type = None
        src_a = None
        src_b = None
        func = None
        br_t = None
        br_f = None
        imm = None
        sw = None
    else:
        return None

    return instr_type, \
        dst, \
        d_type, \
        operands, \
        func, \
        br_t, \
        br_f, \
        imm, \
        sw


def switch_parser(line, dst, d_type, no_br):
    """
    Switch IR is typically not supported by ISA.
    This method works to generate equivalent set of IRs.
    """
    line = line.split()
    """
    switch i32 %7, label %38 [
        i32 48, label %8
        i32 43, label %11
        i32 42, label %15
        i32 45, label %19
        i32 47, label %24
        i32 10, label %35
    ]

    to

    dst = %7

    %lab_{no_br}
    sw_{no_br} = icmp eq d_type dst, 48
    br sw_{no_br}, label %8 label %lab_{no_br+1}

    %lab_{no_br+1}
    sw_{no_br} = icmp eq d_type dst, 43
    br sw_{no_br+1}, label %8 label %lab_{no_br+2}

    %lab_{no_br+2}
    sw_{no_br} = icmp eq d_type dst, 42
    br sw_{no_br+2}, label %8 label %lab_{no_br+3}

    %lab_{no_br+3}
    sw_{no_br} = icmp eq d_type dst, 45
    br sw_{no_br+3}, label %8 label %lab_{no_br+4}

    %lab_{no_br+4}
    sw_{no_br} = icmp eq d_type dst, 47
    br sw_{no_br+4}, label %8 label %lab_{no_br+5}

    %lab_{no_br+5}
    sw_{no_br} = icmp eq d_type dst, 10
    br sw_{no_br+5}, label %8 label %38
    """

    lines = []
    line_icmp = "  sw_" + str(no_br) + " = icmp eq " + line[0] + " " + dst + ", " + line[1]
    line_br = "  br i1 sw_" + str(no_br) + ", label" + line[3] + " label lab_" + str(no_br + 1)

    lines.append(line_icmp)
    lines.append(line_br)
    return "lab_" + str(no_br), lines


class instruction:
    opcode = None       #Opcode Name                String
    dst = None          #Destination Name           String
    d_type = None       #Destination Data-Type      String
    operands = []       #Source Name                String
    func = None         #Function Name              String
    br_t = None         #Lavel for Branch Taken     Bool
    br_f = None         #Lavel for Branch Not Taken Bool
    imm = None          #Immediate Value            String
    nemonic = None      #Nemonic (Assembly Code)    String
    discovered = False  #Tracking Record            Bool


class basicblock():
    """
    Basic Block Extractor
    name = None         Basic Block Name            String
    instrs = []         Set of Instructions         instruction class
    num_instrs = 0      A Number of Instructions    Int
    """
    def __init__(self):
        self.name = None
        self.instrs = []
        self.num_instrs = 0

    def clear(self):
        self.name = None
        self.instrs.clear()
        self.num_instrs = 0

    def append(self, instr=instruction):
        self.instrs.append(copy.deepcopy(instr))
        self.num_instrs += 1

    def set_name(self, b_name):
        self.name = b_name


class function():
    """
    Function Extractor
    name = name         Function Name               String
    bblocks = []        Set of Basic Blocks         basicblock class
    num_bblocks = 0     A Number of Basic Blocks    Int
    """
    def __init__(self):
        self.name = None
        self.bblocks = []
        self.num_bblocks = 0

    def clear(self):
        self.name = None
        self.bblocks.clear()
        self.num_bblocks = 0

    def append(self, bblock):
        self.bblocks.append(copy.deepcopy(bblock))
        self.num_bblocks += 1

    def set_name(self, f_name):
        self.name = f_name


class program():
    """
    Program Extractor
    name = name         Program Name                String
    funcs = []          Set of Functioins           function class
    num_funcs = 0       A Number of Functions       Int
    """
    def __init__(self):
        self.name = None
        self.funcs = []
        self.num_funcs = 0

    def clear(self):
        self.name = None
        self.funcs.clear()
        self.num_funcs = 0

    def append(self, func):
        self.funcs.append(copy.deepcopy(func))
        self.num_funcs += 1

    def set_name(self, p_name):
        self.name = p_name


def asm_parser(asm):
    """
    LLVM-IR Parser
    """

    # Current status flags
    #   True then being entered
    in_func = False
    in_bblock = False
    in_switch = False

    # Switch-IR Label-Handling Variable
    no_br = 0

    # Line Number
    no_line = 0

    # Oblects maintains hierarchical structure
    prog = program()


    for line_no, line in enumerate(asm):
        # These set-up lines should be ommitted
        if (line.find("ModuleID") < 0 and \
            line.find("target") < 0 and \
            line[0] != "@" and \
            line.find("declare") < 0 and \
            line.find("attributes") < 0):

            # Create Instruction Object
            instr = instruction()

            # Parse Switch IR
            if in_switch:

                # Parse Multiple Lines
                # Check Ending of Swtich
                sw_end = "]" in line
                if not sw_end:
                    # Inside Switch Line Pseudo Parse
                    lab, lines = switch_parser(line, dst, d_type, no_br)

                    # Branching label-number
                    # Switch does not assign label-number for every statement,
                    # so assignment is necessary
                    no_br += 1

                    # Swtich Lines
                    for cnt in range(2):
                        sw_line = lines[cnt]

                        # Register Instruction
                        if type_chk.is_instr(sw_line):
                            if DEBUG:
                                print(sw_line)
                            ins = sw_line.split()
                            instr.opcode, \
                            instr.dst, \
                            instr.d_type, \
                            instr.operands, \
                            instr.func, \
                            instr.br_t, \
                            instr.br_f, \
                            instr.imm, \
                            instr.sw = instr_parser(ins)
                            instr.nemonic = sw_line
                            bblock.append(instr)
                            bblock.num_instrs += 1
                else:
                    # Last instruction should have switch-IR's
                    #   branch target address, setting this
                    instr.br_f = br_f
                    bblock.append(instr)
                    in_switch = False


            elif type_chk.is_func(line):
                # Create Function Object
                func = function()

                # Register Function
                in_func = True
                line = line.split()

                # Set Function NaME
                if "define" in line:
                    func.set_name(line[2])
                else:
                    func.set_name("entry")
                func.num_bblocks = 0
                no_br = 0
                if DEBUG:
                    print(f"Enter Func: {func.name}")


            elif type_chk.is_bblock(line) and in_func and not in_bblock:
                # Create Basic-Block Object
                bblock = basicblock()

                # Register Basic-Block
                in_bblock = True
                line = line.split()
                bblock.set_name(line[0].replace(":", ""))
                bblock.num_instrs = 0
                no_br = 0
                if DEBUG:
                    print(f"Enter BBlock: {bblock.name}")


            elif in_func and not in_bblock:
                # Create "First" Basic-Block Object
                bblock = basicblock()

                # Register Basic-Block (Entry-Block)
                bblock.set_name("entry")
                in_bblock = True
                bblock.num_instrs = 0
                no_br = 0
                if DEBUG:
                    print("Enter BBlock: entry")
                line = line.replace("\n", "")

                # Parse First Instr
                ins = line.split()
                if not "preds" in ins:
                    instr.opcode, \
                    instr.dst, \
                    instr.d_type, \
                    instr.operands, \
                    instr.func, \
                    instr.br_t, \
                    instr.br_f, \
                    instr.imm, \
                    instr.sw = instr_parser(ins)
                    instr.nemonic = line

                    # Register Switch Info
                    dst = instr.dst
                    br_f = instr.br_f
                    d_type = instr.d_type

                    # Register Instr
                    in_switch = instr.sw
                    if not in_switch:
                        bblock.append(instr)

                no_br = 0


            elif type_chk.is_instr(line) and "\n" != line and in_bblock and not in_switch:
                # Register Instruction
                line = line.replace("\n", "")

                # Parse Instr
                ins = line.split()
                instr.opcode, \
                instr.dst, \
                instr.d_type, \
                instr.operands, \
                instr.func, \
                instr.br_t, \
                instr.br_f, \
                instr.imm, \
                instr.sw = instr_parser(ins)
                instr.nemonic = line

                # Register Switch Info
                dst = instr.dst
                br_f = instr.br_f
                d_type = instr.d_type

                # Register Instr
                in_switch = instr.sw
                if not in_switch:
                    bblock.append(instr)

                no_br = 0


            elif "\n" == line and in_bblock:
                # Exit Basic-Block
                # Common Exiting
                if DEBUG:
                    print("Exit BBlock")
                func.append(bblock)
                bblock.clear()
                del bblock

                if DEBUG:
                    for f_index, bblock_ in enumerate(func.bblocks):
                        print(bblock_.name)
                        for b_index, instr in enumerate(bblock_.instrs):
                            print(f"{f_index}:{b_index}:{instr.nemonic}")

                # Clear Flag
                in_bblock = False
                no_br = 0
                if DEBUG:
                    print("\n")


            elif "}" in line and in_func:
                if in_bblock:
                    # Exit Basic-Block
                    # Exiting function on next line
                    # Preprocessing of exiting current bblock is needed
                    if DEBUG:
                        print("Exit BBlock")
                    func.append(bblock)
                    bblock.clear()
                    del bblock

                if DEBUG:
                    for f_index, bblock_ in enumerate(func.bblocks):
                        print(bblock_.name)
                        for b_index, instr in enumerate(bblock_.instrs):
                            print(f"{f_index}:{b_index}:{instr.nemonic}")

                # Clear Flag
                in_bblock = False
                no_br = 0
                if DEBUG:
                    print("\n")

                # Exit Function
                if DEBUG:
                    print("Exit Func")
                prog.append(func)
                func.clear()
                del func

                #clear Flag
                in_func = False
                no_br = 0
                if DEBUG:
                    print("\n")

    # Check Exiting Correctly
    if in_func:
        print(f"Error: Function {func.name} is broken.")

    if in_bblock:
        print(f"Error: Basic Block {bblock.name} is broken.")

    # Dubug Print
    if DEBUG:
        for p_index, func_ in enumerate(prog.funcs):
            print(func_.name)

            for f_index, bblock_ in enumerate(func_.bblocks):
                print(bblock_.name)

                for b_index, instr in enumerate(bblock_.instrs):
                    print("{}:{}:{}:{}".format(p_index, f_index, b_index, instr.nemonic))

    return prog


def is_Val(src):
    """
    Check literal is value (val) or not.
    Return
        True:   Literal is Value
        False:  Otherwise
    Common for Source-1 and Source-2.
    """
    return "%" != src[0]

def is_None(src):
    """
    Check literal is None or not.
    Return
        True:   source is type of None
        False:  Otherwise
    Common for Source-1 and Source-2.
    """
    return None == src

def FetchSrc(src="src2", instr=None):
    """
    Fetch Src-ID from instr class.
    Return
        Literal:    if operand exists
        None:       otherwise
    """
    if None == instr:
        print("Error: Un-registered Instruction is discovered.")
        return None
    elif "src2" == src and len(instr.operands) > 1:
        # Fetch Source-2
        return instr.operands[1]
    elif "src1" == src and len(instr.operands) > 0:
        # Fetch Source-1
        return instr.operands[0]
    else:
        return None


class RegInstr:
    """
    Registering Utilities
    """
    def __init__(self, prog, ptr):
        self.prog = prog            #program class
        self.ptr = ptr              #tracking pointer
        self.stack_ptr = []         #stack for pointers
        self.hit_ptr = None         #pointer for search-hit
        self.instr = None           #instruction class
        self.next_bb = False        #Moved to Next Basic Block then True

    def ReadProg(self):
        """
        Read Program
        """
        return self.prog

    def ReadHitPtr(self):
        """
        Read Hit (Source-Node) Pointer
        """
        return self.hit_ptr

    def ReadPtr(self):
        """
        Read Current Pointer
        """
        return self.ptr

    def SetPtr(self, ptr=None):
        """
        Set Pointers
        """
        self.ptr = copy.deepcopy(ptr)

    def PushPtr(self):
        """
        Push Pointers to Stack
        Used for Record a Path having Source-2 for backing to the instr
        Used when enters to source-2 path
        """
        ptr = self.ptr
        self.stack_ptr.append(copy.deepcopy(ptr))

    def PopPtr(self, SrcNo=None):
        """
        Pop Pointers from Stack
        Used for reverting Path and entering to Source-1 path
        """
        if len(self.stack_ptr) > 0:
            self.ptr = self.stack_ptr.pop()

    def DepthStack(self):
        """
        Return Stack-Depth
        """
        return len(self.stack_ptr)

    def CheckInstr(self, ptr=None):
        """
        Record instruction addressed by current pointer
        Marking discovered flag which indicates source-1 operand is commited.
        """
        if None == ptr:
            f_ptr, b_ptr, i_ptr = self.ptr["f_ptr"], self.ptr["b_ptr"], self.ptr["i_ptr"]
        else:
            f_ptr, b_ptr, i_ptr = ptr["f_ptr"], ptr["b_ptr"], ptr["i_ptr"]
        self.prog.funcs[f_ptr].bblocks[b_ptr].instrs[i_ptr].discovered = True

    def CheckHitInstr(self):
        """
        Record hit-instruction addressed by hit-pointer
        Marking discovered flag which indicates source-1 operand is commited.
        """
        f_ptr, b_ptr, i_ptr = self.hit_ptr["f_ptr"], self.hit_ptr["b_ptr"], self.hit_ptr["i_ptr"]
        self.prog.funcs[f_ptr].bblocks[b_ptr].instrs[i_ptr].discovered = True

    def ReadInstr(self, ptr=None):
        """
        Fetch Instruction addessed by current pointer
        """
        f_ptr, b_ptr, i_ptr = ptr["f_ptr"], ptr["b_ptr"], ptr["i_ptr"]
        instr = self.prog.funcs[f_ptr].bblocks[b_ptr].instrs[i_ptr]
        return self.prog.funcs[f_ptr].bblocks[b_ptr].instrs[i_ptr]

    def SetPrevInstr(self, instr=None):
        """
        Set discovered instruction
        """
        self.instr = instr

    def ReadPrevInstr(self):
        """
        Read previoiusly discovered instruction
        """
        return self.instr

    def NextInstr(self, r):
        """
        Set Instruction as a Node
        Update pointers (current and previous) for this loop-cycle.
        """
        SetNextInstr(r)

        # Can Explore Path
        return "next_seq_src2"

    def CheckTerm(self):
        """
        Check termination
        If all instructions are discovered then does termination.
        This event is at reaching to first instruction (pointer is zero).
        """
        prog = self.ReadProg()
        cont = False
        for func in prog.funcs:
            for bblock in func.bblocks:
                for instr in bblock.instrs:
                    if instr.discovered or len(instr.operands) == 0:
                        cont = cont | False
                    else:
                        cont = True

        if not cont and len(self.stack_ptr) == 0:
            return "term"
        else:
            return "next_reg_dst"


    def CheckBlockTerm(self):
        return self.ptr == 0

    def SearchDst(self):
        """
        Search Instruction having Undiscovered
        This module works when seeking pointer reaches to terimial nodes.
        This case needs to resets pointer to un-discovered instruction
            which is closest to end of file.
        """
        prog = self.prog
        f_ptr, b_ptr, i_ptr = self.ptr["f_ptr"], self.ptr["b_ptr"], self.ptr["i_ptr"]
        for f_index in range(f_ptr, -1,-1):
            num_bblocks = prog.funcs[f_index].num_bblocks - 1
            for b_index in range(num_bblocks, -1, -1):
                num_instrs = prog.funcs[f_index].bblocks[b_index].num_instrs - 1
                for i_index in range(num_instrs, -1, -1):
                    instr = prog.funcs[f_index].bblocks[b_index].instrs[i_index]
                    if not instr.discovered:
                        # Find dst node
                        prog.funcs[f_index].bblocks[b_index].instrs[i_index].discovered = True
                        ptr = {"f_ptr":f_index, "b_ptr":b_index, "i_ptr":i_index}
                        self.SetPtr(ptr)

                        self.num_exit += 1

                        return True

        # Could Not Find source node
        return False

    def SearchSrc(self, src=None):
        """
        Search Instruction having Source Operand
        """
        prog = self.prog
        f_ptr, b_ptr, i_ptr = self.ptr["f_ptr"], self.ptr["b_ptr"], self.ptr["i_ptr"]
        for f_index in range(f_ptr, -1,-1):
            num_bblocks = prog.funcs[f_index].num_bblocks - 1
            for b_index in range(num_bblocks, -1, -1):
                num_instrs = prog.funcs[f_index].bblocks[b_index].num_instrs - 1
                for i_index in range(num_instrs, -1, -1):
                    instr = prog.funcs[f_index].bblocks[b_index].instrs[i_index]
                    if instr.dst == src and src != None:
                        # Found source node
                        ptr = {"f_ptr":f_index, "b_ptr":b_index, "i_ptr":i_index}
                        self.hit_ptr = ptr
                        return True

        # Could Not Find source node
        return False


        i_ptr = prog.funcs[f_ptr].bblocks[b_ptr].num_instrs - 1

def DataFlowExploreOriginal(operand="src2", r=None, g=None):
    """
    Common Processing task for Source-1 and -2
    """
    # Fetch Present Instr
    instr = r.ReadInstr(r.ReadPtr())
    instr_dst = instr.dst
    instr_src = FetchSrc(src=operand, instr=instr)

    # Find instruction having source operand as destination operand
    match = r.SearchSrc(src=instr_src)
    num_operands = len(instr.operands)


    # Draw Edge when destination addressed by current pointer is matched
    if match:
        # Push current pointer when forwarding source-2 path
        if "src2" == operand and not (is_None(instr.operands[0]) or is_Val(instr.operands[0])):
            r.PushPtr()

        # Marking when source-1 (means source-2 path is already discovered), or
        #   source-1 is terminal
        if "src1" == operand or ("src2" == operand and (is_None(instr.operands[0]) or is_Val(instr.operands[0]))):
            r.CheckInstr()
            g.Count()

        # Fetch hit-instruction
        next_instr = r.ReadInstr(r.ReadHitPtr())

        # Update current pointer to hit instruction position
        if len(next_instr.operands) > 0:
            r.SetPtr(r.ReadHitPtr())

        # Drawing the edge
        attrib = "[color=blue dir=back]"
        g.edge(instr.nemonic, next_instr.nemonic, extra=attrib)

        # Forward source-2 Path
        if len(next_instr.operands) == 2 and not is_Val(next_instr.operands[1]):
            # Discovering souce-2 path when source-2 is not value (terminal)
            return "next_seq_src2"
        elif len(next_instr.operands) == 2 and is_Val(next_instr.operands[1]):
            # Skip source-2 discovering when source-2 is value (terminal)
            return "next_seq_src1"
        elif len(next_instr.operands) == 1 and not is_Val(next_instr.operands[0]):
            # Discovering source-1 path
            return "next_seq_src1"
        elif r.DepthStack() > 0:
            # Reaches here if #of operands is less than two and
            #   source-1 is value (teminal)
            r.PopPtr(SrcNo="Src2")
            return "next_seq_src1"
        else:
            # Otherwise dicovering next instruction
            #   (all sources are a terminal)
            r.CheckInstr()
            return "next_reg_dst"
    else:
        # Mis-Match Cases
        # 2.  operand == "src1"
        #   2.1.  source-1 is value (True == is_Val())
        #       Next_State = next_reg_dst
        if 0 == num_operands:
            src1_is_Val = False
        else:
            src1_is_Val = is_Val(instr.operands[0])

        #   2.2.  source-1 is None (True == is_Nan())
        #       Next_State = next_reg_dst
        if 0 == num_operands:
            src1_is_None = True
        else:
            src1_is_None = is_None(instr.operands[0])

        #   2.3.  source-1 is a terminal node
        #       Pop stack and update current pointer
        #       Next_State = next_seq_src1
        src1_is_Term = src1_is_Val or src1_is_None

        # 3.  operand == "src2"
        #   3.1.  source-2 is value (True == is_Val())
        #       Next_State = next_seq_src1
        if 2 == num_operands:
            src2_is_Val = is_Val(instr.operands[1])
        else:
            src2_is_Val = False

        #   3.2.  source-2 is None (True == is_Nan())
        #       Next_State = next_seq_src1
        if 2 == num_operands:
            src2_is_None = is_None(instr.operands[1])
        else:
            src2_is_None = False

        #   3.3.  source-2 is a terminal node
        #       Next_State = next_seq_src1
        src2_is_Term = src2_is_Val or src2_is_None


        # 1.  instr is a sink node
        # No Source Operand
        if 0 == num_operands:
            src_is_Val = False
            if is_None(instr_dst):
                dst_is_Sink = True
                src_is_None = True
            elif "ret" == instr.opcode:
                dst_is_Sink = True
                src_is_None = True
            elif "call" == instr.opcode:
                dst_is_Sink = False
                src_is_None = True
            elif "br" == instr.opcode:
                r.CheckInstr()
                dst_is_Sink = True
                src_is_None = True
            elif "jmp" == instr.opcode:
                r.CheckInstr()
                dst_is_Sink = True
                src_is_None = True
            elif "alloca" == instr.opcode:
                dst_is_Sink = False
                src_is_None = True
            else:
                dst_is_Sink = False
                src_is_None = False

        # Single Source Operand
        elif 1 == num_operands:
            dst_is_Sink = not is_None(instr_dst)
            src_is_None = src1_is_None
            src_is_Val = src1_is_Val
            if dst_is_Sink and not src_is_None:
                r.CheckInstr()

        # Multiple Source Operands
        else:
            dst_is_Sink = is_None(instr_dst)
            src_is_None = src1_is_None and src2_is_None
            src_is_Val = src1_is_Val and src2_is_Val

        # Token on Dst Part is Sink
        is_Sink = dst_is_Sink


        if src_is_Val:
            # Source is Immediate Value
            r.SetPrevInstr(instr=instr)
            return "next_reg_dst"
        elif src2_is_Term:
            # Source-2 is Terminal,
            #   so dicovers source-1 path
            return "next_seq_src1"
        elif src1_is_Term:
            # Source-1 is terminal,
            #   so pop-stack and discovers source-2 after
            #   checking a termination
            r.CheckInstr()
            r.PopPtr(SrcNo="Src1")
            return "next_check_term"
        elif is_Sink and (src_is_None or src_is_Val):
            # Forwarding to next instruction
            #   when instruction is sink node without sources
            r.SetPrevInstr(instr=instr)
            r.CheckInstr()
            return "next_reg_dst"
        elif "src2" == operand:
            # Second Source Exploration is done
            return "next_seq_src1"
        elif "src1" == operand:
            # Reaches here after source-2 path discovering,
            #   AND there is no node for source-1 ID.
            r.PopPtr(SrcNo="Src1")
            r.SearchDst()
            return "next_seq_src2"
        else:
            r.CheckInstr()
            r.SetPrevInstr(instr=instr)
            return "next_reg_dst"


def DataFlowExplore(operand="src2", r=None, g=None):
    """
    Common Processing task for Source-1 and -2
    """

    # Fetch Present Instr
    instr = r.ReadInstr(r.ReadPtr())
    instr_dst = instr.dst
    instr_src = FetchSrc(src=operand, instr=instr)

    # Find instruction having source operand as destination operand
    match = r.SearchSrc(src=instr_src)
    num_operands = len(instr.operands)

    # Draw Edge when destination addressed by current pointer is matched
    if match:
        # Push current pointer when forwarding source-2 path
        if "src2" == operand and not (is_None(instr.operands[0]) or is_Val(instr.operands[0])):
            r.PushPtr()

        # Marking when source-1 (means source-2 path is already discovered), or
        #   source-1 is terminal
        if "src1" == operand or ("src2" == operand and (is_None(instr.operands[0]) or is_Val(instr.operands[0]))):
            r.CheckInstr()
            g.Count()

        # Fetch hit-instruction
        next_instr = r.ReadInstr(r.ReadHitPtr())

        # Update current pointer to hit instruction position
        if len(next_instr.operands) > 0:
            r.SetPtr(r.ReadHitPtr())

        # Drawing the edge
        attrib = "[color=blue dir=back]"
        g.edge(instr.nemonic, next_instr.nemonic, extra=attrib)

        # Forward source-2 Path
        if len(next_instr.operands) == 2 and not is_Val(next_instr.operands[1]):
            # Discovering souce-2 path when source-2 is not value (terminal)
            if DEBUG:
                print("    Go to Src-2")
            return "next_seq_src2"

        elif len(next_instr.operands) == 2 and is_Val(next_instr.operands[1]):
            # Skip source-2 discovering when source-2 is value (terminal)
            if DEBUG:
                print("    Go to Src-1")
            return "next_seq_src1"

        elif len(next_instr.operands) == 1 and not is_Val(next_instr.operands[0]):
            # Discovering source-1 path
            if DEBUG:
                print("    Go to Src-1")
            return "next_seq_src1"

        elif r.DepthStack() > 0:
            # Reaches here if #of operands is less than two and
            #   source-1 is value (teminal)
            r.PopPtr(SrcNo="Src2")
            if DEBUG:
                print("    Go to Src-1")
            return "next_seq_src1"

        else:
            # Otherwise dicovering next instruction
            #   (all sources are a terminal)
            r.CheckInstr()
            return "next_reg_dst"
    else:
        # Mis-Match Cases
        return "next_reg_dst"


def IR_Parser( dir_ll, file_name, )

    openfile = dir_ll + file_name + ".ll"
    prog = None

    with open(openfile, "r") as llvm_ir:
        """
        LLVM-IR file-open, and parsing the IR file
        """
        prog = asm_parser(llvm_ir)
        prog.name = file_name.split(".")[0]
        print("File: {} parsed.".format(file_name))

        return prog


def InitInstr(prog):
    """
    Initialize Graph Constructor
    """

    # Pointer Extraction
    f_ptr = prog.num_funcs - 1
    if (f_ptr < 0):
        f_ptr = 0
    b_ptr = prog.funcs[f_ptr].num_bblocks - 1

    if (b_ptr < 0):
        b_ptr = 0
    i_ptr = prog.funcs[f_ptr].bblocks[b_ptr].num_instrs - 1

    if (i_ptr < 0):
        i_ptr = 0
    ptr = {"f_ptr":f_ptr, "b_ptr":b_ptr, "i_ptr":i_ptr}
    instr = prog.funcs[f_ptr].bblocks[b_ptr].instrs[i_ptr]

    # Instruction Adjacency Matrix Size Extraction
    total_num_instrs = 0
    total_num_bblocks = 0
    for func in prog.funcs:
        total_num_bblocks += func.num_bblocks
        for bblock in func.bblocks:
            total_num_instrs += bblock.num_instrs

    return ptr, prog.num_funcs, total_num_bblocks, total_num_instrs, instr


def CDFG_Gen_Simple( dir_dot ):

    # Create Objects constructing
    #   hierarchical instructin structure
    # Setting Initial State
    ptr, \
    total_num_funcs, \
    total_num_blocks, \
    total_num_instrs, \
    instr = InitInstr(prog)

    next_instr = instr
    Next_State = "next_seq_src2"


    with open(dir_dot+prog.name + "_dfg_o.dot", "w") as out:
        # Graph Utilities
        g = GraphUtils(out, total_num_instrs)

        # Graph Header Description
        g.start_df_graph()

        # Utilities
        r = RegInstr(prog=prog, ptr=ptr)

        # Processing Body
        while "term" != Next_State:

            # Sequence for Source-2 (Right)
            if "next_seq_src2" == Next_State:
                Next_State = DataFlowExploreOriginal(operand="src2", r=r, g=g)

            # Sequence for Source-1 (Left)
            if "next_seq_src1" == Next_State:
                Next_State = DataFlowExploreOriginal(operand="src1", r=r, g=g)

            # Check Termination
            if "next_check_term" == Next_State:
                Next_State = r.CheckTerm()

            # Move Next Instruction
            if "next_reg_dst" == Next_State:
                Next_State = r.NextInstr(r=r)

        # Write Edges
        for edge in g.edges:
            g.write(edge)

        g.write("}")


def remove_duplicate_edges(num_dup, start_no, lines):
    """
    Remove Dupplicate (Same) Edges
    """
    if lines is not None:
        for index_no in range(start_no, len(lines)-num_dup, 1):
            lines[index_no] = lines[index_no+1]

        for index_no in range(len(lines)-num_dup, len(lines), 1):
            lines[index_no] = ""

    return lines


def depl_remover(dir_ll):

    # Duplicate Remover
    # Directory path maintains LLVM-IR file
    openfile = dir_ll + prog.name+"_dfg_o.dot"
    dot_file_name = prog.name

    present_lines = []
    lines = []
    num_dup = 0

    with open(openfile, "r") as dot_file:
        for present_line in dot_file:
            present_lines.append(present_line)

    # Seek Same Line with Scan-Line Method
    for present_no in range(len(present_lines)):
        present_line = present_lines[present_no]
        for compare_no, compare_line in enumerate(present_lines[present_no:len(present_lines)-num_dup]):
            if compare_no == 0:
                lines.append(present_line)

            elif compare_line == present_line and compare_no > 0:
                num_dup += 1
                start_no = present_no+compare_no
                present_lines = remove_duplicate_edges(num_dup, start_no, present_lines)


    print("Total {} lines removed.".format(num_dup))

    #Write after removing
    #post-fix:  "_dfg_r"
    dot_file_r_name = "../temp/llvmcdfggen/"+dot_file_name+"_dfg_r.dot"
    with open(dot_file_r_name, "w") as dot_file:
        dot_file.writelines(lines)


def line_reorder(dir_ll):
    openfile = dir_ll + prog.name+"_dfg_r.dot"
    lines_ = []
    with open(openfile, "r") as dot_file:
        for present_line in dot_file:
            lines_.append(present_line)

    dot_file_r_name = dir_ll+dot_file_name+"_dfg.dot"
    with open(dot_file_r_name, "w") as dot_file:
        dot_file.write(lines_[0])
        dot_file.write(lines_[1])
        dot_file.write(lines_[2])

        for line_no in range(len(lines)-2, 3, -1):
            dot_file.write(lines_[line_no-1])

        dot_file.write("}")


def cfg_extractor(r=None, prog=prog, out=None):
    """
    Control Graph Extractor
    """
    dir_ll = "../temp/src/"
    openfile = dir_ll + file_name+".ll"
    with open(openfile, "r") as llvm_ir:
        """
        LLVM-IR file-open, and parsing the IR file
        """
        print("File: {} parsed.".format(file_name))

        # Fetch Basic Block Label
        for bb_f_indx in range(prog.num_funcs):
            #print(prog.funcs[bb_f_indx].num_bblocks)
            # Fetch Target BBlock
            for bb_b_indx in range(prog.funcs[bb_f_indx].num_bblocks):
                bb_i_indx = prog.funcs[bb_f_indx].bblocks[bb_b_indx].num_instrs - 1
                target_nemonic = prog.funcs[bb_f_indx].bblocks[bb_b_indx].name
                br_t = prog.funcs[bb_f_indx].bblocks[bb_b_indx].instrs[bb_i_indx].br_t
                br_f = prog.funcs[bb_f_indx].bblocks[bb_b_indx].instrs[bb_i_indx].br_f

                # Fetch Destination Node of BBlock
                for f_indx in range(prog.num_funcs):
                    for b_indx in range(prog.funcs[f_indx].num_bblocks):
                        if b_indx != bb_b_indx:
                            if DEBUG:
                                print(prog.funcs[f_indx].bblocks[b_indx].name)

                            # Assign Node label
                            if prog.funcs[f_indx].bblocks[b_indx].name is not None:
                                if "entry" in prog.funcs[f_indx].bblocks[b_indx].name:
                                    b_label = "entry"
                                else:
                                    b_label = "label:<"+prog.funcs[f_indx].bblocks[b_indx].name+">"
                            else:
                                break

                            # Fetch BBlock Name
                            b_nemonic = prog.funcs[f_indx].bblocks[b_indx].name

                            # Fetch Number of Instrs in the BBlock
                            num_instrs = prog.funcs[f_indx].bblocks[b_indx].num_instrs
                            instr = prog.funcs[f_indx].bblocks[b_indx].instrs[num_instrs - 1]
                            fro = target_nemonic
                            to = b_nemonic
                            if DEBUG:
                                print("L: {}  T[{}]  F[{}]".format(b_label, br_t, br_f))

                            if br_t is not None and b_label == br_t:
                                if DEBUG:
                                    print("T-Matched:{}".format(br_t))
                                if fro == "entry":
                                    attrib = "[color=black dir=black]"
                                elif br_t == br_f:
                                    attrib = "[color=red dir=black]"
                                else:
                                    attrib = "[color=blue dir=black]"
                                out.write("\"%s\" -> \"%s\"%s\n" % (fro, to, attrib))

                            if br_f is not None and b_label == br_f and br_t != br_f:
                                if DEBUG:
                                    print("F-Matched:{}".format(br_f))
                                attrib = "[color=green dir=black]"
                                out.write("\"%s\" -> \"%s\"%s\n" % (fro, to, attrib))

                num_instrs = prog.funcs[bb_f_indx].bblocks[bb_b_indx].num_instrs
                instr = prog.funcs[bb_f_indx].bblocks[bb_b_indx].instrs[num_instrs - 1]
                b_nemonic = prog.funcs[bb_f_indx].bblocks[bb_b_indx].name
                to = b_nemonic
                if instr.opcode == "ret" and bb_f_indx == (prog.num_funcs-1) and bb_b_indx == (prog.funcs[bb_f_indx].num_bblocks-1):
                    attrib = "[color=black dir=black]"
                    out.write("\"%s\" -> \"%s\"%s\n" % (to, "ret", attrib))

        out.write("}")


def Main_Gen_LLVMtoCDFG(r_file_path, r_file_name):

    prog = ReadProgram(r_file_path, r_file_name)

    with open("../temp/llvmcdfggen/"+prog.name + "_cfg.dot", "w") as out:
        # Graph Utilities
        g_cfg = GraphUtils(out, total_num_instrs)

        # Graph Header Description
        g_cfg.start_cf_graph()
        cfg_extractor(r=r, prog=prog, out=out)

    def dupl_remover(dir_ll, dot_file_name, prog):
        dot_file_name = prog.name+"_cfg.dot"
        openfile = dir_ll + dot_file_name

        present_lines = []
        lines = []
        num_dup = 0

        with open(openfile, "r") as dot_file:
            for present_line in dot_file:
                present_lines.append(present_line)

        # Seek Same Line with Scan-Line Method
        for present_no, present_line in enumerate(present_lines):
            for compare_no, compare_line in enumerate(present_lines):
                if compare_no == 0:
                    lines.append(present_line)
                elif compare_line == present_line and compare_no != present_no:
                    #print("duplicated.")
                    num_dup += 1
                    start_no = present_no+compare_no
                    for index_no in range(start_no, len(present_lines)-1, 1):
                        present_lines[index_no] = present_lines[index_no+1]

                    present_lines[len(present_lines)-1] = ""

        print("Total {} lines removed.".format(num_dup))

        dot_file_name = "../temp/llvmcdfggen/"+prog.name+"_cfg_r.dot"
        with open(dot_file_name, "w") as dot_file:
            for line_no in range(len(present_lines)):
                dot_file.write(present_lines[line_no])


