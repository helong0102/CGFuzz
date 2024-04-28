import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))
from pattern_TS import detectDS

from pattern_BN import detectBN
from pattern_DC import detectDC
from pattern_OF import detectOF
from pattern_RE import detectRE
from pattern_UE import detectUE
from unsafecode_locating.ast_helper import AstHelper
from unsafecode_locating.utils import readtxt, get_location_by_src


def get_source_by_src(src, filePath):
    start, end = get_location_by_src(src)
    text = readtxt(filePath)
    return text[start:end]


def get_source_code_slice_and_src(node, filePath):
    src = node['src']
    source_code_slice = get_source_by_src(src, filePath)
    return source_code_slice, src


def get_unsafe_code_src(contents, inputFilePath):
    source_text = readtxt(inputFilePath)
    unsafe_code_src_list = []
    for content in contents:
        if len(content) == 0:
            continue
        for str in content:
            if len(str) == 0:
                continue
            else:
                start = source_text.find(str)
                length = len(str)
                unsafe_code_src_list.append((start, start + length))
    return unsafe_code_src_list


def get_unsafe_code_function(unsafe_code_src_list, func_infos):
    outputs = {}
    for function_name, src in func_infos.items():
        func_start, func_end = src['src']
        for unsafe_src in unsafe_code_src_list:
            unsafe_start, unsafe_end = unsafe_src
            if unsafe_start > func_start and unsafe_end < func_end:
                temp_info = {}
                temp_info["src"] = src['src']
                temp_info["unsafe_src"] = unsafe_src
                outputs[function_name] = temp_info
    return outputs


def findPosition(inputFileDir, file):
    inputFilePath = inputFileDir + file
    FileName = file.split('.')[0]
    c_name = inputFilePath + ":" + FileName

    outputs = {}
    contents = []

    # contents.append(detectDS(inputFilePath))
    # contents.append(detectBN(inputFilePath))
    # contents.append(detectOF(inputFilePath))
    contents.append(detectRE(inputFilePath))
    # contents.append(detectDC(inputFilePath))
    # contents.append(detectUE(inputFilePath))

    unsafe_code_src_list = get_unsafe_code_src(contents, inputFilePath)

    ast_helper = AstHelper(inputFilePath)
    func_name_to_def_nodes = ast_helper.get_func_name_to_def_nodes(c_name)

    for function_name, node in func_name_to_def_nodes.items():
        source_code_slice, src = get_source_code_slice_and_src(node, inputFilePath)
        start, end = get_location_by_src(src)
        function_info = {}
        function_info['src'] = (start, end)
        outputs[function_name] = function_info

    outputs = get_unsafe_code_function(unsafe_code_src_list, outputs)

    return outputs, True


def write_order(funcs_order, abis, _last):
    for node in abis:
        if node["type"] == "constructor":
            node["order"] = _last
        if node["type"] == "fallback":
            node["order"] = funcs_order[node['type']]
        if node["type"] == "function" and not node["constant"]:
            node["order"] = funcs_order[node["name"]]

    return json.dumps(abis)


def add_order_contracts(inputFileDir):
    Files = os.listdir(inputFileDir)
    for file in Files:
        if len(file.split(".")) <= 2 and file.split(".")[1] == "sol":
            output, flag = findPosition(inputFileDir, file)
            if not flag:
                continue

            un_safe_funcs = [key for key in output.keys()]
            # print(un_safe_funcs)

            json_name = file + ".json"
            json_content = {}

            with open(inputFileDir + json_name, 'r') as f:
                try:
                    jsons = json.load(f)
                    json_content = jsons
                except:
                    exit(1)
            f.close()

            funcs_order = {}
            index = 0
            for func_name in un_safe_funcs:
                funcs_order[func_name] = index
                index += 1
            contract_name = 'contracts/' + file
            contract = contract_name.split("/")[-1].split('.sol')[0]
            un_order_funcs = []
            tag_has_constructor = False
            abis = json.loads(json_content["contracts"][contract_name + ":" + contract]["abi"])
            for node in abis:
                if node["type"] == 'constructor':
                    tag_has_constructor = True
                if node['type'] == 'fallback':
                    un_order_funcs.append(node['type'])
                if node['type'] == 'function' and not node['constant']:
                    un_order_funcs.append(node['name'])

            un_order_funcs = [x for x in un_order_funcs if x not in un_safe_funcs]
            for func_name in un_order_funcs:
                funcs_order[func_name] = index
                index += 1
            if tag_has_constructor:
                funcs_order['constructor'] = index

            json_content["contracts"][contract_name + ":" + contract]["abi"] = \
                write_order(funcs_order, json.loads(json_content["contracts"][contract_name + ":" + contract]["abi"]),
                            index)

            with open(inputFileDir + json_name, "w") as r:
                json.dump(json_content, r)
            r.close()


def add_order_assets(inputFileDir):
    Files = os.listdir(inputFileDir)
    for file in Files:
        if len(file.split(".")) <= 2 and file.split(".")[1] == "sol":
            output, flag = findPosition(inputFileDir, file)
            if not flag:
                continue

            un_safe_funcs = [key for key in output.keys()]
            # print(un_safe_funcs)

            json_name = file + ".json"
            json_content = {}

            with open(inputFileDir + json_name, 'r') as f:
                try:
                    jsons = json.load(f)
                    json_content = jsons
                except:
                    exit(1)
            f.close()

            funcs_order = {}
            index = 0
            for func_name in un_safe_funcs:
                funcs_order[func_name] = index
                index += 1
            contract_name = 'assets/' + file
            contract = contract_name.split("/")[-1].split('.sol')[0]
            un_order_funcs = []
            tag_has_constructor = False
            abis = json.loads(json_content["contracts"][contract_name + ":" + contract]["abi"])
            for node in abis:
                if node["type"] == 'constructor':
                    tag_has_constructor = True
                if node['type'] == 'fallback':
                    un_order_funcs.append(node['type'])
                if node['type'] == 'function' and not node['constant']:
                    un_order_funcs.append(node['name'])

            un_order_funcs = [x for x in un_order_funcs if x not in un_safe_funcs]
            for func_name in un_order_funcs:
                funcs_order[func_name] = index
                index += 1
            if tag_has_constructor:
                funcs_order['constructor'] = index

            json_content["contracts"][contract_name + ":" + contract]["abi"] = \
                write_order(funcs_order, json.loads(json_content["contracts"][contract_name + ":" + contract]["abi"]),
                            index)

            with open(inputFileDir + json_name, "w") as r:
                json.dump(json_content, r)
            r.close()


def USCLocation():
    current_file_path = os.path.abspath(os.path.join(os.getcwd(), "."))
    # inputFileDir_contracts = current_file_path + "/../contracts/"
    # inputFileDir_assets = current_file_path + "/../assets/"
    # os run
    inputFileDir_contracts = current_file_path + "/contracts/"
    inputFileDir_assets = current_file_path + "/assets/"

    add_order_contracts(inputFileDir_contracts)
    add_order_assets(inputFileDir_assets)


if __name__ == '__main__':
    USCLocation()
