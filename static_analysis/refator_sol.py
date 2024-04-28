import os
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))

from static_analysis.build_constraints import get_sol_cons
from static_analysis.parse_constriants import del_no_reached_cons_for_if_and_require, parse_constraints, \
    get_location_params_alert
from unsafecode_locating.ast_helper import AstHelper
from unsafecode_locating.utils import readtxt, get_location_by_src


def get_func_name_and_src(inputFilePath):
    ret = {}
    file = inputFilePath.split('/')[-1]
    FileName = file.split('.')[0]
    c_name = inputFilePath + ":" + FileName
    ast_helper = AstHelper(inputFilePath)
    func_name_to_def_nodes = ast_helper.get_func_name_to_def_nodes(c_name)
    for func_name, node in func_name_to_def_nodes.items():
        if func_name == 'constructor':
            pass
        else:
            ret[func_name] = (int(get_location_by_src(node['src'])[0]), int(get_location_by_src(node['src'])[1]))
    return ret


def get_func_name_and_list(inputFilePath):
    ret = {}
    file = inputFilePath.split('/')[-1]
    FileName = file.split('.')[0]
    c_name = inputFilePath + ":" + FileName
    ast_helper = AstHelper(inputFilePath)
    func_name_to_def_nodes = ast_helper.get_func_name_to_def_nodes(c_name)
    text = readtxt(inputFilePath)
    for func_name, node in func_name_to_def_nodes.items():
        if func_name == 'constructor':
            pass
        else:
            ret[func_name] = text[int(get_location_by_src(node['src'])[0]): int(get_location_by_src(node['src'])[1])]
    return ret


def get_func_name_and_params(code):
    pattern = r'function\s*(\w+)\s*\(.*?\)'
    match = re.search(pattern, code)
    return match.group()


def add_param(func_and_param, param):
    new_func_and_param = ""

    start_index = func_and_param.find('(')
    end_index = func_and_param.find(')')
    if len(func_and_param[start_index: end_index-1]) > 0:
        new_func_and_param = func_and_param[:end_index] + "," + param + func_and_param[end_index:]
    else:
        new_func_and_param = func_and_param[:end_index] + param + func_and_param[end_index:]

    return new_func_and_param


def get_insert_location(ret, exp_alter):
    position = ret.find(exp_alter)
    if position != -1:
        new_position = ret.find("\n", position)
        if new_position != -1:
            return new_position + 1


def get_func_name(code):
    ret = get_func_name_and_params(code)
    func_name = ret[8:].split('(')[0].strip()
    return func_name


def get_func_content_modify_after(code, exps, pars):
    ret = code

    if len(exps) > 0:
        i = 1
        global_exps = []
        for node, exp_list in exps.items():
            if (node.type.name == 'IF'):
                exp_alter = str(node.expression)
            else:
                exp_alter = str(node.expression)
                exp_alter = exp_alter.replace("(bool)", '')
            # 获取插入位置
            insert_index = get_insert_location(ret, exp_alter)
            # 拼接代码块
            func_name = get_func_name(ret)
            condition = 'isFirstTime_' + str(func_name) + str(i)
            code_block = "if(" + condition + ") { \n"
            for exp in exp_list:
                code_block += exp
                code_block += ";\n"
            code_block += condition
            code_block += " = false;\n"
            code_block += "}\n"
            ret = ret[:insert_index] + code_block + ret[insert_index:]
            # 收集全局变量
            global_exp = "bool private " + condition + " = true;"
            global_exps.append(global_exp)

            i += 1
        # 插入全局变量
        global_exp = ''
        for exp in global_exps:
            global_exp += exp
            global_exp += "\n"
        ret = ret[:0] + global_exp + ret[0:]

    for node, var_list in pars.items():
        if (node.type.name == 'IF'):
            exp_alter = str(node.expression)
        else:
            exp_alter = str(node.expression)
            exp_alter = exp_alter.replace("(bool)", '')

        i = 1
        for var in var_list:
            type = var.type
            name = var.name
            # 替换分支中的变量
            new_exp = exp_alter.replace(name, 'var_' + str(i))
            ret = ret.replace(exp_alter, new_exp)
            exp_alter = new_exp
            # 增加参数
            # 首先获取参数
            param = str(type) + " " + str('var_' + str(i))
            func_and_param = get_func_name_and_params(ret)
            new_param = add_param(func_and_param, param)
            ret = ret.replace(func_and_param, new_param)
            i += 1

    return ret


def get_sol_by_params_and_cons(constraints_expressions, params_alert_list, filepath, src_code):
    ret = {}
    func_name_and_list = get_func_name_and_list(filepath)
    params = {}
    for key, value in params_alert_list.items():
        params[str(key)] = value
    params_alert_list = params

    for func_name, code in func_name_and_list.items():
        # 通过func_name拿到对应的表达式约束和修改参数
        exps = ''
        pars = ''
        if func_name in [key for key in constraints_expressions.keys()]:
            exps = constraints_expressions[func_name]
        if func_name in [str(key) for key in params_alert_list.keys()]:
            pars = params_alert_list[func_name]

        ret[func_name] = get_func_content_modify_after(code, exps, pars)

    for func_name, s_code in func_name_and_list.items():
        src_code = src_code.replace(s_code, ret[func_name])

    return src_code


if __name__ == '__main__':
    pass