#!/bin/bash

python3 ./static_analysis/__main__.py
python3 ./pre_analysis/pre_analysis.py

./sFuzz/cmake-build-debug/fuzzer/fuzzer -g -r 0 -d 10

# split fuzzMe into two parts
python3 ./unsafecode_locating/split_fuzzMe.py

chmod +x fuzzMe_1
./fuzzMe_1

python3 ./unsafecode_locating/get_targetLoc.py

sed -i 's|\.\/fuzzer|\.\/sFuzz\/cmake-build-debug\/fuzzer\/fuzzer|g' ./fuzzMe_2
chmod +x fuzzMe_2
./fuzzMe_2
