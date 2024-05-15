
if Gen_DFG:
    Main_Gen_LLVMtoDFG( r_file_path, r_file_name, dir_dot )

if Gen_CFG:
    Main_Gen_LLVMtoCFG( r_file_path, r_file_name, dir_dot )

if Gen_AM:
    DST_APPEND = True
    ZERO_REMOVE = True
    Main_Gen_CDFGtoAM( r_file_path, r_file_name, w_file_path, ZERO_REMOVE, DST_APPEND )

if Gen_Path:
    Main_Gen_AMtoPath( r_file_path, r_file_name, w_file_path )
    
