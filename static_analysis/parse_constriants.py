import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))
from collections import OrderedDict

from static_analysis.build_constraints import get_sol_cons, get_write_node_by_read_var_name
from static_analysis.z3_solver import check_greater_sat, check_less_sat


def get_state_var_value_by_cons_list(cons_list):
    ret = {}
    for node in cons_list:
        if node.type.name == 'EXPRESSION' and 'require' in str(node):
            expression = str(node).split(")")[-2].split("(")[-1]
            if "==" in expression:
                key_value = expression.split("==")
                ret[key_value[0].strip()] = key_value[1].strip()
        elif node.type.name == 'IF':
            pass
        else:
            key_value = str(node.expression).split("=")
            if str(node.expression.expression_return_type) == 'address':
                ret[key_value[0].strip()] = 'msg.sender'
            else:
                ret[key_value[0].strip()] = key_value[1].strip()

    return ret


def get_init_var_by_obj(init_state_var):
    init_state = {}
    for var_name, var_value in init_state_var.items():
        init_state[var_name] = str(var_value.value)
    return init_state


def update_cons_by_del_cons(cons, del_cons):
    for func_name, del_con in del_cons.items():
        if func_name in cons:
            for node, var_and_cons in del_con.items():
                if node in cons[func_name]:
                    for var_name, del_con_list in var_and_cons.items():
                        if var_name in cons[func_name][node]:
                            cons[func_name][node][var_name] = [con for con in cons[func_name][node][var_name] if
                                                               con not in del_con_list]

    # 从内到外删除为空的部分
    empty_nodes = []

    # 创建备份列表
    cons_items = list(cons.items())

    for func_name, func_cons in cons_items:
        for node, var_and_cons in func_cons.items():
            if not any(var_and_cons.values()):
                # 节点中的所有变量都为空
                empty_nodes.append((func_name, node))

    for func_name, node in empty_nodes:
        del cons[func_name][node]

    for func_name, func_cons in list(cons.items()):
        if not any(func_cons.values()):
            # 函数中的所有节点都为空
            del cons[func_name]

    return cons


def del_no_reached_cons_for_if_and_require(cons, d_cfg):
    ret = {}
    init_state_var = d_cfg['init_state_var']
    del_cons = {}
    for func_name, con in cons.items():
        tmp = {}
        for node, var_and_cons in con.items():
            if node.type.name == 'IF':
                expression_left = node.expression.expression_left
                expression_right = node.expression.expression_right
                type = node.expression.type
                # 根据类型确定选择的求解方式
                if type.name == 'GREATER':
                    init_state = get_init_var_by_obj(init_state_var)
                    s_check_init_T = check_greater_sat(expression_left, expression_right, init_state)
                    s_check_init_F = check_less_sat(expression_left, expression_right, init_state)
                    if str(s_check_init_T) == 'sat' and str(s_check_init_F) == 'sat':
                        continue
                    elif str(s_check_init_T) != 'sat' and str(s_check_init_F) == 'sat':
                        # 约束下检查左分支
                        tmp1 = {}
                        for var_name, cons_list in var_and_cons.items():
                            tmp2 = []
                            # 获取约束条件
                            var_and_value = {}
                            var_and_value = get_state_var_value_by_cons_list(cons_list)

                            # 将未在var_and_value中的值放入
                            var_and_value.update(
                                {key: value for key, value in init_state.items() if key not in var_and_value})

                            if str(check_greater_sat(expression_left, expression_right, var_and_value)) != 'sat':
                                # 删除约束
                                # print("删除约束")
                                tmp2.extend(cons_list)
                            tmp1[var_name] = tmp2
                        tmp[node] = tmp1
                        del_cons[func_name] = tmp
                    elif str(s_check_init_T) == 'sat' and str(s_check_init_F) != 'sat':
                        # 约束下检查右分支
                        tmp1 = {}
                        for var_name, cons_list in var_and_cons.items():
                            tmp2 = []
                            # 获取约束条件
                            var_and_value = {}
                            var_and_value = get_state_var_value_by_cons_list(cons_list)

                            # 将未在var_and_value中的值放入
                            var_and_value.update(
                                {key: value for key, value in init_state.items() if key not in var_and_value})

                            if str(check_less_sat(expression_left, expression_right, var_and_value)) != 'sat':
                                # 删除约束
                                # print("删除约束")
                                tmp2.extend(cons_list)
                            tmp1[var_name] = tmp2
                        tmp[node] = tmp1
                        del_cons[func_name] = tmp
                    else:
                        # 约束下检查两分支
                        tmp1 = {}
                        for var_name, cons_list in var_and_cons.items():
                            tmp2 = []
                            # 获取约束条件
                            var_and_value = {}
                            var_and_value = get_state_var_value_by_cons_list(cons_list)

                            # 将未在var_and_value中的值放入
                            var_and_value.update(
                                {key: value for key, value in init_state.items() if key not in var_and_value})

                            if str(check_greater_sat(expression_left, expression_right, var_and_value)) != 'sat' and \
                                    str(check_less_sat(expression_left, expression_right, var_and_value)) != 'sat':
                                # 删除约束
                                # print("删除约束")
                                tmp2.extend(cons_list)
                            tmp1[var_name] = tmp2
                        tmp[node] = tmp1
                        del_cons[func_name] = tmp

            if node.type.name == 'EXPRESSION' and 'require' in str(node):
                var_and_value = get_state_var_value_by_cons_list([node])
                # 判断初始状态下是否满足
                init_state = get_init_var_by_obj(init_state_var)
                is_sat = True
                for key, value in var_and_value.items():
                    for key_1, value_1 in init_state.items():
                        if key == key_1:
                            if value == value_1:
                                continue
                            else:
                                is_sat = False
                                break
                if is_sat:
                    # 删除约束
                    # print("删除约束")
                    tmp[node] = var_and_cons
                    del_cons[func_name] = tmp
                else:
                    # 判断约束条件下是否满足
                    tmp1 = {}
                    for var_name, cons_list in var_and_cons.items():
                        tmp2 = []
                        cons_var_and_value = get_state_var_value_by_cons_list(cons_list)
                        is_sat_cons = True
                        for key, value in var_and_value.items():
                            for key_1, value_1 in cons_var_and_value.items():
                                if key == key_1:
                                    if value == value_1:
                                        continue
                                    else:
                                        is_sat_cons = False
                                        break
                        if not is_sat_cons:
                            # 删除约束
                            # print("删除约束")
                            tmp2.extend(cons_list)
                        tmp1[var_name] = tmp2
                    tmp[node] = tmp1
                    del_cons[func_name] = tmp

    ret = update_cons_by_del_cons(cons, del_cons)

    return ret


def is_check_T_or_F(expression_node, expressions):
    ret = True
    tag = 0
    # 拿到下一个需要解析的结点
    next_node = None
    for ex_node in expressions:
        if ex_node == expression_node:
            tag = 1
            continue
        if tag == 1:
            next_node = ex_node
    # 判断节点的True分支是否包含next_node
    is_contained_t = False
    node_t = expression_node.son_true
    if node_t == next_node:
        is_contained_t = True
    else:
        while True:
            node_t = node_t.sons[0]
            if 'END' in node_t.type.name:
                break
            if node_t == next_node:
                is_contained_t = True
    if not is_contained_t:
        ret = False
    return ret


def parse_expression(expressions):
    ret = []
    for expression_node in expressions:
        if expression_node.type.name == 'IF':
            if is_check_T_or_F(expression_node, expressions):
                # print("取正操作")
                if expression_node.expression.type.name == 'GREATER':
                    left = expression_node.expression.expression_left
                    right = expression_node.expression.expression_right
                    exp = str(left) + " = "
                    exp += str(right)
                    exp += " + "
                    exp += '1'
                    ret.append(exp)
            else:
                # print("取反操作")
                if expression_node.expression.type.name == 'GREATER':
                    left = expression_node.expression.expression_left
                    right = expression_node.expression.expression_right
                    exp = str(right) + " = "
                    exp += str(left)
                    exp += " + "
                    exp += '1'
                    ret.append(exp)

        elif (expression_node.type.name == 'EXPRESSION') and \
                ('require' in str(expression_node)):
            key_and_value = get_state_var_value_by_cons_list([expression_node])
            exp = ''
            for key, value in key_and_value.items():
                exp += key
                exp += " = "
                exp += value
                ret.append(exp)
        else:
            key_and_value = get_state_var_value_by_cons_list([expression_node])
            exp = ''
            for key, value in key_and_value.items():
                exp += key
                exp += " = "
                exp += value
                ret.append(exp)

    return ret


def add_cons_exp_for_cfg(node, exp):
    ret = {}

    tmp_node = list(node.keys())[0]

    while True:
        if (tmp_node.type.name == 'IF') or \
                (tmp_node.type.name == 'EXPRESSION' and 'require' in str(tmp_node)):
            ret[tmp_node] = exp
            break
        else:
            tmp_node = tmp_node.fathers[0]
    return ret


def del_second_cons(node1, node2):
    node_2_del_list = {}
    for var_name_1, cons_1_list in node1.items():
        for var_name_2, cons_2_list in node2.items():
            # 判断这两个list中是否含有相同约束，有则在第二个中删除对应变量
            if set(cons_1_list).intersection(cons_2_list):
                # 存在交集，则删除var_name_2
                tmp = {}
                tmp[var_name_2] = cons_2_list
                node_2_del_list.update(tmp)
    # 删除node2中对应的变量
    for key in node_2_del_list.keys():
        del node2[key]


def del_cons(cfg_node):
    if_require_nodes = []
    for node in cfg_node.keys():
        if (node.type.name == 'IF') or \
                (node.type.name == 'EXPRESSION' and 'require' in str(node)):
            if_require_nodes.append(node)
    print()
    tag = 0
    for if_and_require_node in if_require_nodes:
        for node in cfg_node.keys():
            if if_and_require_node == node:
                tag = 1
                continue
            if tag == 1:
                # 判断两个节点是否有相同的约束
                # print("判断两个节点是否有相同的约束")
                del_second_cons(cfg_node[if_and_require_node], cfg_node[node])
            if (node.type.name == 'IF') or \
                    (node.type.name == 'EXPRESSION' and 'require' in str(node)):
                break  # 跳出一重循环
    return cfg_node


def del_cons_in_function(cons):
    ret = {}

    for func_name, cfg_node in cons.items():
        if len(cfg_node) > 1:
            # 直接删除存在相同的变量约束
            ret[func_name] = del_cons(cfg_node)
        else:
            ret[func_name] = cfg_node

    return ret


def parse_constraints(cons):
    ret = {}
    # 删除函数内部分支语句(IF和require语句)相反的依赖
    del_cons_in_function(cons)
    for func_name, node in cons.items():
        # 在此处判断约束属于那个分支(本函数),直接为CFG进行赋值
        exp = []
        for key, value in node.items():
            for var_name, expression_nodes in value.items():
                # 在此处判断条件是否需要取反操作(其他函数)
                exp_str = parse_expression(expression_nodes)
                exp.extend(exp_str)
        # 对表达式进行去重操作
        exp = list(OrderedDict.fromkeys(exp))
        # 为该函数对应的CFG中节点添加约束
        ret[func_name] = add_cons_exp_for_cfg(node, exp)
    return ret


def get_global_vars_name(param):
    ret = []
    for key, value in param.items():
        ret.append(key)
    return ret


def get_location_params_alert(d_cfg):
    ret = {}
    cfg = d_cfg['cfg']
    if_and_require = {}
    for func_name, node_list in cfg.items():
        tmp = []
        for node in node_list:
            if (node.type.name == 'IF') or \
                    (node.type.name == 'EXPRESSION' and 'require' in str(node)):
                # print("IF or Expression")
                tmp.append(node)
        if_and_require[func_name] = tmp

    # 拿到全局变量名
    global_vars = get_global_vars_name(d_cfg['init_state_var'])
    for func_name, node_list in if_and_require.items():
        tmp1 = {}
        for node in node_list:
            if len(node.variables_read) > 0:
                tmp2 = []
                for read_var in node.variables_read:
                    if str(read_var) in global_vars:
                        if len(get_write_node_by_read_var_name(read_var, cfg)) > 0:
                            tmp2.append(read_var)
                tmp1[node] = tmp2
        ret[func_name] = tmp1
    return ret


if __name__ == '__main__':
    pass
