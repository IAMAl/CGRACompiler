import Gen_LLVMtoCDFG
import Gen_CDFGtoAM
import Gen_AMtoPath
import Cycle_Detector
import CFG_NodeMerger
import Gen_AGUCode

Gen_DFG     = False
Gen_CFG     = False
Gen_AM      = False
GenBackPath = False
Gen_Path    = False
Remove_Cycle= False
Gen_CFGMerge= False
Gen_AGU     = False

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
    Main_CycleDetector( r_file_path, r_file_name, w_file_path, w_file_name )

if Gen_CFGMerge:
    Main_CFGNodeMerger( r_file_path, r_file_name, w_file_path )

if Gen_AGU:
    Main_Gen_AGUCode( r_file_path, r_file_name, w_file_path, w_file_name )