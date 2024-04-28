import os

import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))

# def split_contract(file):
#     contract_list = {}
#     contract = ''
#     lines = file.readlines()
#     new_contractname = ''
#     flag = False
#     for line in lines:
#         if line.strip().startswith("contract"):
#             if new_contractname != '':
#                 contract_list[new_contractname] = contract
#             new_contractname = line.split(" ", 2)[1].strip()
#             contract = line
#         elif line.strip().startswith("library") or line.strip().startswith("interface"):
#             flag = True
#         elif line.strip().endswith('}'):
#             flag = False
#         elif not flag:
#             contract += line
#     contract_list[new_contractname] = contract
#     return contract_list
import shutil

from unsafecode_locating.utils import readlines


def split_contract(file):
    contract_list = {}
    contract_name = ''
    contract_lines = []
    lines = file.readlines()
    inside_library = False

    for line in lines:
        if line.strip().startswith("contract "):
            if contract_name:
                contract_list[contract_name] = ''.join(contract_lines)
            contract_name = line.split(" ")[1].strip()
            contract_lines = [line]
            inside_library = False
        elif line.startswith("library "):
            inside_library = True
        elif line.startswith("interface "):
            inside_library = True
        elif line.endswith('{'):
            inside_library = False
        elif not inside_library:
            contract_lines.append(line)

    if contract_name:
        contract_list[contract_name] = ''.join(contract_lines)

    return contract_list


def split_function(f):
    function_list = []
    pc = []
    lines = f.readlines()
    flag = -1
    index = 0
    for line in lines:
        index += 1
        text = line.strip()
        if len(text) > 0:
            if text.split()[0] == "function" or text.split()[0] == "function()":
                function_list.append([line])
                flag += 1
                pc.append(index)
            elif len(function_list) > 0 and ("function" in function_list[flag][0]):
                function_list[flag].append(line)
    return function_list, pc


def testAnalysis(inputDir, file):
    filepath = inputDir + file
    functionList = []
    output = []
    index = 0
    contractList = []
    try:
        f = open(filepath, 'r')
        contractList = split_contract(f)
        # print(contractList)
    except:
        print("empty contract file!")
        return "", False
    try:
        f = open(filepath, 'r')
        functionList, pc = split_function(f)
        # print(functionList)
    except:
        print("empty contract file!")
        return "", "", False
    contractNames = []
    for func in functionList:
        fstr = ''
        for line in func:
            fstr += line
        index1 = fstr.find('{')
        index2 = fstr.find(';')
        if index2 != -1 and (index1 >= index2 or index1 < 0):
            for contractName in contractList:
                if fstr.split(';')[0] + ';' in contractList[contractName]:
                    contractNames.append(contractName)
            output.append(str(pc[index]))
        index += 1
    return output, set(contractNames), True


def get_new_file_name(original_file_name):
    fh = open(original_file_name)
    new_file_name = ""
    while True:
        line = fh.readline()
        if line.startswith("contract"):
            new_file_name = line.split(" ", 2)[1].strip()
            if new_file_name[-1] == "{":
                new_file_name = new_file_name[:-1]
            new_file_name += ".sol"
            break
        if not line:
            break
    fh.close()
    return new_file_name


def rename_sol_file(inputFileDir):
    Files = os.listdir(inputFileDir)
    for file in Files:
        if len(file.split(".")) <= 2 and file.split(".")[1] == "sol":
            original_file_name = inputFileDir + file
            new_file_name = "../contracts/" + get_new_file_name(original_file_name)
            if os.path.isfile(original_file_name) and new_file_name != "":
                shutil.copyfile(original_file_name, new_file_name)


def main():
    current_file_path = os.path.abspath(os.path.join(os.getcwd(), "."))
    # inputFileDir = current_file_path + "/../contracts/"
    # os run
    inputFileDir = current_file_path + "/contracts/"
    # rename_sol_file("../source_code/")
    outputs = {}
    Files = os.listdir(inputFileDir)
    for file in Files:
        if len(file.split(".")) <= 2 and file.split(".")[1] == "sol":
            output, contractNames, flag = testAnalysis(inputFileDir, file)
            if not flag:
                continue
            contractName = file.split(".")[0]
            # print(contractName)
            outputs[contractName] = list(set(output))
            for c in contractNames:
                if c == contractName.split('.')[0]:
                    print(c + ".sol may be absract, not implement an abstract parent's methods completely  \n"
                              "or not invoke an inherited contract's constructor correctly. ERROR: at line " + ','.join(
                        output))
                    try:
                        os.rename(dir + c + ".sol", dir + c + ".sol.err")
                    except:
                        print("file is not found!!!")
    # print(outputs)
    if ~len(outputs):
        print("pre analyze success!\n")


if __name__ == '__main__':
    main()
