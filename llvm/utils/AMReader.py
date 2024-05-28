def ReadAM( file_path="./test/", file_name="am.txt" ):
    """
    File-Open used for AM file

    Arguments
        file_path:    path (directory) for source file
        file_name:    name of file for source file
    """
    f = open( file_path + file_name )
    return f