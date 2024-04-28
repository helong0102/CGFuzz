import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))

'''
#!/bin/bash
solc --combined-json abi,bin,bin-runtime,srcmap,srcmap-runtime,ast contracts/CrowdFunding.sol > contracts/CrowdFunding.sol.json
solc --combined-json abi,bin,bin-runtime,srcmap,srcmap-runtime,ast assets/ReentrancyAttacker.sol > assets/ReentrancyAttacker.sol.json
solc --combined-json abi,bin,bin-runtime,srcmap,srcmap-runtime,ast assets/NormalAttacker.sol > assets/NormalAttacker.sol.json
./fuzzer --file contracts/CrowdFunding.sol.json --source contracts/CrowdFunding.sol --name CrowdFunding --assets assets/ --duration 5 --mode 0 --reporter 0 --attacker ReentrancyAttacker
'''
if __name__ == '__main__':
    # 在那执行就显示那个路径(terminal)
    work_dir = os.path.abspath(os.path.join(os.getcwd(), "."))
    # pycharm
    # work_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))

    fuzzMe_path = work_dir + '/fuzzMe'
    fuzzMe_1_path = work_dir + "/fuzzMe_1"
    fuzzMe_2_path = work_dir + "/fuzzMe_2"
    fuzzMe_1_content = "#!/bin/bash\n"
    fuzzMe_2_content = "#!/bin/bash\n"

    with open(fuzzMe_path, 'r') as f:
        lines = f.readlines()
        i = 1
        while i < len(lines) - 1:
            fuzzMe_1_content += lines[i]
            i += 1
        fuzzMe_2_content += lines[len(lines) - 1]
    f.close()

    with open(fuzzMe_1_path, 'w') as f:
        f.write(fuzzMe_1_content)
    f.close()

    with open(fuzzMe_2_path, 'w') as f:
        f.write(fuzzMe_2_content)
    f.close()
