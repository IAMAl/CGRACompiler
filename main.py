
if Gen_DFG:
    Main_Gen_LLVMtoDFG( r_file_path, r_file_name, dir_dot )

if Gen_CFG:
    Main_Gen_LLVMtoCFG( r_file_path, r_file_name, dir_dot )

if Gen_AM:
    DST_APPEND = True
    ZERO_REMOVE = True
    Main_Gen_CDFGtoAM( r_file_path, r_file_name, w_file_path, ZERO_REMOVE, DST_APPEND )

if GenBackPath:
    PATH_FORMAT = True
    Gen_BackPath( PATH_FORMAT, r_file_path, r_file_name, w_file_path )

if Gen_Path:
    Main_Gen_AMtoPath( r_file_path, r_file_name, w_file_path )
    
if Remove_Cycle:
    Main_CyckeDetector( cycles, node_id, edges, first, last_level, level )
    
if Gen_CFGMerge:
    Main_CFGNodeMerger( r_file_path, r_file_name, w_file_path )