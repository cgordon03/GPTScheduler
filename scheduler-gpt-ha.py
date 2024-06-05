#Harper Archambault
#ChatGPT Scheduler

import sys
import re
from collections import deque

class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.start_time = -1
        self.finish_time = 0
        self.wait_time = 0
        self.response_time = -1
        self.turnaround_time = 0

def fifo_scheduling(processes, run_for):
    current_time = 0
    logs = []
    processes.sort(key=lambda x: x.arrival_time)
    process_queue = deque()
    idle_flag = True
    next_process_index = 0

    while current_time < run_for:
        while next_process_index < len(processes) and processes[next_process_index].arrival_time == current_time:
            process = processes[next_process_index]
            logs.append(f"Time {current_time:3} : {process.pid} arrived")
            process_queue.append(process)
            next_process_index += 1

        if process_queue:
            process = process_queue[0]
            if idle_flag:
                logs.append(f"Time {current_time:3} : {process.pid} selected (burst {process.remaining_time:3})")
                idle_flag = False
                if process.start_time == -1:
                    process.start_time = current_time
                    process.response_time = current_time - process.arrival_time

            process.remaining_time -= 1

            if process.remaining_time == 0:
                process.finish_time = current_time + 1
                process.turnaround_time = process.finish_time - process.arrival_time
                process.wait_time = process.turnaround_time - process.burst_time
                logs.append(f"Time {current_time + 1:3} : {process.pid} finished")
                process_queue.popleft()
                idle_flag = True
        else:
            logs.append(f"Time {current_time:3} : Idle")

        current_time += 1

    logs.append(f"Finished at time {current_time:3}\n")    

    return processes, logs

def preemptive_sjf_scheduling(processes, run_for):
    current_time = 0
    completed = 0
    n = len(processes)
    processes.sort(key=lambda x: x.arrival_time)
    logs = []
    current_process = None
    arrival_set = set()

    while completed != n or current_time < run_for:
        for process in processes:
            if process.arrival_time == current_time and process.pid not in arrival_set:
                logs.append(f"Time {current_time:3} : {process.pid} arrived")
                arrival_set.add(process.pid)

        idx = -1
        min_remaining_time = float('inf')

        for i in range(n):
            if processes[i].arrival_time <= current_time and processes[i].remaining_time > 0:
                if processes[i].remaining_time < min_remaining_time:
                    min_remaining_time = processes[i].remaining_time
                    idx = i
                elif processes[i].remaining_time == min_remaining_time:
                    if processes[i].arrival_time < processes[idx].arrival_time:
                        idx = i

        if idx != -1:
            if processes[idx] != current_process:
                #if current_process and current_process.remaining_time == 0:
                    #logs.append(f"Time {current_time:3} : {current_process.pid} finished")
                #if current_process and current_process.remaining_time > 0:
                    #logs.append(f"Time {current_time:3} : {current_process.pid} preempted")

                current_process = processes[idx]
                logs.append(f"Time {current_time:3} : {current_process.pid} selected (burst {current_process.remaining_time:3})")

            if processes[idx].start_time == -1:
                processes[idx].start_time = current_time
                processes[idx].response_time = current_time - processes[idx].arrival_time

            processes[idx].remaining_time -= 1
            current_time += 1

            if processes[idx].remaining_time == 0:
                processes[idx].finish_time = current_time
                processes[idx].turnaround_time = processes[idx].finish_time - processes[idx].arrival_time
                processes[idx].wait_time = processes[idx].turnaround_time - processes[idx].burst_time
                completed += 1
                logs.append(f"Time {current_time:3} : {processes[idx].pid} finished")
        else:
            logs.append(f"Time {current_time:3} : Idle")
            current_time += 1

    while current_time < run_for:
        logs.append(f"Time {current_time:3} : Idle")
        current_time += 1

    logs.append(f"Finished at time {current_time:3}\n")       

    return processes, logs

def round_robin_scheduling(processes, quantum, run_for):
    current_time = 0
    queue = deque()
    logs = []
    arrival_set = set()
    processes.sort(key=lambda x: x.arrival_time)
    n = len(processes)
    process_map = {process.pid: process for process in processes}

    # Add initial arriving processes to the queue
    for process in processes:
        if process.arrival_time == current_time:
            logs.append(f"Time {current_time:3} : {process.pid} arrived")
            arrival_set.add(process.pid)
            queue.append(process)

    while current_time < run_for:
        if queue:
            current_process = queue.popleft()

            if current_process.start_time == -1:
                current_process.start_time = current_time
            if current_process.response_time == -1:
                current_process.response_time = current_time - current_process.arrival_time

            time_slice = min(current_process.remaining_time, quantum)
            logs.append(f"Time {current_time:3} : {current_process.pid} selected (burst {current_process.remaining_time:3})")
            current_time += time_slice
            current_process.remaining_time -= time_slice

            # Add newly arrived processes during this time slice
            for process in processes:
                if current_process != process and current_process.remaining_time > 0:
                    if current_time - time_slice < process.arrival_time <= current_time and process.pid not in arrival_set:
                        logs.append(f"Time {process.arrival_time:3} : {process.pid} arrived")
                        arrival_set.add(process.pid)
                        queue.append(process)

            if current_process.remaining_time > 0:
                queue.append(current_process)
            else:
                current_process.finish_time = current_time
                current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
                current_process.wait_time = current_process.turnaround_time - current_process.burst_time
                logs.append(f"Time {current_time:3} : {current_process.pid} finished")
        else:
            logs.append(f"Time {current_time:3} : Idle")
            current_time += 1

        # Add any new arriving processes exactly at the current time
        for process in processes:
            if process.arrival_time == current_time and process.pid not in arrival_set:
                logs.append(f"Time {current_time:3} : {process.pid} arrived")
                arrival_set.add(process.pid)
                queue.append(process)

    while current_time < run_for:
        logs.append(f"Time {current_time:3} : Idle")
        current_time += 1

    logs.append(f"Finished at time {current_time:3}\n")    

    return processes, logs

def parse_input(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    process_count = int(re.search(r'\d+', lines[0]).group())
    run_for = int(re.search(r'\d+', lines[1]).group())
    scheduling_algo = lines[2].split()[1]
    quantum = None

    processes = []

    for line in lines[3:-1]:
        if line.startswith("quantum"):
            quantum = int(line.split()[1])
        else:
            parts = line.split()
            pid = parts[2]
            arrival_time = int(parts[4])
            burst_time = int(parts[6])
            processes.append(Process(pid, arrival_time, burst_time))

    return process_count, run_for, scheduling_algo, quantum, processes

def generate_output(process_count, scheduling_algo, processes, logs, quantum=None):
    output = []
    output.append(f"{process_count} processes")
    if scheduling_algo == 'fcfs':
        output.append("Using First-Come First-Serve")
    elif scheduling_algo == 'sjf':
        output.append("Using preemptive Shortest Job First")
    elif scheduling_algo == 'rr':
        output.append("Using Round-Robin")
        if quantum is not None:
            output.append(f"Quantum   {quantum}\n")

    for log in logs:
        output.append(log)
    #output.append(f"Finished at time {max([proc.finish_time for proc in processes] + [20])}\n")

    processes.sort(key=lambda x: x.pid)

    for process in processes:
        output.append(f"{process.pid} wait {process.wait_time:3} turnaround {process.turnaround_time:3} response {process.response_time}")
    
    return "\n".join(output)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python code.py <input_file>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    process_count, run_for, scheduling_algo, quantum, processes = parse_input(input_file_path)

    if scheduling_algo == 'fcfs':
        result, logs = fifo_scheduling(processes, run_for)
    elif scheduling_algo == 'sjf':
        result, logs = preemptive_sjf_scheduling(processes, run_for)
    elif scheduling_algo == 'rr':
        if quantum is None:
            raise ValueError("Quantum time must be specified for Round Robin scheduling")
        result, logs = round_robin_scheduling(processes, quantum, run_for)
    else:
        raise ValueError("Unsupported scheduling algorithm")

    output = generate_output(process_count, scheduling_algo, result, logs, quantum)

    output_file_path = input_file_path.replace('.in', 'test.out')
    with open(output_file_path, 'w') as output_file:
        output_file.write(output)

    print(f"Output written to {output_file_path}")