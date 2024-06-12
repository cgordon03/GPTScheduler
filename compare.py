import os
import subprocess
import filecmp
import difflib

def run_scheduler(input_file, scheduler_script):
    result = subprocess.run(['python3', scheduler_script, input_file], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running scheduler for {input_file}: {result.stderr}")
        return False
    return True

def compare_outputs(expected_file, generated_file):
    if filecmp.cmp(expected_file, generated_file, shallow=False):
        print(f"Files {expected_file} and {generated_file} match.")
    else:
        print(f"Files {expected_file} and {generated_file} differ.")
        with open(expected_file, 'r') as file1, open(generated_file, 'r') as file2:
            expected_lines = file1.readlines()
            generated_lines = file2.readlines()
            diff = difflib.unified_diff(expected_lines, generated_lines, fromfile=expected_file, tofile=generated_file)
            for line in diff:
                print(line, end='')

def main():
    scheduler_script = 'scheduler-gpt.py'
    test_cases = [
        ('c2-fcfs.in', 'c2-fcfs.out'),
        ('c2-rr.in', 'c2-rr.out'),
        ('c2-sjf.in', 'c2-sjf.out'),
        ('c5-fcfs.in', 'c5-fcfs.out'),
        ('c5-rr.in', 'c5-rr.out'),
        ('c5-sjf.in', 'c5-sjf.out'),
        ('c10-fcfs.in', 'c10-fcfs.out'),
        ('c10-rr.in', 'c10-rr.out'),
        ('c10-sjf.in', 'c10-sjf.out')
    ]

    for input_file, expected_output_file in test_cases:
        if run_scheduler(input_file, scheduler_script):
            generated_output_file = input_file.replace('.in', '_test.out')
            compare_outputs(expected_output_file, generated_output_file)

if __name__ == "__main__":
    main()
