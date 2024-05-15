def ExtractNumber(element):
    """
    Extract Number (str) of Destination Register Index
    Register index number in LLVM-IR has prefix "%".
    """

    start_index = element.find('%') + 1
    end_index = element[start_index:].find(' ') + start_index
    number_str = element[start_index:end_index].strip()
    # When the string does not have digit number, set infiity number
    number = int(number_str) if number_str.isdigit() else float('inf')
    return number


def FlattenList(nested_list):
    """
    Flattening Nested List

    Arguments:
        nested_list:    nested data-flow list for a basic block

    Basic block can have multiple paths forming a nested list
    To generate IR-code in the basic block, it needs frattening the list before sorting.
    """

    flattened_list = []
    for item in nested_list:
        if isinstance(item, list):
            flattened_list.extend(FlattenList(item))
        else:
            flattened_list.append(item)
    return flattened_list


def SortList(lst):
    """
    Sorting LLVM-IR with Destination Register Index Number
    The sorting skips branch IR-code having "br" string.
    """

    result = []
    for list_ in lst:
        flattened_lst = FlattenList(list_)
        sorted_lst = sorted(flattened_lst, key=lambda x: (ExtractNumber(x.split(' ')[0]), not x.strip().startswith("br")))
        result = result + sorted_lst[::-1]
    return result


def Parser( Paths_, mode ):
    """
    Parser

    Arguments
        Paths_:     Set of Paths (list type)
        mode:       Parsing mode
                        'dfg'       Data-Flow Graph
                        otherwise   Control-Flow Graph
    """

    if mode == 'dfg':
        Paths = []
        num = 0
        for path_ in Paths_:
            path = []
            nodes = path_.split("][")
            if len(nodes) > 1:
                for node_infos in nodes:
                    node_infos = node_infos.replace("[", '')
                    node_infos = node_infos.replace("]", '')
                    node_infos = node_infos.replace("'", '')
                    node_infos = node_infos.replace(",", '')
                    node_infos = node_infos.split(" ")

                    node_info = []
                    for item in node_infos:
                        node_info.append(item)

                    path.append(node_info)

                Paths = path

            else:
                nodes = path_.split(", ")
                for node_info in nodes:
                    node_info = node_info.replace("[", '')
                    node_info = node_info.replace("]", '')
                    node_info = node_info.replace("'", '')
                    node_info = node_info.replace(",", '')

                    path.append(node_info)

                Paths.append(path)
            num += 1
    elif mode == 'nemonic':
        Paths = []
        num = 0
        for node in Paths_:
            nodes = node.split("\"")
            path = []
            for node_info in nodes:
                node_info = node_info.replace("[", '')
                node_info = node_info.replace("]", '')
                node_info = node_info.replace("'", '')
                if '' != node_info:
                    path.append(node_info)

            Paths.append(path)

            num += 1
    else:
        Paths = []
        for line in Paths_:
            line = line.split('], [')

            for path_ in line:
                path_ = path_.split(', ')
                path = []
                for node_id in path_:
                    node_id = node_id.replace("'", '')
                    node_id = node_id.replace("[", '')
                    node_id = node_id.replace("]", '')
                    node_id = node_id.replace("[]", '')
                    node_id = node_id.replace("][", '')
                    node_id = node_id.replace(",", '')
                    path.append(node_id)

                Paths.append(path)
    return Paths


def ReadDFG( r_file_path2="./", r_file_path="./", r_file_name="mvm", cfg_node_id="1"):
    """
    Read Data-Flow Graph, its Node List, and its Nemonic List

    Arguments:
        r_file_path:    reding file path
        r_file_name:    reading base file name
        cfg_node_id:    Cyclic Control-Flow Node-ID
    """

    r_path_file_name = r_file_name+"_"+cfg_node_id+"_bpath_st.txt"
    dfg_paths = ReadFile(file_path=r_file_path2, file_name=r_path_file_name )
    DFG_Paths = Parser( dfg_paths, 'dfg' )
    #print("    DFG Paths:{}".format(DFG_Paths))

    r_node_list_file_name = r_file_name+"_"+cfg_node_id+"_node_list.txt"
    dfg_node_list = ReadFile(file_path=r_file_path, file_name=r_node_list_file_name )
    DFG_Node_List = Parser( dfg_node_list, 'dfg' )
    #print("    DFG Node List:{}".format(DFG_Node_List))

    r_nm_list_file_name = r_file_name+"_"+cfg_node_id+"_nemonic_list.txt"
    nm_node_list = ReadFile(file_path=r_file_path, file_name=r_nm_list_file_name )
    NM_Node_List = Parser( nm_node_list, 'nemonic' )
    #print("    DFG Node List:{}".format(DFG_Node_List))

    return DFG_Paths, DFG_Node_List, NM_Node_List


class Create_CFGNode:
    """
    Node Class

    Role:
        Node having Data Structure for Control-Flow Graph.
    """

    def __init__(self):
        self.ID = ""
        self.StLdPaths = []
        self.NeighborNodes = []
        self.Explored = False
        self.num_paths = 0
        self.num_nodes = 0
        self.read_cnt = 0
        self.read_ptr = 0


    def ReadNeighborExplored(self):
        """
        Read Neighbor's Explored Flag
        """
        return self.NeighborNodes[1][1]


    def ReadPathNo(self, Src, Dst, index):
        """
        Read Path Number
        """
        if self.read_cnt == self.num_paths:
            return index, Src, Dst, False

        if self.read_ptr == self.num_paths:
            return index, Src, Dst, False

        for no, StLdPath in enumerate(self.StLdPaths):
            if not StLdPath[1]:
                for st_no in StLdPath[2][Dst]:
                    for id in st_no:
                        if id == index:
                            self.StLdPaths[no][1] = True
                            self.read_cnt += 1
                            return index, Src, Dst, no

        for no, StLdPath in enumerate(self.StLdPaths):
            if not StLdPath[1]:
                for st_no in StLdPath[2][Src]:
                    for id in st_no:
                        if id == index:
                            self.StLdPaths[no][1] = True
                            self.read_cnt += 1
                            return index, Src, Dst, no

        temp_ptr = self.read_ptr
        for no, StLdPath in enumerate(self.StLdPaths):
            if not StLdPath[1]:
                self.StLdPaths[no][1] = True
                if self.read_ptr < self.num_paths:
                    self.read_ptr += 1
                if Src == Dst:
                    return self.StLdPaths[no][2][Src][0][0], Src, Dst^1, no
                else:
                    return self.StLdPaths[no][2][Src][0][0], Src, Dst, no

        return -1, Src, Dst, False


    def ClrExplores(self):
        """
        Clear Explore Flag
        """
        for StLdPath in self.StLdPaths:
            StLdPath[1] = False


    def ReadNumPaths(self):
        """
        Read Number of Paths in Node
        """
        return self.num_paths


    def SetNodeID(self, ID):
        """
        Set This Node's ID
        """
        self.ID = ID

    def ReadNodeID(self):
        """
        Read This Node's ID
        """
        return self.ID

    def ReadNumNodes(self):
        """
        Read Number of Neighbor Nodes
        """
        return self.num_nodes

    def SetExplored(self):
        """
        Set Flag of Explored
            The flag is set at read node
        """
        self.Explored = True

    def ClrExplored(self):
        """
        Clear Flag of ExploredX
        """
        self.Explored = False

    def ReadExplored(self):
        """
        Read Flag of Explored
        """
        return self.Explored


    def SetNeighborNode(self, node_id):
        """
        Set Neighbor Node's ID,
        Initialize Flag-Explored
        """
        self.NeighborNodes.append([node_id, False])
        self.num_nodes += 1

    def SetNeigboorNode(self, node_id):
        """
        Set Neighbor's Node-ID
        Set Valid Flag
        """
        for neighbor_node in self.NeighborNodes:
            if neighbor_node[0] == node_id:
                neighbor_node[1] = True

    def ClrNeigboorNode(self, node_id):
        """
        Clear Neighbor's Valid Flag
        """
        for neighbor_node in self.NeighborNodes:
            if neighbor_node[0] == node_id:
                neighbor_node[1] = False

    def SetStLdPaths(self, path):
        """
        Register Path inside of This Node
        path:   DFG-Path
        False:  Init Flag for Path-Explored
        []:     Init Set of Store and Load Indeces
        """
        self.StLdPaths.append([copy.deepcopy(path), False, [[], []]])
        self.num_paths += 1

    def ReadStLdPaths(self):
        """
        Read Set (List) of Store-Load Paths
        """
        return self.StLdPaths

    def ReadStLdPath(self, path_no):
        """
        Read Store-Load Path
        """
        return self.StLdPaths[path_no]

    def CheckStLdPaths(self, src):
        """
        Check Availability of Source Register Index in Store-Load Path
        """
        Chk_Src = False
        for StLdPath in self.StLdPaths:
            for src_indices in StLdPath[2][src]:
                for src_index in src_indices:
                    if src_index > 0:
                        Chk_Src = True

        return Chk_Src

    def ReadStLdPathExplored(self, path_no):
        """
        Read Explored-Flag of This Node's Path
        """
        return self.StLdPaths[path_no][1]


    def SetStLdIndex(self, path_no, st, index):
        """
        Set Store/Load Indeces to Path[path_no]
            st = 0:     Store
            ld = 1:     Load
        """
        self.StLdPaths[path_no][2][st].append(index)

    def ReadStLdIndex(self, path_no, st):
        """
        Read Path[path_no]
            st = 0:     Store
            ld = 1:     Load
        """
        return self.StLdPaths[path_no][2][st]

    def CheckExplored(self, node_id):
        """
        Check Explored Flag and Valid Flags
        """
        for neigbor_node in self.NeighborNodes:
            if neigbor_node[0] == node_id:
                return True, neigbor_node[1]

        return False, False

    def CheckAllExplored(self):
        """
        Check Explored Flag and Valid Flags
        """
        for neigbor_node in self.NeighborNodes:
            if neigbor_node[1]:
                return True, True

        return False, False

    def ClrNeigboorNodes(self):
        """
        Clear Neibor Node;s Explored Flag
        """
        for neigbor_node in self.NeighborNodes:
            neigbor_node[1] = False


class Create_CFGNodes:
    """
    Control Flow Graph Class

    Role:
        Structure of Graph
    """

    def __init__(self):
        self.path_ptr = 0
        self.node_ptr = 0
        self.nums = 0
        self.nodes = []

    def ReadInitNode(self):
        """
        Read Initial CFGNode
        """
        self.node_ptr += 1
        if self.node_ptr <= self.nums:
            return self.nodes[self.node_ptr-1]
        else:
            return -1

    def SetNode(self, node):
        """
        Register Node
        """
        self.nodes.append(copy.deepcopy(node))
        self.nums += 1

    def ReadNode(self, node_no):
        """
        Read Node
        """
        if node_no < len(self.nodes):
            return self.nodes[node_no]
        else:
            f = node_no//self.nums
            return self.nodes[node_no-f*self.nums]

    def SetExplored(self, node_id):
        """
        Set Explored Flag to Node
        """
        for index, node in enumerate(self.nodes):
            if node.ReadNodeID() == node_id:
                self.nodes[index].SetExpored()

    def SetNeigboorNode(self, node_id, chk_node_id):
        """
        Set Neighbor's Node-ID
        """
        for node in self.nodes:
            if node.ReadNodeID() == node_id:
                node.SetNeigboorNode(self, chk_node_id)

    def ClrNeigboorNode(self, node_id):
        """
        Clear Neighbor's Node-ID
        """
        for node in self.nodes:
            if node.ReadNodeID() == node_id:
                node.ClrNeigboorNode(self, node_id)

    def ReadExplored(self, node_id):
        """
        Check node_id is already explored
        """
        for node in self.nodes:
            if node.ReadNodeID() == node_id:
                return node.ReadExplored()

        return False

    def ClrAllExplored(self):
        """
        Clear Explored Flag for All
        """
        for node in self.nodes:
            node.ClrExplored()

    def ReadNum(self):
        """
        Read Number of (CFG) Nodes
        """
        return self.nums

    def SetStLdPaths(self, node_id, path):
        """
        Set Path to Node[node_id]
        """
        for node in self.nodes:
            if node.ReadNodeID() == node_id:
                node.SetStLdPaths(path)
                self.path_ptr += 1

    def SetStLdIndex(self, node_id, st, index):
        """
        Set Indeces to Node[node_id]
            st = 0:     Store
            st = 1:     Load
        """
        for node in self.nodes:
            if node.ReadNodeID() == node_id:
                node.SetStLdIndex(node.num_paths-1, st, index)

    def ReadCFGNode(self, cycle_no):
        """
        Read (CFG) Node
        """
        return self.nodes[cycle_no]

    def ReadCFGNodebyID(self, node_id):
        """
        Read (CFG) Node by ID
        """
        for node in self.nodes:
            if node.ReadNodeID() == node_id:
                return node
        return -1


    def Reorder(self, sw):
        """
        Reorder to Inverse Order
        """
        nodes = []
        if sw == 0:
            nodes.append(self.nodes[0])
            for index in range(self.nums-1, 0, -1):
                nodes.append(self.nodes[index])
        else:
            for index in range(self.nums-1, -1, -1):
                nodes.append(self.nodes[index])

        self.nodes = nodes


    def ReadNumNodes(self):
        """
        Read Number of (CFG) Nodes
        """
        return self.nums


    def ClrExplored(self):
        """
        Clear All Neighbors
        """
        for node in self.nodes:
            node.ClrNeigboorNodes()


    def ClrExplores(self):
        """
        Clear All Explore Flags
        """
        for node in self.nodes:
            node.ClrExplores()


def ReadIndex( DFG_Path, DFG_Node_List ):
    """
    Read Indeces of Store and Load IR Instructions
    - Begining Element in Data-Flow Path is Store Node of Data-Flow Path
    - End Element in Data-Flow Path is Load Node of Data-Flow Path

    Set -1 when register index number is not available.
    """

    # Read Indeces' ID to Access Node List
    if isinstance(DFG_Path, list) and len(DFG_Path) > 0:
        #print("    DFG-Path: {}".format(DFG_Path))

        cnt_st = 0
        st_index = []
        for st_node in DFG_Path:
            st_node_id = int(st_node)
            St_Node = DFG_Node_List[st_node_id][0]
            #print("  Store Node-{} ({})".format(st_node_id, St_Node))

            if "store" in St_Node:
                # Store-IR Instruction Detection
                St_Node = St_Node.split(" ")
                st_index1 = St_Node[2]
                if not "%" in st_index1:
                    st_index1 = -1
                    st_index.append(int(st_index1))
                else:
                    # First Source Register Index Number
                    st_index.append(int(st_index1[1:]))

                if len(St_Node) > 3:
                    st_index2 = St_Node[3]
                    if not "%" in st_index2:
                        st_index2 = -1
                        st_index.append(int(st_index2))
                    else:
                        # Second Source Register Index Number
                        st_index.append(int(st_index2[1:]))

                cnt_st += 1

        if cnt_st == 0:
            st_index = [-1]


        cnt_ld = 0
        ld_index = []
        for no in range(len(DFG_Path)-1, -1, -1):
            ld_node_id = int(DFG_Path[no])

            Ld_Node = DFG_Node_List[ld_node_id][0]
            #print("  Load Node-{} ({})".format(ld_node_id, Ld_Node))

            if "load" in Ld_Node or ((not "load" in Ld_Node) and (no == (len(DFG_Path)-1))):
                # Load-IR Instruction Detection
                Ld_Node = Ld_Node.split(" ")
                if (not "load" in Ld_Node) and (no == (len(DFG_Path)-1)):
                    ld_index1 = Ld_Node[1]
                else:
                    ld_index1 = Ld_Node[2]
                if not "%" in ld_index1:
                    ld_index1 = -1
                    ld_index.append(int(ld_index1))
                else:
                    # First Source Register Index
                    ld_index.append(int(ld_index1[1:]))

                if len(Ld_Node) > 3:
                    ld_index2 = Ld_Node[3]
                    if not "%" in ld_index2:
                        ld_index2 = -1
                        ld_index.append(int(ld_index2))
                    else:
                        # Second Source Register Index Number
                        ld_index.append(int(ld_index2[1:]))

            cnt_ld += 1

        if cnt_ld == 0:
            ld_index = [-1]


        # Find DFG-Node
        return st_index, ld_index
    else:
        return [-1], [-1]


def Preprocess( r_file_path2, r_file_path, r_file_name, CyclicPaths ):
    """
    Preprocessor

    Role:
        Construct Control-Flow Graph
    """

    #print("START PREPROCESS")

    CFGNodes = []
    NM_List = []
    for cycle_path in CyclicPaths:

        label_A = False
        #print("Work in CFG Cyclic-Loop Path: {}".format(cycle_path))
        Nodes = Create_CFGNodes()

        ptr = 0
        NM_list = []
        for cycle_id in range(len(cycle_path)):

            if label_A == False:
                # Get ID
                node_A_id = cycle_path[ptr]

                index = int(node_A_id)

                label_A = True

            if label_A == True:

                # Create Node
                node_A = Create_CFGNode()

                # Set This Node's ID
                node_A.SetNodeID(node_A_id)

                # Set Explored Flag
                node_A.SetExplored()

                # Set Forward Linked Node
                if ptr < (len(cycle_path)-1):
                    node_A.SetNeighborNode(cycle_path[ptr+1])
                else:
                    node_A.SetNeighborNode(cycle_path[0])

                # Set Backward Linked Node
                if ptr > 0 and ptr < len(cycle_path):
                    node_A.SetNeighborNode(cycle_path[ptr-1])
                else:
                    node_A.SetNeighborNode(cycle_path[-1])

                # Register Node
                #print("  CFG Node-{} is created".format(node_A_id))
                Nodes.SetNode(node_A)

                ptr += 1


            # Read This Block's DFG Paths
            #print("  Read DFG for CFG Node-{}".format(node_A_id))
            DFG_paths, node_list, nm_list = ReadDFG(r_file_path2=r_file_path, r_file_path=r_file_path2, r_file_name=r_file_name, cfg_node_id=node_A_id)
            NM_list.append([cycle_path[cycle_id]])
            NM_list[-1] = NM_list[-1]+[nm_list]

            # Set Store-Load Path if available
            if isinstance(DFG_paths, list) and len(DFG_paths) > 0:
                for no, DFG_path in enumerate(DFG_paths):
                    #print("    Path-{}".format(no))
                    #print("      Set Path: {}".format(DFG_path))
                    Nodes.SetStLdPaths(node_A_id, DFG_path)

                    St_Index, Ld_Index = ReadIndex(DFG_Path=DFG_path, DFG_Node_List=node_list)

                    #print("      Set Indeces: Store{} Load{}".format(St_Index, Ld_Index, DFG_path))
                    Nodes.SetStLdIndex(node_id=node_A_id, st=1, index=St_Index)
                    Nodes.SetStLdIndex(node_id=node_A_id, st=0, index=Ld_Index)
            else:
                label_A = False


            # Check Neighbor Node Availabiliyty
            if node_A.ReadNumNodes() != 0 and label_A == True:

                # Get Neighbor Node's ID
                if ptr == len(cycle_path):
                    CFGNodes.append(Nodes)
                    break

                node_C_id = cycle_path[ptr]

                # Check Node-C is already Explored
                if Nodes.ReadExplored(node_C_id):

                    #Back to Previous CFG-Node
                    ptr -= 1
                    node_id = cycle_path[ptr]

                    # Check node_ is the "node-A"
                    if node_id == node_A.ReadNodeID():

                        # Read Remained Neighbor Node
                        remained_node = Nodes.ReadNeighborNode(node_id)

                        if isinstance(remained_node, int):
                            # remained_node == -1 then Exit
                            return Nodes
                        else:
                            node_A_id = remained_node.ReadNodeID()
                            #print("  Set Node-{} to Node-A".format(node_A_id))
                            label_A = True

                else:
                    #print("  Set New Node-{} to Node-A".format(node_C_id))
                    node_A_id = node_C_id
                    label_A = True
        NM_List.append(NM_list)

    return CFGNodes, NM_List


def BranchNodeTracker(CFG_Nodes):
    """
    Finding Branch CFG-Node used for transitting between Cyclic Control-Flow
    """

    BranchList = []
    for CycleNo, CFGNodes in enumerate(CFG_Nodes):
        for CFG_No in range(CFGNodes.ReadNumNodes()):

            CFGNode = CFGNodes.ReadCFGNode(CFG_No)
            CFGNode_ID = CFGNode.ReadNodeID()

            CFGNodeBranchList = []

            for Chk_CycleNo in range(CycleNo+1, len(CFG_Nodes), 1):
                for Chk_Node_No in range(CFG_Nodes[Chk_CycleNo].ReadNumNodes()):

                    Chk_CFGNode = CFG_Nodes[Chk_CycleNo].ReadNode(Chk_Node_No)
                    Chk_CFGNode_ID = Chk_CFGNode.ReadNodeID()

                    if Chk_CFGNode_ID == CFGNode_ID:
                        CFGNodeBranchList.append([Chk_CycleNo, Chk_CFGNode_ID])

            if len(CFGNodeBranchList) > 0:
                BranchList.append([CycleNo, CFGNodeBranchList])

    return BranchList


def ReadBranchNodeID(CycleNo, BranchList):
    """
    Read Branch CFG Node-ID
    """

    for BranchInfo in BranchList:
        Cycle_ID = BranchInfo[0]
        if Cycle_ID == CycleNo:
            return BranchInfo[1][0]

    return -1


Record = []

def PathPicker(CycleNo, Node_Ptr, BranchList, CFGNode_Src, CFG_Nodes, Path, CFG, TurnNo, Src_Index, Src, Dst, Step_Count):
    """
    Data-Flow Path Picker

    Arguments:
        CycleNo:        Cyclic Control-Flow ID
        Node_Ptr:       Node Pointer
        BranchList:     List for Branching CFG Node
        CFGNode_Src:    Source CFG-Node
        Path:           Picking Path List
        Src_Index:      Source REgister Index Number
        Src:            Pick Index for Source Register Index Number
        Dst:            Pick Index for Destination Register Index Number
    """

    No_Path = False
    Stop = False
    explored = False
    Tmp_Node_Ptr = Node_Ptr

    # Check Node Availability
    if isinstance(CFGNode_Src, int):
        if Node_Ptr == 0:
            # There is NO Available Node
            return No_Path, CFG, Path
        else:
            Node_Ptr -= 1

    # Get Branching Target Node Information
    BranchInfo = ReadBranchNodeID(CycleNo, BranchList)
    if isinstance(BranchInfo, list):
        # Target Cycle Number
        Branch_Cycle_No = BranchInfo[0]

        # Target Node ID
        Branch_Node_ID = BranchInfo[1]
    else:
        Branch_Cycle_No = -1
        Branch_Node_ID = -1

    # Search Body
    Next_Path_No = 0

    while True:

        Find = False
        Block_Multiple_Dst = -1

        # Get Path-Number
        Repair_Src_Index, Src, Dst, Path_No = CFGNode_Src.ReadPathNo(Src, Dst, Src_Index)
        chk_vld, explored = CFGNode_Src.CheckAllExplored()
        if (Repair_Src_Index != -1) and (Repair_Src_Index != Src_Index) and not Repair_Src_Index in Record:
            CFGNode_Dst =  CFG_Nodes[CycleNo].ReadNode(Node_Ptr+1)
            chk_vld_, explored_ = CFGNode_Dst.CheckAllExplored()
            if explored_:
                return False, CFG, Path
            Record.append(Repair_Src_Index)
            for CFGNodes in CFG_Nodes:
                CFGNodes.ClrExplored()
                CFGNodes.ClrExplores()

            TurnNo = 0
            Path.append([])
            Path_Src = [[], False, [[-1], [-1]]]
            Node_Ptr = 0

            CFG.append([Repair_Src_Index])
        elif Repair_Src_Index in Record and explored:
            return False, CFG, Path
        elif Repair_Src_Index in Record and not explored and Src_Index == Repair_Src_Index:
            CFGNode_Dst =  CFG_Nodes[CycleNo].ReadNode(Node_Ptr)
            chk_vld_, explored_ = CFGNode_Dst.CheckAllExplored()
            if isinstance(Path_No, int ) and Path_No == 0 and explored_:
                return False, CFG, Path
            elif isinstance(Path_No, bool ) and not Path_No and Node_Ptr == 0 and not explored_ and CFGNode_Dst.ReadNodeID() == CFGNode_Src.ReadNodeID():
                return False, CFG, Path


        # There is NO available path
        if Path_No is False:
            #if Next_Path_No == len(CFGNode_Src.StLdPaths):
            #    break

            if Next_Path_No < CFGNode_Src.num_paths and Node_Ptr != Step_Count:
                if CFGNode_Src.num_paths <= Next_Path_No+1:
                    Path_Src = CFGNode_Src.ReadStLdPath(Next_Path_No)
                    Next_Path_No += 1
                else:
                    break

                Node_Ptr -= 1
                CFGNode_Dst =  CFG_Nodes[CycleNo].ReadNode(Node_Ptr+1)

                for Path_Dst_No in range(CFGNode_Dst.ReadNumPaths()):
                    # Get one path
                    Dst = Dst^1
                    Path_Src = CFGNode_Dst.ReadStLdPath(Path_Dst_No)
                    Indices_Dst = Path_Src[2]
                    Dst_Indices = Indices_Dst[Dst][0]
                    Stop = False
                    for Dst_Index in Dst_Indices:
                        if Dst_Index == Src_Index:
                            Stop = True
                            break

                    if Stop:
                        break

                Src_Indices = [Src_Index]

                No_Path = True
            elif isinstance(Branch_Node_ID, int) and (int(Branch_Node_ID) > -1) and (Branch_Cycle_No > -1):
                #### NOT NEEDED SECTION
                No_Path = True
                break
            else:
                break

        BackPath = []
        if not No_Path:
            # Get one path by Path-Number
            Path_Src = CFGNode_Src.ReadStLdPath(Path_No)
            Indeces = Path_Src[2]

            # Get set of indices
            Src_Indices = Indeces[Src][0]

        # Blcok Multiple Sources having same index
        Block_Multiple_Src = -1



        for Src_Index in Src_Indices:

            Find = False

            if Block_Multiple_Src != Src_Index and (Repair_Src_Index == Src_Index):

                # Mark index to block
                Block_Multiple_Src = Src_Index

                # Set repairing index number
                Repair_Src_Index = Src_Index

                # Tempral node pointer needed for restarting the search in while-loop
                Tmp_Node_Ptr = Node_Ptr

                # Check source index register number
                if Src_Index != -1:
                    While_Continue = True
                    Break_Point = False
                    while While_Continue:


                        # Get neighbot node
                        CFGNode_Dst =  CFG_Nodes[CycleNo].ReadNode(Tmp_Node_Ptr+1)


                        # Check destination node was already explored
                        chk_vld, explored = CFGNode_Src.CheckExplored(CFGNode_Dst.ReadNodeID())

                        # Fetched node is branching node then enter
                        if chk_vld and not explored and CFGNode_Dst.ReadNodeID() == Branch_Node_ID:

                            # Mark this neighbor node is explored
                            CFGNode_Src.SetNeigboorNode(CFGNode_Dst.ReadNodeID())

                            if not CFGNode_Src.ReadNodeID() in CFG[-1]:
                                CFG[-1] = CFG[-1]+[CFGNode_Src.ReadNodeID()]

                            # Go to next cycle-path having same
                            No_Path, CFG_Dst, Path_Dst = PathPicker(Branch_Cycle_No, Node_Ptr, BranchList, CFG_Nodes[Branch_Cycle_No].ReadCFGNodebyID(CFGNode_Dst.ReadNodeID()), CFG_Nodes, Path, CFG, TurnNo, Src_Index, Dst, Dst, 0)


                            # Concat paths
                            Path_Concat = Path_Src[0]
                            if Path_Dst[-1] != None:
                                ####UPDATE
                                if TurnNo == 0:
                                    Path_Concat = Path_Dst[-1]+Path_Src[0]
                                else:
                                    Path_Concat = Path_Src[0]+Path_Dst[-1]

                            BackPath = Path_Concat

                            TurnNo = TurnNo ^ 1


                            # Return then adjust the Dst and Src flags
                            if len(BackPath) > 0:
                                Dst = Dst
                                Src = Src^1

                                # Returned so not explore this destination node
                                if not No_Path:
                                    Break_Point = True


                        # Check Node Availability
                        if not Break_Point and isinstance(CFGNode_Dst, int):
                            if CycleNo < (CFG_Nodes[CycleNo].ReadNumNodes()):
                                # Mark this neighbor node is explored
                                CFGNode_Src.SetNeigboorNode(CFGNode_Dst.ReadNodeID())

                                if not CFGNode_Src.ReadNodeID() in CFG[-1]:
                                    CFG[-1] = CFG[-1]+[CFGNode_Src.ReadNodeID()]

                                # There is NO available node, Explore nenxt cyclic path
                                No_Path, CFG_Dst, Path_Dst = PathPicker(CycleNo+1, Node_Ptr, BranchList, CFGNode_Dst, CFG_Nodes, Path, CFG, TurnNo, Dst_Index, Src^1, Dst^1, 0)

                                # Concat paths
                                Path_Concat = Path_Src[0]
                                if Path_Dst[-1] != None:
                                    #
                                    if TurnNo == 0:
                                        Path_Concat = Path_Dst[-1]+Path_Src[0]
                                    else:
                                        Path_Concat = Path_Src[0]+Path_Dst[-1]

                                BackPath = Path_Concat

                                return No_Path, CFG, BackPath


                        # While-loop control
                        if CFGNode_Dst.ReadNumPaths() == 0:
                            # No-path then go to next node
                            While_Continue = True
                            Step_Count += 1
                        elif Step_Count< CFG_Nodes[CycleNo].ReadNumNodes():
                            # Check reaching terminal
                            While_Continue = True
                        else:
                            While_Continue = False



                        # Pre-Check Dst-Index
                        Find_Index_Match = False
                        for Path_Dst_No in range(CFGNode_Dst.ReadNumPaths()):
                            Path_Dst = CFGNode_Dst.ReadStLdPath(Path_Dst_No)
                            # Get set of indices
                            Indices_Dst = Path_Dst[2]

                            # Get set of destination indices
                            Dst_Indices = Indices_Dst[Dst][0]

                            for Dst_Index in Dst_Indices:
                                if Dst_Index == Src_Index:
                                    Find_Index_Match = True
                        if not Find_Index_Match and (Node_Ptr+1) < CFG_Nodes[CycleNo].nums:
                            Dst = Dst^1
                            Src = Src^1


                        # Search body
                        Find = False
                        if not Break_Point and (Node_Ptr+1) < CFG_Nodes[CycleNo].nums:
                            for Path_Dst_No in range(CFGNode_Dst.ReadNumPaths()):

                                # Get one path
                                Path_Dst = CFGNode_Dst.ReadStLdPath(Path_Dst_No)

                                # Get set of indices
                                Indices_Dst = Path_Dst[2]

                                # Get set of destination indices
                                Dst_Indices = Indices_Dst[Dst][0]

                                Find = False

                                for Dst_Index in Dst_Indices:
                                    if Dst_Index != -1 and Dst_Index == Src_Index and Block_Multiple_Dst != Dst_Index:

                                        # Mark destination index for blocking multiple time enterings
                                        Block_Multiple_Dst = Dst_Index

                                        if ((Tmp_Node_Ptr-Node_Ptr+2) < CFG_Nodes[CycleNo].ReadNumNodes()):

                                            # Count how many nodes are explored
                                            Tmp_Node_Ptr += 1

                                            # Mark this neighbor node is explored
                                            CFGNode_Src.SetNeigboorNode(CFGNode_Dst.ReadNodeID())

                                            if not CFGNode_Src.ReadNodeID() in CFG[-1]:
                                                CFG[-1] = CFG[-1]+[CFGNode_Src.ReadNodeID()]

                                            # Go to destination node
                                            No_Path, CFG_Dst, Path_Dst = PathPicker(CycleNo, Tmp_Node_Ptr, BranchList, CFGNode_Dst, CFG_Nodes, Path, CFG, TurnNo, Dst_Index, Dst, Src, Step_Count+1)

                                            # Concat paths
                                            Path_Concat = Path_Src[0]
                                            if Path_Dst[-1] != None and ((Path_No > -1) or (Path_No != False)):
                                                if CFGNode_Dst.ReadNeighborExplored() or ( CFGNode_Dst.ReadNodeID() == Branch_Node_ID ):
                                                    if TurnNo == 1:
                                                        Path_Concat = Path_Dst[-1]+Path_Src[0]
                                                    else:
                                                        Path_Concat = Path_Src[0]+Path_Dst[-1]
                                                else:
                                                    if TurnNo == 0:
                                                        Path_Concat = Path_Dst[-1]+Path_Src[0]
                                                    else:
                                                        Path_Concat = Path_Src[0]+Path_Dst[-1]

                                            BackPath = Path_Concat


                                        Find = True

                        if not Break_Point and not Find:
                            if (Tmp_Node_Ptr-Node_Ptr+2) < CFG_Nodes[CycleNo].ReadNumNodes() and Step_Count < CFG_Nodes[CycleNo].ReadNumNodes():
                                # Explore next destination node
                                While_Continue = True
                                Tmp_Node_Ptr += 1
                            else:
                                While_Continue = False
                        elif not ((Tmp_Node_Ptr-Node_Ptr+2) < CFG_Nodes[CycleNo].ReadNumNodes() and Step_Count < CFG_Nodes[CycleNo].ReadNumNodes()):
                            While_Continue = False
                        else:
                            Tmp_Node_Ptr += 1


                    if len(BackPath) > 0 and  chk_vld and not explored:
                        # Update path record
                        Path[-1] = BackPath
                        BackPath = []

            else:
                # Repaire source index
                Src_Index = Repair_Src_Index


    if CFGNode_Src.ReadNumPaths() == 0:
        return No_Path, [], []
    elif (Branch_Cycle_No > -1) and (Node_Ptr+1 == CFG_Nodes[CycleNo].ReadNumNodes()) and (Step_Count == CFG_Nodes[CycleNo].ReadNumNodes()) and not Find:
        if TurnNo == 0:
            Path[-1] = Path[-1]+Path_Src[0]
        else:
            Path[-1] = Path_Src[0]+Path[-1]

        CFG[-1] = CFG[-1] + [CFGNode_Src.ReadNodeID()]

        return No_Path, CFG, Path
    else:
        if not CFGNode_Src.ReadNodeID() in CFG[-1]:
            CFG[-1] = CFG[-1] + [CFGNode_Src.ReadNodeID()]

        return No_Path, CFG, Path


def CommonFetch(CyclicCFG, CFG):
    """
    Read Common CFG Node-ID between Cyclic Control-Flows
    """

    prog_cfg = []
    for index, cfg in enumerate(CFG):
        one_cfg = []
        for no, node in enumerate(cfg):
            if no == 0:
                one_cfg = [node]
            for c_node in CyclicCFG[index]:
                if c_node == node:
                    one_cfg.append(node)

        prog_cfg.append(one_cfg)

    return prog_cfg


def BackTrack(CFG_Nodes):

    CycleNo = 0
    Node_Ptr = 0
    CFGNodes = CFG_Nodes[0]
    Path = []
    CFG = []

    # Compose a List for Bnranch CFG Node-ID
    BranchList = BranchNodeTracker(CFG_Nodes)

    # Fetch Initial Source Node
    CFGNode_Src = CFGNodes.ReadInitNode()

    # Pick Data-Flow Node-IDs with:
    #   - Cyclic Control Flow
    #   - Branch CFG Node-ID
    #   - Path Information for each Basic Block in Cyclic Control-Flow
    print("Read Remained Node: {}".format(CFGNode_Src.ReadNodeID()))
    _, CFG, Path = PathPicker(CycleNo, Node_Ptr, BranchList, CFGNode_Src, CFG_Nodes, Path, CFG, 0, "-1", 0, 1, 0)

    if len(Path) > 0:
        return CFG, Path
    else:
        return CFG, []


def GetBBlock( prog, bblock_no ):

    nemonic = []

    for func in prog.funcs:
        for bblock in func.bblocks:

            bb_name = bblock.name
            if bblock_no in bb_name and int(bblock_no) == int(bb_name.replace('\n', '')):
                for instr in bblock.instrs:

                    nemonic.append(instr.nemonic)

    return nemonic


def Rotate( prog, cfg_node_id ):
    """
    Rotation of List by Basic Block's ID
    The Item having the ID is located to First by Rotation
    This is assumed by Cyclic Control Flow
    """

    if cfg_node_id in prog:
        index = prog.index( cfg_node_id )
        if index > 0:
            if index == 1:
                prog = prog[1:]+[prog[0]]
            else:
                prog = prog[index:]+prog[0:index]

        return prog, index

    return prog, 0


def ReadNodeList( tag, cfg_node_id, node_lists ):

    if cfg_node_id in tag:
        index = tag.index( cfg_node_id )
        return node_lists[index]
    else:
        return -1


def DFG_Extract( node_lists, dfg ):
    """
    Data-Flow Graph Extraction
    """

    prog_dfg = []
    is_Branch = False
    if isinstance(node_lists, list):
        for index, dfg_node_id in enumerate(dfg):
            chk_node = node_lists[int(dfg_node_id)]
            # Append "Nemonic" (NOT DFG-Node ID)
            prog_dfg.append( chk_node )
            if index == 0 and "br" in node_lists[0][1]:
                is_Branch = True

        return prog_dfg[0:len(prog_dfg)-1], is_Branch
    else:
        return -1, is_Branch


def CreateNodeList( r_file_path, bblock_id ):

    file_name = "@main()_bblock_"+str( bblock_id )+"_node_list.txt"
    with open( r_file_path+file_name, "r") as file:

        node_list = []
        for line in file:
            line = line.replace('\n','')
            lines = line.split(' ')
            entry = []
            for item in lines:
                entry.append(item)
            node_list.append(entry)

        return node_list


def CreateNodeLists( r_file_path, Programs ):

    node_lists = []
    tag = []
    for _ in range(len(Programs)-1):
        node_lists.append("")

    for no, cfg_node_id in enumerate(Programs[1:]):
        node_lists[no] = CreateNodeList( r_file_path=r_file_path, bblock_id=cfg_node_id )

    return node_lists


def NMCompose(cfg_node_id, prog_dfg, NM_List):

    list_no = 0
    for list_no, nm_list in enumerate(NM_List):
        cfg_id = nm_list[0]
        if cfg_id == cfg_node_id:
            break

    nm_list = []
    for dfg_node in prog_dfg:
        node_id = dfg_node[0]
        for nm_node in NM_List[list_no][1:]:
            for node in nm_node:
                if int(node_id) == int(node[0].replace(" ", ' ')):
                    nm_list.append(node[1])


    nm_list = sorted(nm_list, key=ExtractNumber, reverse=True)

    return nm_list


def DFG_Compose( r_file_path, r_file_path2, r_file_name, no, no_index, cfg_node_id, Programs, StLd_Paths, NM_List ):
    """
    Data-Flow Graph Composer
    """

    # Set cfg_node_id to first entry
    tmp_no = no
    if no == no_index:
        prog, index = Rotate( Programs[no][1:], cfg_node_id )
    else:
        prog, index = Rotate( Programs[no][1:], cfg_node_id )
        no = no_index

    # Create Node List for the Cyclic Control-Flow
    bb_node_lists = CreateNodeLists( r_file_path2, Programs[tmp_no] )

    # Create Program (LLVM-IR)
    program = ReadProgram( r_file_path=r_file_path, r_file_name=r_file_name)

    # Composition Body
    ld_paths = []
    Branch = True
    for set_no, ld_ld_path in enumerate(StLd_Paths[tmp_no][index]):                                   ####
        path_dfg = []
        is_Branch = False

        # Load-Load Path has Register Index at Last in the List
        dfg_node_id = ld_ld_path[-1]

        # Read Node from Node List
        #   DFG's Node-ID corresponds to Entry number of Node-List
        src_index = bb_node_lists[index][int(dfg_node_id)][1]

        # Read Register Index Number from Basic Block
        reg_index = Programs[no][0]

        if reg_index == int( src_index[1:] ):

            # Read Nemonic
            bb_nemonics = GetBBlock(prog=program, bblock_no=cfg_node_id)
            bb_nemonics.reverse( )

            # Data-Flow Node Extraction
            prog_dfg, is_Branch = DFG_Extract( node_lists=bb_node_lists[index], dfg=StLd_Paths[tmp_no][index][set_no] )

            if is_Branch:
                path_dfg.append( bb_nemonics )
            else:
                # This Statement does not include Branch IR-Instruction
                nemonics =NMCompose(cfg_node_id, prog_dfg, NM_List[tmp_no])
                path_dfg.append( nemonics )
                Branch = False

        if len(path_dfg) > 0:
            ld_paths.append( path_dfg )

    if Branch:
        if len(ld_paths) > 0:
            return ld_paths
        else:
            # Enter Next Cyclic Control-Flow
            # Read This Basic Block's Nemonics
            bb_nemonics = GetBBlock(prog=program, bblock_no=cfg_node_id)
            bb_nemonics.reverse( )

            # Sort by CFG-ID
            #   Entry of the ID is at First Entry by Rotation (Cyclic Control-Flow)
            prog, index = Rotate( Programs[no-1][1:], cfg_node_id )

            # Extract Next CFG-ID (Neighbor in Cyclic Control-FLow)
            back_cfg_node_id = Programs[no-1][index+2]

            # Set Label for This Currect CFG-ID
            label = [back_cfg_node_id+":                                               ; preds =%"+cfg_node_id]

            # Set Nemonic
            rtn_list =[]
            rtn_list_ = [bb_nemonics[0]]
            rtn_list.append(rtn_list_)

            return rtn_list

    else:
        return ld_paths+[[bb_nemonics[0]]]


def CreateEntry( program ):

    alloc_list = []
    for func in program.funcs:
        for bblock in func.bblocks:
            if "entry" in bblock.name:
                for instr in bblock.instrs:
                    if "alloc" in instr.opcode:
                        alloc_list.append([instr.dst, instr.nemonic.replace("\n", '')])

                for instr in bblock.instrs:
                    if "store" in instr.nemonic and "%" in instr.nemonic:
                        start_index = instr.nemonic.find("%")
                        reg_index = instr.nemonic[start_index:]
                        end_index = reg_index.find(" ")
                        reg_index = reg_index[0:end_index]

                        for alloc_no, item in enumerate(alloc_list):
                            chk_reg_index = item[0]
                            if chk_reg_index == reg_index:
                                alloc_list[alloc_no] = alloc_list[alloc_no] + [instr.nemonic.replace("\n", '')]

    return alloc_list


def AppendEntry( reg_index, alloc_list ):

    for item in alloc_list:
        reg_no = int(item[0][1:])
        if reg_no == reg_index:
            return item[1:]


def AddrGen( r_file_path, r_file_path2, r_file_path3, r_file_name, Programs, StLd_Paths, LdLdPaths, NM_List ):

    program = ReadProgram( r_file_path=r_file_path, r_file_name=r_file_name )
    alloc_list = CreateEntry( program )

    target_bblock_lists = []
    for index, prog in enumerate(Programs):
        cfg_list = prog[1:]
        target_bblock_list = [cfg_list[-1]]+cfg_list[0:len(cfg_list)-1]
        target_bblock_lists.append( target_bblock_list )

    LLVM_IR = []
    for no, prog in enumerate(Programs):

        llvm_ir = []

        reg_index = prog[0]
        #print( "Index-{}".format( reg_index ) )
        llvm_ir.append( "Index-"+str(reg_index) )
        entry = AppendEntry( reg_index, alloc_list )
        if len(entry) > 0:
            #print( "{}:".format("entry"))
            llvm_ir.append( "entry:" )
            if isinstance(entry, list):
                for item in entry:
                    print(item)
                    llvm_ir.append( item )
            else:
                print(entry)
                llvm_ir.append( entry )

        entry_br = "  br label %"+prog[1]+"\n"
        #print( "{}".format( entry_br ))
        llvm_ir.append( entry_br )

        target_bblock_list = target_bblock_lists[no]
        for index, cfg_node_id in enumerate(prog[1:]):

            # Append Label
            #print( "{}:".format( str( cfg_node_id ) ), end="" )
            llvm_ir.append( str( cfg_node_id )+":" )

            # Add Predicate Info
            predict_labels = " "
            if len( target_bblock_list ) > 1:
                predict_labels = "%"+target_bblock_list[index]+", "
            if len( target_bblock_list ) > 0:
                predict_labels = "%"+target_bblock_list[index]

            if predict_labels != " ":
                predict_labels = "                                               ; preds ="+predict_labels

            #print("{}".format( predict_labels ))
            llvm_ir[-1] = llvm_ir[-1]+predict_labels

            # Get Ld-Ld DFG-Path
            Transit = False
            paths_dfg = DFG_Compose( r_file_path, r_file_path2, r_file_name,  no=no, no_index=no, cfg_node_id=cfg_node_id, Programs=Programs, StLd_Paths=StLd_Paths, NM_List=NM_List )

            Check_LoopBody = LdLdPaths[no][index][0]

            paths_dfg_ = []
            if not Check_LoopBody and isinstance(paths_dfg, list):
                for path_no, paths in enumerate(paths_dfg):
                    if isinstance(paths, list):
                        if len(paths[0]) > 1:
                            if not isinstance(paths[0], str):
                                if path_no == 0:
                                    paths_dfg_= paths_dfg_+SortList(paths)
                                else:
                                    paths_dfg_= SortList(paths)+paths_dfg_

                            elif len(paths) == 1 and len(paths_dfg) == 2 and isinstance(paths[0], str) and not "br" in paths[0]:
                                llvm_ir.append( paths[0].replace("\n", '') )
                            elif len(paths) == 1:
                                paths_dfg_= paths_dfg_+paths
                            else:
                                paths_dfg_= paths_dfg_+SortList(paths)
                        else:
                            test = paths[0]
                            if len(test)> 0 and "preds" in test[0]:
                                tmp_label =  paths[0]
                                Transit = True
                                grap = SortList(paths)
                                sorting =  grap

                                paths_dfg_ = paths_dfg_+[" "]+sorting[0:len(sorting)-1]
                            else:
                                paths_dfg_= paths_dfg_+SortList(paths)
                    else:
                        paths_dfg_ = paths_dfg_+[paths]

            else:
                paths_dfg_ = paths_dfg[-1]

            BR_EXIST = False


            if isinstance(paths_dfg_, list):
                for nmemonic in paths_dfg_:
                    if isinstance(nmemonic, list):
                        if Transit:
                            Transit = False
                            for nm in nmemonic:
                                if not "br" in nm:
                                    #print(nm.replace("\n", ''))
                                    llvm_ir.append(nm.replace("\n", ''))
                                elif not BR_EXIST:
                                    tmp_nmemonic = nmemonic
                                    BR_EXIST = True
                        elif isinstance( nmemonic[0], str ):
                            if not "br" in nmemonic[0]:
                                    #print(nmemonic[0].replace("\n", ''))
                                    llvm_ir.append( nmemonic[0].replace("\n", ''))
                        else:
                            for nm in nmemonic[0]:
                                if not "br" in nm:
                                    #print(nm.replace("\n", ''))
                                    llvm_ir.append( nm.replace("\n", ''))
                                elif not BR_EXIST:
                                    tmp_nmemonic = nmemonic
                                    BR_EXIST = True
                    elif not "br" in nmemonic:
                        #print(nmemonic.replace("\n", ''))
                        llvm_ir.append(nmemonic.replace("\n", ''))
                    elif not "br" in nmemonic and not BR_EXIST:
                        #print(nmemonic.replace("\n", ''))
                        llvm_ir.append(nmemonic.replace("\n", ''))
                        tmp_nmemonic = ""
                        BR_EXIST = False
                    else:
                        print(nmemonic.replace("\n", ''))
                        llvm_ir.append(nmemonic.replace("\n", ''))
                        tmp_nmemonic = ""
                        BR_EXIST = True

            if BR_EXIST and len(tmp_nmemonic) > 0:
                #print(tmp_nmemonic.replace("\n", ''))
                llvm_ir.append(tmp_nmemonic.replace("\n", ''))
            elif"br" in tmp_nmemonic:
                #print(tmp_nmemonic.replace("\n", ''))
                llvm_ir.append(tmp_nmemonic.replace("\n", ''))

            llvm_ir.append(" ")

        LLVM_IR.append(llvm_ir)

    return LLVM_IR


def ReadLdLdPath( r_file_path, post_fix, Programs ):
    """
    Read Load-Load Path
    """

    ld_ld_paths = []
    for prog in Programs:
        cfg_ld_paths = []
        for cfg_node_id in prog[1:]:
            r_file_name = "@main()_bblock_"+str( cfg_node_id )+"_bpath_"+post_fix+".txt"
            with open( r_file_path+r_file_name, "r" ) as file:
                for line in file:
                    paths = line.split( "][" )
                    ld_ld_path = []
                    for path in paths:
                        path = path.replace('[', '')
                        path = path.replace(']', '')
                        ld_ld_path.append( path.split( ", ") )

            cfg_ld_paths.append( ld_ld_path )

        ld_ld_paths.append( cfg_ld_paths )

    return ld_ld_paths


def Reorder(CFG_Nodes):
    """
    Make Inverse Order
    """

    CFGNodes = []
    for index in range(len(CFG_Nodes)-1, -1, -1):
        CFG_Nodes[index].Reorder(index&1)
        CFGNodes.append(CFG_Nodes[index])

    return CFGNodes


def CodeWrite(w_file_path, w_post_fix, llvm_ir):
    for llvm_ir_ in llvm_ir:
        for line_no, line in enumerate(llvm_ir_):
            if "Index-" in line:
                reg_index = line[6:]
                file_name = w_post_fix+"_reg_"+reg_index+".txt"
                openfile = w_file_path+file_name
                with open(openfile, "w") as ir_file:
                    for nemonic in llvm_ir_[line_no+1:]:
                        if "Index-" in nemonic:
                            break
                        ir_file.writelines(nemonic+"\n")


def LdLdPathChecker( Programs, LdLdPaths ):

    LdLdPaths_ = []
    for Cycle_ID, ldldpaths in enumerate(LdLdPaths):
        ldld_paths = []
        for CFG_ID, CFG_PATH in enumerate(ldldpaths):
            if len(CFG_PATH) > 2:
                ldld_paths.append([True])
            else:
                ldld_paths.append([False])

        LdLdPaths_.append(ldld_paths)

    return LdLdPaths_


def DuplicatedDFGNodeRemover( LLVM_IR ):

    LLVM_IR_ = []
    for Cycle_No, CycleBBlocks in enumerate(LLVM_IR):
        Cycle_LLVM_IR = []
        for bb_no, BBlock in enumerate(CycleBBlocks):

            Duplicate = False
            for chk_bb_no in range(bb_no+1, len(CycleBBlocks), +1):
                Chk_BBlock = CycleBBlocks[chk_bb_no]
                if Chk_BBlock == BBlock and not " " == Chk_BBlock and not "br" in Chk_BBlock:
                    Duplicate = True
                    break

            if not Duplicate:
                Cycle_LLVM_IR.append(BBlock)

        LLVM_IR_.append(Cycle_LLVM_IR)


    return LLVM_IR_


def AddrGen1(name, r_file_path, r_file_path1, r_file_path2, ):

    # Compiled Program Name
    name='mvm'

    # Reading File Path

    # Read Loop Paths in Control-Flow Graph
    r_file_name = name+"_cfg_loop.txt"
    cfg_paths = ReadFile(file_path=r_file_path1, file_name=r_file_name)
    CyclicPaths = Parser( cfg_paths, 'cfg' )

    # Read Data-Flow Graphs and their Node Lists
    # Compose CFG_Nodes Object
    r_file_name = "@main()_bblock"
    CFG_Nodes, NM_List = Preprocess( r_file_path2, r_file_path, r_file_name, CyclicPaths )

    # Reordering (Inverse Order)
    CFGNodes = []
    NMList = []
    for index in range(len(CFG_Nodes)-1, -1, -1):
        CFG_Nodes[index].Reorder(0)
        CFGNodes.append(CFG_Nodes[index])

    for index in range(len(NM_List)-1, -1, -1):
        NM_List[index] = NM_List[index][1:] +[ NM_List[index][0]]
        NMList.append(NM_List[index])

    NM_List = NMList

    # Tracking
    CFG, Path = BackTrack(CFGNodes)

    # Read LLVM-IR Code
    Programs = CFG

    # Writing File Path
    w_file_path = "../temp/backtracker/"

    # Writing File Common Name Part
    w_file_name = name

    with open(w_file_path+w_file_name+"_addr_gen_dfg.txt", "w") as addr_gen_dfg_list:
        addr_gen_dfg_list.writelines(map(str, Path))

    with open(w_file_path+w_file_name+"_addr_gen_cfg.txt", "w") as addr_gen_cfg_list:
        addr_gen_cfg_list.writelines(map(str, Programs))


def AddrGen2(r_file_path, r_file_name, w_file_path, Programs):

    # Read Load-Load Paths
    post_fix = "st_ld"
    StLdPaths = ReadLdLdPath( r_file_path, post_fix, Programs )

    # Read Load-Load Paths
    post_fix = "ld_source_ld"
    LdLdPaths = ReadLdLdPath( r_file_path, post_fix, Programs )
    LdLdPaths = LdLdPathChecker( Programs, LdLdPaths )

    r_file_path = "../temp/llvmcdfggen/"
    r_file_path2 = "../temp/cdfgamgen/"
    r_file_path3 = "../temp/ampathgen/"

    # Generate LLVM-IR Code
    LLVM_IR = AddrGen(r_file_path=r_file_path, r_file_path2=r_file_path2, r_file_path3=r_file_path3, r_file_name=name, Programs=Programs, StLd_Paths=StLdPaths, LdLdPaths=LdLdPaths, NM_List=NM_List )

    LLVM_IR = DuplicatedDFGNodeRemover( LLVM_IR )

    # Output to File
    openfile = w_file_path + name+"_ir.txt"
    with open(openfile, "w") as ir_file:
        for cfg in LLVM_IR:
            for nmemonic in cfg:
                ir_file.writelines(str(nmemonic)+"\n")

    w_post_fix = name
    llvm_ir = LLVM_IR
    CodeWrite(w_file_path, w_post_fix, llvm_ir)


def CodeMerger( NM_List, Node_Lists, MaskLdLdPaths, LdLdPaths, LLVM_IR ):

    reg_index_list = []
    for llvm_ir in LLVM_IR:
        if "Index-" in llvm_ir[0]:
            reg_index_list.append(llvm_ir[0][6:])

    LLVM_IR_ = []
    for reg_no, reg_index in enumerate(reg_index_list):
        for cycle_no, LdLdPaths_ in enumerate(LdLdPaths):
            for no, LdLdPath in enumerate(LdLdPaths_):
                if MaskLdLdPaths[cycle_no][no][0]:
                    for path_no, ldldpath in enumerate(LdLdPath):

                        no_index = ldldpath[-1]
                        nodes = NM_List[cycle_no][no-1][1:][0]
                        cfg_node_id = NM_List[cycle_no][no-1][0]
                        offset = int(nodes[-1][0]) + len(nodes)
                        for node_no in range(len(nodes)-1,-1,-1):
                            node = nodes[node_no]
                            list_no = offset-int(node[0].replace(" ", ''))
                            if int(no_index) == list_no:
                                llvm_ir_ = []
                                for nemonic in LLVM_IR[reg_no]:
                                    llvm_ir_.append(nemonic)

                                header = cfg_node_id+":                                               ; preds ="
                                llvm_ir_.append(header)
                                for index in range(len(LdLdPath[path_no])-1, -1, -1):
                                    node_index = LdLdPath[path_no][index]
                                    for node_no_ in range(len(nodes)-1,-1,-1):
                                        node_ = nodes[node_no_]
                                        list_no_ = offset-int(node_[0].replace(" ", ''))
                                        if int(node_index) == list_no_:
                                            nemonic = NM_List[cycle_no][no-1][1][list_no_-1]
                                            llvm_ir_.append(nemonic[1])
                                            break

                                LLVM_IR_.append(llvm_ir_)
                                break

    return LLVM_IR_


def ExtractBBs(file_path, file_name):

    basic_blocks = []
    current_label = None
    branch_instruction = None

    basic_blocks = []

    instrs = []
    bblocks = []

    with open(file_path+file_name, 'r') as file:
        instrs = []
        bblocks = []
        count = 0
        for index, line in enumerate(file):

            if not line.isspace():
                count += 1

                instrs.append(line)

                # Check for a label
                if ('%' not in line or ('%' in line and 'preds' in line )) and ':' in line:
                    line = line.split()
                    current_label = line[0].strip().replace(':', '')
                    branch_instruction = None

                # Check for a branch instruction
                elif 'br' in line:
                    branch_instruction = line.strip()
                    bblocks.append(instrs)

                # Save the previous basic block
                if current_label is not None and branch_instruction is not None:
                    basic_blocks.append([current_label, branch_instruction, count])
                    current_label = None
                    branch_instruction = None
                    instrs = []
                    count = 0

    return bblocks, basic_blocks


def ReadLabel(branch_instr):

    tokens = branch_instr.split(' ')
    labels = []
    for token in tokens:
        if '%' in token:
            token = token.replace(' ', '').replace(',', '').replace('%', '')
            labels.append(token)

    return labels


def GetLabelInfo(basic_blocks):

    label_info = []

    for basic_block in enumerate(basic_blocks):
        #print(f"basic_block:{basic_block}")
        label = basic_block[1][0]
        branch_instr = basic_block[1][1]

        labels = ReadLabel(branch_instr)
        #print(f"labels:{labels}")
        label_info.append([label, labels])

    return label_info


def CFGNodeMerger(r_file_path, r_file_name):

    bblocks, basic_blocks = ExtractBBs(r_file_path, r_file_name)

    label_info = GetLabelInfo(basic_blocks)
    #print(f"label_info:{label_info}")

    hit_count = 0
    for bb_index, basic_block in enumerate(basic_blocks):
        #print(f"basic_block:{basic_block}")
        num_instrs = basic_block[2]
        find = False
        if num_instrs == 2 and len(label_info[bb_index][1]) < 2:
            find = True
            bb_label = label_info[bb_index][0]
            print(f"br only basic block label:{bb_label} bblock-no:{bb_index}")

            for bb_chk_index, bblock in enumerate(bblocks):
                label = label_info[bb_chk_index][0]
                if label == bb_label:
                    target_labels = label_info[bb_chk_index][1]
                    label_t = None
                    label_f = None
                    if len(target_labels)>2:
                        label_t = target_labels[1]
                        label_f = target_labels[2]
                    elif len(target_labels)>1:
                        label_t = target_labels[0]
                        label_f = target_labels[1]
                    elif len(target_labels)>0:
                        label_t = target_labels[0]

                    print(f"target_labels:{target_labels} at bblock-no:{bb_chk_index} label_t:{label_t} label_f:{label_f}")

                    if label_t is not None:
                        t_index_t = 0
                        t_label = ""
                        for index, chk_label in enumerate(label_info):
                            if label_t in chk_label[0]:
                                t_label = chk_label[1]
                                t_index_t = index
                                #print(f"t_index_t:{t_index_t}")
                                break

                        index_t = 0
                        pred_label = ""
                        for index, chk_label in enumerate(label_info):
                            if bb_label in chk_label[1]:
                                pred_label = chk_label[0]
                                if pred_label != 'entry':
                                    pred_label = '%'+pred_label
                                index_t = index
                                #print(f"index_t:{index_t} pred_label:{pred_label}")
                                break

                        bblocks[t_index_t][0] = bblocks[t_index_t][0].replace('%', '').replace(bb_label, " "+pred_label)
                        #print(f"bblocks[t_index_t][0]:{bblocks[t_index_t][0]}")

                        target_label = '%'+label_t
                        label = '%'+bb_label
                        print(f"replace label:{label} with target_label:{target_label} at bblock-no:{index}")
                        for index, labels in enumerate(label_info):
                            chk_label = labels[1]
                            if bb_label in chk_label:
                                #print(f"bblock:{bblocks[index]}")
                                bblocks[index][-1] = bblocks[index][-1].replace(label, target_label)
                                bblock[bb_chk_index:] = bblock[bb_chk_index+1:]
                                bblock[bb_chk_index-1-hit_count:] = bblock[bb_chk_index+1-hit_count:]
                                hit_count += 2

                    if label_f is not None:
                        f_index_t = 0
                        f_label = ""
                        for index, chk_label in enumerate(label_info):
                            if label_t in chk_label[0]:
                                f_label = chk_label[1]
                                f_index_t = index
                                #print(f"f_index_t:{f_index_t}")
                                break

                        index_t = 0
                        pred_label = ""
                        for index, chk_label in enumerate(label_info):
                            if bb_label in chk_label[1]:
                                pred_label = chk_label[0]
                                if pred_label != 'entry':
                                    pred_label = '%'+pred_label
                                index_t = index
                                #print(f"index_t:{index_t} pred_label:{pred_label}")
                                break

                        bblocks[f_index_t][0] = bblocks[f_index_t][0].replace('%', '').replace(bb_label, " "+pred_label)
                        #print(f"bblocks[f_index_t][0]:{bblocks[f_index_t][0]}")

                        target_label = '%'+label_f
                        label = '%'+bb_label
                        print(f"replace label:{label} with target_label:{target_label} at bblock-no:{index}")
                        for index, labels in enumerate(label_info):
                            chk_label = labels[1]
                            if bb_label in chk_label:
                                #print(f"bblock:{bblocks[index]}")
                                bblocks[index][-1] = bblocks[index][-1].replace(label, target_label)
                                bblock[bb_chk_index:] = bblock[bb_chk_index+1:]
                                bblock[bb_chk_index-1-hit_count:] = bblock[bb_chk_index+1-hit_count:]
                                hit_count += 2

                    print("\n")
        if not find:
            bblocks[bb_index].append('\n')

    return bblocks

def cfg_nodemerger(r_file_path, r_file_name, w_file_path):
    w_file_name = r_file_name

    bblocks = CFGNodeMerger(r_file_path, r_file_name)
    with open(w_file_path+w_file_name, 'w') as file:
        for bblock in bblocks:
            for instr in bblock:
                file.write(instr)

