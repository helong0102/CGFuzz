import json
import os
import shlex
import subprocess
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))


def run_command(cmd):
    FNULL = open(os.devnull, 'w')
    solc_p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=FNULL)
    return solc_p.communicate()[0].decode('utf-8', 'strict')


def run_command_with_err(cmd):
    FNULL = open(os.devnull, 'w')
    solc_p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = solc_p.communicate()
    out = out.decode('utf-8', 'strict')
    err = err.decode('utf-8', 'strict')
    return out, err


def readlines(file):
    with open(file, 'r') as f:
        data = f.readlines()
        return data


def readtxt(file):
    with open(file, 'r') as f:
        data = f.read()
        return data


def get_contract_version_decline(filePath):
    lines = readlines(filePath)
    for line in lines:
        if line.strip().startswith("pragma") and line.strip().endswith(";"):
            return line


def get_location_by_src(src):
    start, len, _ = src.split(":")
    start = int(start)
    end = start + int(len)
    return start, end


def load_json(json_file_path):
    with open(json_file_path, "r", encoding='utf-8') as file:
        data = json.load(file)
        return data


def write_to_file(file_path, data):
    try:
        # 打开文件以写入数据，'w'表示写入模式，如果文件不存在则创建新文件
        with open(file_path, 'w') as file:
            # 将数据写入文件
            file.write(data)
        print("Successfully Written：", file_path)
    except Exception as e:
        print("Failed to Written：", str(e))


if __name__ == '__main__':
    pass
