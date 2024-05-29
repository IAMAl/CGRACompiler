import utils.AMComposer
import utils.AMReader

def Preprocess( r_file_path="./", r_file_name="mvm_am" ):

    file_name = r_file_name+"_am_inv.txt"
    f = ReadAM( file_path=r_file_path, file_name=file_name )
    am_size, am = QuickAMComposer( f )

    return am_size, am


class Node:
    def __init__(self, am, am_size, index):
        self.NodeID = index
        self.am_size = am_size

        self.Detect = False

        dest_ids = []
        row = am[index]
        for clm_no, elm in enumerate(row):
            if elm == 1:
                dest_ids.append(clm_no)
        #print("init: Node-{} set destination nodes: {}".format(index, dest_ids))

        self.DestIDs = dest_ids

        self.Term = False

    def Set_MyNodeID(self, id):
        """
        Set CFG Node-ID
        """
        self.NodeID = id

    def Set_DestNodeID(self, row_am):
        """
        Set Destination CFG Node-ID
        """
        for index, elm in row_am:
            self.DestIDs.append(index)

    def Read_DestIDs(self):
        """
        Read CFG Node-ID of Destination
        """
        dest_ids = []
        for id in self.DestIDs:
            dest_ids.append(id)
        return dest_ids

    def Set_Term(self):
        """
        Set Terminal Flag
        """
        self.Term = True

    def Read_Term(self):
        """
        Read Terminal Flag
        """
        if self.Term:
            print("Node-{} is ended".format(self.NodeID))
        return self.Term

    def Set_Detect(self):
        """
        Set Detection Flag
        """
        self.Detect = True

    def Read_Detect(self):
        """
        Read Detection Flag
        """
        return self.Detect


def GetShape( lst ):
    """
    Get Shape of List
    """
    shape = []
    if isinstance(lst, list):
        shape.append(len(lst))
    if lst:
        shape.extend(GetShape(lst[0]))

    return shape


def AppendLowestList( my_id, lst ):
    """
    Append Item to Most-Inner Level in List
    """
    check = False
    temp = []
    if isinstance(lst, list):
        for lst_ in lst:
            #print("test:{}".format(lst_))
            rtn_lst, check = AppendLowestList(my_id, lst_)

            if not check:
                temp.append(lst_)

        if check:
            return lst.append(my_id), False
        else:
            return temp, False
    else:
        return lst, True


def RemoveList( lst ):
    """
    Remove List
    """
    #print("Try to remove: {}".format(lst))
    if isinstance(lst, list):
        temp = []
        for lst_ in lst:
            if isinstance(lst_, list):
                if len(lst_) == 0:
                    return []

                lst_ = RemoveList(lst_)

            temp.append(lst_)

        return temp
    return lst


class EdgeTab:
    def __init__(self, am_size):
        self.am_size = am_size

        brank1 = []
        for _ in range(am_size):
            brank1.append([])
        brank2 = []
        for _ in range(am_size):
            brank2.append([])

        edges = []
        edges.append(brank1)
        edges.append(brank2)
        self.Edges = edges

    def Read(self, read_no, my_id):
        """
        Read Edges
        """
        edges = self.Edges[read_no][my_id]
        self.Edges[read_no][my_id] = []
        return edges

    def Write(self, write_no, my_id, dest_ids, edges):
        """
        Write Edges
        """
        #print("  >Write ID-{} in {}".format(my_id, edges))
        shape = GetShape(edges)
        if len(shape) == 1 and len(edges) == 0:
            for dest_id in dest_ids:
                self.Edges[write_no][dest_id].append([my_id])
                #print("  Dest Node-{}: {}".format(dest_id, self.Edges[write_no][dest_id]))
        elif len(shape) == 1 and len(edges) > 0:
            edges.append(my_id)
            for dest_id in dest_ids:
                self.Edges[write_no][dest_id].append(edges)
                #print("  Dest Node-{}: {}".format(dest_id, self.Edges[write_no][dest_id]))
        else:
            edges_, _ = AppendLowestList(my_id, edges)
            for dest_id in dest_ids:
                #print("  Dest Node-{}: {}".format(dest_id, edges_))
                self.Edges[write_no][dest_id].append(edges_)

    def Dump(self, my_id):
        """
        Dump List
        """
        for index, edges in enumerate(self.Edges):
            print("no-{} {}".format(index, edges))


def CheckEcho( node_id, edges ):
    if isinstance(edges, list):
        temp = []
        for edges_ in edges:
            #print("  Check Echo for Node-{}: {}".format(node_id, edges))
            edge, check = CheckEcho(node_id, edges_)
            if check:
                #print("  Echo is Detected for Node-{}: {}".format(node_id, edge))
                break
            elif isinstance(edge, list) and len(edge) > 0:
                temp.append(edge)
            elif isinstance(edge, int):
                temp.append(edge)

        return temp, False
    else:
        return edges, edges == node_id


def CheckCycle( cycles, node_id, edges, first, last_level, level ):
    """
    Sub-function for checking Cyclic-Loop
    """
    if isinstance(edges, list):
        #print("  Check Cyclic Loop for Node-{}: {} at Level-{}".format(node_id, edges, level))
        temp = []
        level += 1
        first = True
        for edges_ in edges:
            cycles, edge, check, first, last_level, level = CheckCycle(cycles, node_id, edges_, first, last_level, level)

            if check and first and len(edges) > 2:
                cycles.append(edges)
                #print("  Cyclic-Loop Detected on Nodes: {} in List: {} at Level-{}".format(node_id, edges, level))
                break
            elif isinstance(edge, list) and len(edge) > 0:
                temp.append(edge)
            elif isinstance(edge, int):
                temp.append(edge)
            else:
                temp.append(edge)

            if last_level:
                first = False
            else:
                first = True

        level -= 1

        return cycles, temp, False, first, False, level
    else:
        return cycles, edges, edges == node_id, first, True, level


def CheckEmpty( node_id, edges ):
    """
    Check List is Empty
    """
    if isinstance(edges, list):
        if len(edges) == 0:
            #print("  Empty Detected on Nodes: {}".format(node_id))
            return True
        else:
            return False
    else:
        True


def CycleDetector( am_size=0, am=[], nodes=[], edgetab=[] ):
    """
    Cyclic-Loop Detector
    """
    read_no = 1
    write_no = 0
    CyclicEdges = []
    for steps in range(am_size):
        #print("\nStep-{}".format(steps))
        #print("Read from Table-{}".format(read_no))
        for node_id in range(am_size):
            #edgetab.Dump(node_id)
            #print("  Enter Node-{}".format(node_id), end="")
            if not nodes[node_id].Read_Term() or steps == 0:

                edges = edgetab.Read(read_no, node_id)

                cycles, edges, check_index, _, last_level, level = CheckCycle([], node_id, edges, True, False, 0)
                if len(cycles) > 0 and not nodes[node_id].Read_Detect():
                    CyclicEdges.append(cycles[0])
                    nodes[node_id].Set_Detect()
                    #print("    CYCLE Detected: {}".format(cycles), end="")

                edges, check_index = CheckEcho(node_id, edges)

                edges = RemoveList(edges)

                if CheckEmpty(node_id, edges) and steps != 0:
                    print("  Node-{} Terminated: {}".format(node_id, edges))
                    nodes[node_id].Set_Term()

                dest_ids = nodes[node_id].Read_DestIDs()
                #print("  Send from Node-{} to Dest Nedes:{}".format(node_id, dest_ids), end="")
                edgetab.Write(write_no, node_id, dest_ids, edges)

            #print("\n")

        tmp_no = read_no
        read_no = write_no
        write_no = tmp_no

    return CyclicEdges


def RemoveCycles( CyclicEdges ):
    """
    Remove Duplicated (Same) Edge
    """
    CyclicEdges_ = []
    index = 0
    offset = 0
    length = len(CyclicEdges)
    if length > 1:
        while True:

            index += 1
            if (offset+index) == length:
                break

            cycle = CyclicEdges.pop(0)

            for idx in range(length-offset-index-1):
                check_cycle = CyclicEdges[idx-offset]

                if len(check_cycle) == len(cycle):
                    for count in range(len(cycle)):
                        #print("Check {} and {}".format(check_cycle, cycle))
                        if check_cycle == cycle:
                            CyclicEdges_.append(cycle)
                            CyclicEdges.pop(idx-offset)
                            offset += 1
                            #print("idx:{} offset:{} for {}".format(idx, offset, cycle))
                        else:
                            check_cycle = check_cycle[1:]+check_cycle[:1]

    return CyclicEdges_


def ReadNodeList( r_file_name ):
    """
    Read Node-List Generated by CDFGAMGen
    """
    r_node_list_file_name = r_file_name+"_node_list.txt"
    node_list = []
    with open(r_node_list_file_name, "r") as list:
        for line in list:
            line_ = []
            line = line.split(" ")
            for item in line:
                item = item.replace('\n', '')
                line_.append(item)

            node_list.append(line_)

    return  node_list


def TranslateNode( r_file_name, CyclicEdges ):
    node_list = ReadNodeList(r_file_name)

    CyclicEdges_ = []
    for cycle_path in CyclicEdges:
        path = []
        for node_no in cycle_path:
            for node in node_list:
                if node[0] in str(node_no):
                    #print("Checked: {}({}) == {}".format(node[0], node[1], node_no))
                    node_id = node[1]
                    path.append(node_id)
                    break

            #print(path)

        CyclicEdges_.append(path)

    return CyclicEdges_


def Main_CycleDetector( r_file_path, r_file_name, w_file_path, w_file_name ):

    am_size, am = Preprocess(r_file_path="./", r_file_name=r_file_name)

    #print(am)
    nodes = []
    for index in range(len(am)):
        nodes.append(Node(am, am_size, index))

    edgetab = EdgeTab(am_size)

    CyclicEdges = CycleDetector(am_size=am_size, am=am, nodes=nodes, edgetab=edgetab)
    CyclicEdges = RemoveCycles(CyclicEdges)

    CyclicEdges = TranslateNode(r_file_name=r_file_name, CyclicEdges=CyclicEdges)

    if len(CyclicEdges) > 0:
        print("Cycle: {} in Graph {}".format(CyclicEdges, r_file_name))
    else:
        print("No Cycles in Graph {}".format(r_file_name))

    openfile = w_file_path + w_file_name+"_loop.txt"
    with open(openfile, "w") as cfg_cycle_file:
        cfg_cycle_file.writelines(str(CyclicEdges))
