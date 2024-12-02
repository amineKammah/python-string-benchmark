# Python String Processing Benchmark

This repository contains code to benchmark the performance and memory usage of different string processing frameworks in Python, including:

- **Python lists and strings** (native Python)
- **NumPy arrays**
- **Pandas Series** with `object` dtype
- **Pandas Series** with `string` dtype (Python backend)
- **Pandas Series** with Arrow string dtype (`string[pyarrow]`)
- **Native PyArrow arrays**

## Overview

The benchmark performs a series of string operations on a dataset of **1,000,000 random strings**, each 100 characters long. The operations include:

- **Modify Operations**:
  - `uppercase`: Convert strings to uppercase.
  - `replace`: Replace substrings.
  - `pad`: Pad strings to a certain length.
  - `strip`: Remove leading and trailing whitespace.
- **Non-modify Operations**:
  - `find_substring`: Check for the presence of a substring.
  - `count_char`: Count occurrences of a character.
  - `startswith`: Check if strings start with a specific prefix.
  - `sort`: Sort the array of strings alphabetically.
- **Complex Operations**:
  - `delete_sequence`: Remove strings containing a specific sequence.
  - `custom_hash`: Apply a Python `hash` function to each string.

The benchmark measures the execution time and memory usage of each operation across the different frameworks.

## Requirements

- Python 3.x
- NumPy
- Pandas
- PyArrow
- memory_profiler

You can install the required packages using:

```bash
pip install -r requirements.txt
```

## Running the Benchmark

To run the benchmark, execute the `benchmark.py` script:

```bash
python benchmark.py
```

**Note**: Processing large datasets can consume significant system resources and may take some time to complete.

## Understanding the Results

The benchmark outputs three tables:

- **Processing Times**: Shows the execution time (in seconds) of each operation for each framework.
- **Speedup over Python list**: Indicates how many times faster each framework is compared to the native Python implementation.
- **Memory Usage**: Displays the memory consumed (in MB) during each operation for each framework.

Use these results to compare the performance and memory efficiency of different string processing options in Python.

## License

This project is licensed under the MIT License.
