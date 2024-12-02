import random
import string
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import timeit
from memory_profiler import memory_usage
import gc

# Function to generate a random string of fixed length
def random_string(length=100):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Create a list of 1,000,000 random strings
print("Generating 1,000,000 random strings...")
random_strings = [random_string() for _ in range(1_000_000)]

# Define operations to benchmark
operations = {
    "uppercase": {
        "Python list": lambda strings: [s.upper() for s in strings],
        "NumPy": lambda arr: np.char.upper(arr),
        "Pandas object": lambda series: series.str.upper(),
        "Pandas string": lambda series: series.str.upper(),
        "Pandas Arrow": lambda series: series.str.upper(),
        "PyArrow": lambda arr: pc.ascii_upper(arr),
    },
    "find_substring": {
        "Python list": lambda strings: ['abc' in s for s in strings],
        "NumPy": lambda arr: np.char.find(arr, 'abc') >= 0,
        "Pandas object": lambda series: series.str.contains('abc'),
        "Pandas string": lambda series: series.str.contains('abc'),
        "Pandas Arrow": lambda series: series.str.contains('abc'),
        "PyArrow": lambda arr: pc.match_substring(arr, 'abc'),
    },
    "split": {
        "Python list": lambda strings: [s.split('a') for s in strings],
        "NumPy": lambda arr: np.char.split(arr, sep='a'),
        "Pandas object": lambda series: series.str.split('a'),
        "Pandas string": lambda series: series.str.split('a'),
        "Pandas Arrow": lambda series: series.str.split('a'),
        "PyArrow": lambda arr: pc.split_pattern(arr, 'a'),
    },
    "replace": {
        "Python list": lambda strings: [s.replace('a', 'zfds') for s in strings],
        "NumPy": lambda arr: np.char.replace(arr, 'a', 'zfds'),
        "Pandas object": lambda series: series.str.replace('a', 'zfds'),
        "Pandas string": lambda series: series.str.replace('a', 'zfds'),
        "Pandas Arrow": lambda series: series.str.replace('a', 'zfds'),
        "PyArrow": lambda arr: pc.replace_substring(arr, pattern='a', replacement='zfds'),
    },
    "pad": {
        "Python list": lambda strings: [s.ljust(110, ' ') for s in strings],
        "NumPy": lambda arr: np.char.ljust(arr, 110, ' '),
        "Pandas object": lambda series: series.str.pad(110, side='right', fillchar=' '),
        "Pandas string": lambda series: series.str.pad(110, side='right', fillchar=' '),
        "Pandas Arrow": lambda series: series.str.pad(110, side='right', fillchar=' '),
        "PyArrow": lambda arr: pc.ascii_rpad(arr, 110, padding=' '),
    },
    "count_char": {
        "Python list": lambda strings: [s.count('a') for s in strings],
        "NumPy": lambda arr: np.char.count(arr, 'a'),
        "Pandas object": lambda series: series.str.count('a'),
        "Pandas string": lambda series: series.str.count('a'),
        "Pandas Arrow": lambda series: series.str.count('a'),
        "PyArrow": lambda arr: pc.count_substring(arr, 'a'),
    },
    "startswith": {
        "Python list": lambda strings: [s.startswith('a') for s in strings],
        "NumPy": lambda arr: np.char.startswith(arr, 'a'),
        "Pandas object": lambda series: series.str.startswith('a'),
        "Pandas string": lambda series: series.str.startswith('a'),
        "Pandas Arrow": lambda series: series.str.startswith('a'),
        "PyArrow": lambda arr: pc.starts_with(arr, 'a'),
    },
    "strip": {
        "Python list": lambda strings: [s.strip() for s in strings],
        "NumPy": lambda arr: np.char.strip(arr),
        "Pandas object": lambda series: series.str.strip(),
        "Pandas string": lambda series: series.str.strip(),
        "Pandas Arrow": lambda series: series.str.strip(),
        "PyArrow": lambda arr: pc.utf8_trim_whitespace(arr),
    },
    "sort": {
        "Python list": lambda strings: sorted(strings),
        "NumPy": lambda arr: np.sort(arr),
        "Pandas object": lambda series: series.sort_values(),
        "Pandas string": lambda series: series.sort_values(),
        "Pandas Arrow": lambda series: series.sort_values(),
        "PyArrow": lambda arr: arr.take(pc.sort_indices(arr)),
    },
    "delete_sequence": {
        "Python list": lambda strings: [s for s in strings if 'ab' not in s],
        "NumPy": lambda arr: arr[np.char.find(arr, 'ab') == -1],
        "Pandas object": lambda series: series[~series.str.contains('ab')],
        "Pandas string": lambda series: series[~series.str.contains('ab')],
        "Pandas Arrow": lambda series: series[~series.str.contains('ab')],
        "PyArrow": lambda arr: arr.filter(pc.invert(pc.match_substring(arr, 'ab'))),
    },
    "custom_hash": {
        "Python list": lambda strings: [hash(s) for s in strings],
        "NumPy": lambda arr: np.array([hash(s) for s in arr]),
        "Pandas object": lambda series: series.apply(hash),
        "Pandas string": lambda series: series.apply(hash),
        "Pandas Arrow": lambda series: series.apply(hash),
        "PyArrow": lambda arr: pa.array([hash(s.as_py()) for s in arr]),
    },
}

# Function to measure memory usage
def measure_memory(func, *args, **kwargs):
    gc.collect()
    mem_before = memory_usage()[0]
    result = func(*args, **kwargs)  # Ensure the function runs
    mem_after = memory_usage()[0]
    return mem_after - mem_before

# Prepare input data for each backend
print("Preparing input data for each backend...")
input_data = {
    "Python list": random_strings,
    "NumPy": np.array(random_strings),
    "Pandas object": pd.Series(random_strings, dtype='object'),
    "Pandas string": pd.Series(random_strings, dtype='string'),
    "Pandas Arrow": pd.Series(random_strings, dtype=pd.ArrowDtype(pa.string())),
    "PyArrow": pa.array(random_strings),
}

# Perform benchmarks
print("Starting benchmarks...")
results = {}
memory_results = {}

for op_name, backends in operations.items():
    for backend_name, operation in backends.items():
        print(f"Performing {op_name} operation with {backend_name}")
        data = input_data[backend_name]
        # Measure execution time
        duration = timeit.timeit(lambda: operation(data), number=1)
        # Measure memory usage
        mem_usage = measure_memory(operation, data)
        results[(op_name, backend_name)] = duration
        memory_results[(op_name, backend_name)] = mem_usage

# Calculate speedups and store results
python_list_times = {k: v for (k, m), v in results.items() if m == 'Python list'}
speedups = {}

print("\nBenchmark Results:")
for (op_name, method), duration in results.items():
    speedup = python_list_times[op_name] / duration
    speedups[(op_name, method)] = speedup
    print(f"Operation: {op_name}, Method: {method}, Time: {duration:.4f}s, Speedup: {speedup:.2f}x")

# Create DataFrames for times, speedups, and memory usage
methods = ['Python list', 'NumPy', 'Pandas object', 'Pandas string', 'Pandas Arrow', 'PyArrow']
operations_list = list(operations.keys())

df_times = pd.DataFrame(index=methods, columns=operations_list)
df_speedups = pd.DataFrame(index=methods, columns=operations_list)
df_memory = pd.DataFrame(index=methods, columns=operations_list)

for (op_name, method), duration in results.items():
    df_times.loc[method, op_name] = duration

for (op_name, method), speedup in speedups.items():
    df_speedups.loc[method, op_name] = speedup

for (op_name, method), mem_usage in memory_results.items():
    df_memory.loc[method, op_name] = mem_usage

# Calculate and add the average values
df_times['Overall Time'] = df_times.mean(axis=1)
df_speedups['Overall Speedup'] = df_speedups.mean(axis=1)
df_memory['Overall Memory'] = df_memory.mean(axis=1)

# Clean DataFrames
df_times = df_times.fillna(0)
df_speedups = df_speedups.fillna(1)  # Speedup for missing methods is 1
df_memory = df_memory.fillna(0)

# Display the results
print("\nProcessing Times (seconds):")
print(df_times)

print("\nSpeedup over Python list (×):")
print(df_speedups)

print("\nMemory Usage (MB):")
print(df_memory)
