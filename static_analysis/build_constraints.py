import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))
from static_analysis.data_cfg import get_contracts_cfg_and_initial_state_vars


def get_write_node_by_read_var_name(var_name, cfg):
    ret = []
    for function in cfg:
        for node in function.nodes:
            for variable in node.variables_written:
                if variable.name == str(var_name):
                    ret.append(node)
    return ret


def get_if_and_require_nodes(function):
    if_and_require_nodes = []
    for node in function.nodes:
        if node.type.namnodee == 'IF':
            if_and_require_nodes.append(node)
        if node.type.name == 'EXPRESSION':
            if 'require' in str(node):
                if_and_require_nodes.append(node)
    return if_and_require_nodes


def is_contain_global_var(variables_read, state_vars_name):
    for variable_read in variables_read:
        for state_var in state_vars_name:
            if variable_read.name == state_var:
                return True
    return False


def get_constraints_by_var_name(var_name, node, state_vars_name):
    ret = []
    while True:
        # 有多个父节点存在的情况下，只选择一条父节点即可，只要满足这个条件即可
        if node.type.name == 'ENTRYPOINT':
            break
        else:
            # 获取节点的约束信息: 为写操作节点或者为全局变量读的if或require语句
            # var_name为全局变量
            if var_name in node.variables_written:
                ret.append(node)
            # 判断条件语句是否对全局变量读
            elif (var_name not in node.variables_written) \
                    and (node.type.name == 'IF' or 'require' in str(node)) \
                    and is_contain_global_var(node.variables_read, state_vars_name):
                ret.append(node)
            node = node.fathers[0]
    return ret


def get_var_constraints(var_name, func_name, cfg, state_vars_name):
    ret = []

    write_nodes = get_write_node_by_read_var_name(var_name, cfg)
    # print(write_nodes)

    for node in write_nodes:
        if str(node.function) == func_name:
            continue
        else:
            var_constraints = get_constraints_by_var_name(var_name, node, state_vars_name)
            # 将多个不同函数的约束添加到一个list中
            ret.extend(var_constraints)

    return ret[::-1]


def get_state_vars(param):
    return [key for key in param]


def get_node_constraints(node, data_and_cfg):
    ret = {}
    # 需要获取全局变量名称
    state_vars_name = get_state_vars(data_and_cfg['init_state_var'])
    for var in node.variables_read:
        # 判断该变量是否为自依赖变量，自依赖则不考虑其他约束
        if var in node.variables_written:
            continue
        if str(var) in state_vars_name:
            var_constraints = get_var_constraints(var, node.function.name, data_and_cfg['cfg'], state_vars_name)
            ret[str(var)] = var_constraints
    return ret


def get_function_constraints(function, data_and_cfg):
    ret = {}
    for node in function.nodes:
        if 'ENTRY_POINT' in str(node) or 'END_IF' in str(node):
            continue
        if len(node.variables_read) > 0:
            node_constraints = get_node_constraints(node, data_and_cfg)
            ret[node] = node_constraints
    return ret


def get_constraints(contract):
    ret = {}
    for function in contract['cfg']:
        function_constraints = get_function_constraints(function, contract)
        ret[str(function.name)] = function_constraints
    return ret


def get_sol_cons(input_sol_path):
    ret = {}
    data_and_control_flow = get_contracts_cfg_and_initial_state_vars(input_sol_path)
    for c_name, contents in data_and_control_flow.items():
        cons_ret = get_constraints(contents)
        # 删除为空的变量约束
        temp_ret = {}
        for func_name, cons in cons_ret.items():
            temp = {}
            for node, var_cons in cons.items():
                temp1 = {}
                for var_name, con in var_cons.items():
                    if len(con) > 0:
                        temp1[var_name] = con
                        temp[node] = temp1
                        temp_ret[func_name] = temp

        ret[c_name] = temp_ret
    return ret, data_and_control_flow


if __name__ == '__main__':
    pass