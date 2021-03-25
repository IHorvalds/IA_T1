import sys
import os
import stopit

from search.ucs import ucs_timeout
from search.a_star import a_star_timeout, a_star_opt_timeout
from search.ida_star import ida_star_timeout

## Defaults
NSOL = 4
INPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
TIMEOUT = 1


def write_out(file, to_write):
    with open(file, 'a') as f:
        f.write(to_write)

def get_or_create_folder(path):
    if not os.path.exists(path):
            os.mkdir(path)
    return path

def write_results(result, output_file_path):
    with open(output_file_path, 'w') as f:
        f.write("")
    if isinstance(result, tuple):
        for index, r in enumerate(result[0]):
            write_out(output_file_path, r)
            write_out(output_file_path, "timp solutie: {}\n".format(result[3][index]))
        write_out(output_file_path, "noduri in memorie: {}\n".format(result[1]))
        write_out(output_file_path, "noduri procesate: {}\n".format(result[2]))
        write_out(output_file_path, "\n")
    else:
        write_out(output_file_path, result)

def run_ucs(file):
    result = ucs_timeout(os.path.join(INPUT_PATH, file), NSOL, timeout=TIMEOUT)
    output_folder = get_or_create_folder(os.path.join(OUTPUT_PATH, "ucs"))
    output_file_path = os.path.join(output_folder, "output_for_"+file)
    write_results(result, output_file_path)

def run_a_star(file):
    euristici = ["euristica banala", "euristica manhattan", "euristica euler", "neadmisibila"]

    output_folder = get_or_create_folder(os.path.join(OUTPUT_PATH, "a_star"))
    for euristica in euristici:
        result = a_star_timeout(os.path.join(INPUT_PATH, file), NSOL, euristica, timeout=TIMEOUT)
        output_file_path = os.path.join(output_folder, euristica+"_output_for_"+file)
        write_results(result, output_file_path)

def run_a_star_opt(file):
    euristici = ["euristica banala", "euristica manhattan", "euristica euler", "neadmisibila"]

    output_folder = get_or_create_folder(os.path.join(OUTPUT_PATH, "a_star_opt"))
    for euristica in euristici:
        result = a_star_opt_timeout(os.path.join(INPUT_PATH, file), euristica, timeout=TIMEOUT)
        output_file_path = os.path.join(output_folder, euristica+"_output_for_"+file)
        write_results(result, output_file_path)

def run_ida_star(file):
    euristici = ["euristica banala", "euristica manhattan", "euristica euler", "neadmisibila"]

    output_folder = get_or_create_folder(os.path.join(OUTPUT_PATH, "ida_star"))
    for euristica in euristici:
        result = ida_star_timeout(os.path.join(INPUT_PATH, file), NSOL, euristica, timeout=TIMEOUT)
        output_file_path = os.path.join(output_folder, euristica+"_output_for_"+file)
        write_results(result, output_file_path)

def main():
    """
    Main entrypoint for program
    
    Usage:
    message --[OPTIONS]=[VALUES]

    Options:
    --i     Path at which to look for input files.
            All files in the given directory will be used.
            Default: <directory of message.py>/inputs/

    --o     Path at which to write output files.
            Files with the same name will be overwritten.
            Default: <Current working directory>/outputs/

    --t     Timeout in seconds. Should support floating point
            values.
            Default: 1s
    
    --s     Number of solutions to compute per algorithm, per
            input.
            Default: 1

    --h     Print this message
    """
    global NSOL, INPUT_PATH, OUTPUT_PATH, TIMEOUT

    for arg in sys.argv:
        if arg[:4] == "--i=":
            INPUT_PATH = arg[4:]
        
        if arg[:4] == "--o=":
            OUTPUT_PATH = arg[4:]
        
        if arg[:4] == "--t=":
            TIMEOUT = float(arg[4:])

        if arg[:4] == "--s=":
            NSOL = int(arg[4:])
        
        if arg[:3] == "--h":
            print(main.__doc__)
            exit()
    
    print(NSOL, INPUT_PATH, OUTPUT_PATH, TIMEOUT)


    for file in os.listdir(INPUT_PATH):
        # rulam fiecare algoritm pentru fiecare fisier de input

        ## UCS
        run_ucs(file)

        ## A*
        run_a_star(file)

        ## A* Optimizat
        run_a_star_opt(file)

        ## IDA*
        run_ida_star(file)


if __name__ == "__main__":
    main()