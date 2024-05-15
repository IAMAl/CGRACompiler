def ReadFile( file_path="./", file_name="mvm_cfg_loop.txt" ):
    """
    File-Open used for CFG (cyclic loops) file

    Arguments
        file_path:    path (directory) for source file
        file_name:    name of file for source file
    """

    with open(file_path + file_name, "r") as file:
        lines = []
        for line in file:
            #print("reading line: {}".format(line))
            line = line.replace("\n", '')
            lines.append(line)

        return lines