import os

import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))

from static_analysis.build_constraints import get_sol_cons
from static_analysis.parse_constriants import del_no_reached_cons_for_if_and_require, parse_constraints, \
    get_location_params_alert
from static_analysis.refator_sol import get_sol_by_params_and_cons
from unsafecode_locating.utils import readtxt, write_to_file


if __name__ == '__main__':
    current_file_path = os.path.abspath(os.path.join(os.getcwd(), "."))
    # input_dir_path = current_file_path + "/../source_code/"
    # os run
    input_dir_path = current_file_path + "/source_code/"
    Files = os.listdir(input_dir_path)
    # output_dir_path = current_file_path + '/../contracts/'
    # os run
    output_dir_path = current_file_path + '/contracts/'
    for file in Files:
        if len(file.split(".")) <= 2 and file.split(".")[1] == "sol":
            print("Analysis Path:" + str(file))
            # 获取约束，初始数据状态和控制流
            constraints, data_and_control_flow = get_sol_cons(input_dir_path + file)
            # 将之前位置的代码进行替换
            src_code = readtxt(input_dir_path + file)
            for c_name in data_and_control_flow.keys():
                # 删除不可达分支没有依赖关系的约束
                del_no_reached_cons_for_if_and_require(constraints[c_name], data_and_control_flow[c_name])
                # 获取节点的约束表达式
                constraints_expressions = parse_constraints(constraints[c_name])
                # 获取函数参数应该修改的位置
                params_alert_list = get_location_params_alert(data_and_control_flow[c_name])
                # 将修改后的合约写入对应位置
                src_code = get_sol_by_params_and_cons(constraints_expressions, params_alert_list, input_dir_path + file, src_code)
            # 将src_code写进对应目录
            new_filename = 'NotFundCName.sol'
            fh = open(input_dir_path+file, 'r')
            while True:
                line = fh.readline()
                if line.startswith("contract"):
                    new_filename = line.split(" ", 2)[1].strip()
                    if new_filename[-1] == "{":
                        new_filename = new_filename[:-1]
                    new_filename += ".sol"
                if not line:
                    break
            fh.close()
            write_to_file(os.path.join(output_dir_path,new_filename), src_code)
