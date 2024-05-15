def Preprocess(r_file_path="./", r_file_name="mvm_am"):

    file_name = r_file_name+"_am_inv.txt"
    f = ReadAM( file_path=r_file_path, file_name=file_name )
    am_size, am = AMComposer( f )

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
        #else:
        #    print("Node-{} runs".format(self.NodeID))
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


def GetShape(lst):
    """
    Get Shape of List
    """
    shape = []
    if isinstance(lst, list):
        shape.append(len(lst))
    if lst:
    shape.extend(GetShape(lst[0]))

    return shape


def AppendLowestList(my_id, lst):
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


def RemoveList(lst):
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


def CheckEcho(node_id, edges):

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


def CheckCycle(cycles, node_id, edges, first, last_level, level):
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
        #if edges == node_id:
        #    print("  Cyclic-Loop Detected on Nodes: {} at Level-{}".format(node_id, edges, level))
        return cycles, edges, edges == node_id, first, True, level
    

def Main_CyckeDetector(cycles, node_id, edges, first, last_level, level):
    return CheckCycle(cycles, node_id, edges, first, last_level, level)
