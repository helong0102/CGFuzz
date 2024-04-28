from z3 import *
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))

def check_greater_sat(left, right, state_vars):
    # 首先变量符号化
    left_symbol = Real(left.value.name)
    right_symbol = Real(right.value.name)
    # 取出对应变量的初始值
    left_value = ''
    right_value = ''
    for var_name, value in state_vars.items():
        if var_name == left.value.name:
            left_value = value
        elif var_name == right.value.name:
            right_value = value
    s = Solver()
    if left_value != '' and right_value != '':
        s.add(left_symbol > right_symbol, left_symbol == left_value, right_symbol == right_value)
    if left_value != '' and right_value == '':
        s.add(left_symbol > right_symbol, left_symbol == left_value)
    if left_value == '' and right_value != '':
        s.add(left_symbol > right_symbol, right_symbol == right_value)
    if left_value == '' and right_value == '':
        s.add(left_symbol > right_symbol)
    # if str(s.check()) == 'sat':
    #     return s.check(), s.model()
    # else:
    return s.check()


def check_less_sat(left, right, state_vars):
    # 首先变量符号化
    left_symbol = Real(left.value.name)
    right_symbol = Real(right.value.name)
    # 取出对应变量的初始值
    left_value = ''
    right_value = ''
    for var_name, value in state_vars.items():
        if var_name == left.value.name:
            left_value = value
        elif var_name == right.value.name:
            right_value = value
    s = Solver()
    if left_value != '' and right_value != '':
        s.add(left_symbol < right_symbol, left_symbol == left_value, right_symbol == right_value)
    if left_value != '' and right_value == '':
        s.add(left_symbol < right_symbol, left_symbol == left_value)
    if left_value == '' and right_value != '':
        s.add(left_symbol < right_symbol, right_symbol == right_value)
    if left_value == '' and right_value == '':
        s.add(left_symbol < right_symbol)
    # if str(s.check()) == 'sat':
    #     return s.check(), s.model()
    # else:
    return s.check()


if __name__ == '__main__':
    pass