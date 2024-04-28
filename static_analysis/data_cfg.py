import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))
from slither import Slither


def proccing_functions(functions):
    rets = {}
    for function in functions:
        if function.name == 'constructor' or function.name == 'slitherConstructorVariables':
            continue
        rets[function] = function.nodes
    return rets


def get_contracts_info(inputPath):
    slither = Slither(inputPath)
    contract_infos = {}
    for contract in slither.contracts:
        temp_contract = {}
        temp_contract['functions'] = proccing_functions(contract.functions)
        temp_contract['state_variables'] = contract.state_variables
        contract_infos[contract.name] = temp_contract
    return contract_infos


def get_state_variables_initial_value(contract_infos, c_name):
    state_variables = {}
    constructor_nodes = {}

    for state_variable in contract_infos[c_name]['state_variables']:
        state_variables[state_variable.name] = state_variable.expression

    for function in contract_infos[c_name]['functions']:
        if function.name == 'constructor':
            constructor_nodes = function.nodes
            break

    for node in constructor_nodes:
        if node.type.name == 'EXPRESSION':
            var_name = node.expression.expression_left.value if isinstance(node.expression.expression_left.value, str) else node.expression.expression_left.value.name
            var_value = node.expression.expression_right.value if isinstance(node.expression.expression_right.value, str) else node.expression.expression_right.value.name
            for state_variable_name in state_variables.keys():
                if state_variable_name == var_name:
                    state_variables[state_variable_name] = var_value

    return state_variables


def get_contracts_cfg_and_initial_state_vars(inputPath):
    rets = {}
    contract_infos = get_contracts_info(inputPath)
    for c_name in contract_infos:
        initial_state_vars = get_state_variables_initial_value(contract_infos, c_name)
        tmp = {}
        tmp['cfg'] = contract_infos[c_name]['functions']
        tmp['init_state_var'] = initial_state_vars
        rets[c_name] = tmp
    return rets


if __name__ == '__main__':
    pass

