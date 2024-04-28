# CGFuzz

CGFuzz: Smart Contract Vulnerability Detection Using Constraint-guided Gey-box Fuzzing.

## Requirements

CGFuzz is executed on Linux (ideally Ubuntu 20.04).

Dependencies:

- Cmake: >= 3.5.1
- Python: >= 3.8 (ideally 3.10)
- leveldb: 1.2.0
- Z3-slover: >= 4.5.1 (ideally 4.5.1)
- crytic-compile: 0.1.13
- solc-select: 1.0.4
- slither-analyzer: 0.10.1

## Build

Configure the project build with the following command to create the `build` directory with the configuration.

```shell
mkdir build; cd build # Create a build directory.
cmake ../sFuzz/		  # Configure the project.
cd fuzzer; make       # Build fuzzer target.
```

## Fuzz Contract

Create a directory `contracts` in the current directory.

```shell
mkdir contracts/
```

Start fuzzing using the command:

```shell
chmod +x run.sh
./run.sh
```

