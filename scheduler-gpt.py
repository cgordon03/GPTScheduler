#Combination of individual projects
#Written using ChatGPT

import sys
import re
from collections import deque

#Harper's data structure for process
class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining_burst = burst
        self.start_time = -1
        self.finish_time = 0
        self.wait_time = 0
        self.response_time = -1
        self.turnaround_time = 0

def parse_input(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()

    process_count = int(lines[0].split()[1])
    run_for = int(lines[1].split()[1])
    algorithm = lines[2].split()[1]
    
    quantum = None
    if algorithm == 'rr':
        quantum = int(lines[3].split()[1])
        process_lines = lines[4:-1]
    else:
        process_lines = lines[3:-1]

    processes = []
    for line in process_lines:
        parts = line.split()
        name = parts[2]
        arrival = int(parts[4])
        burst = int(parts[6])
        processes.append(Process(name, arrival, burst))

    return process_count, run_for, algorithm, quantum, processes

#Amoy's calculate_metrics
#Calculates metrics for FCFS and SJF
def calculate_metrics(processes):
    metrics = {}

    for process in processes:
        turnaround_time = process.finish_time - process.arrival
        wait_time = turnaround_time - process.burst
        response_time = process.response_time - process.arrival

        metrics[process.name] = {
            'wait': wait_time,
            'turnaround': turnaround_time,
            'response': response_time
        }

    return metrics


#Amoy's FCFS
def fcfs(processes, run_for):
    time = 0
    process_queue = deque(sorted(processes, key=lambda p: p.arrival))
    output = []
    arrived_processes = set()
    last_selected_process = None

    while time < run_for:
        while process_queue and process_queue[0].arrival <= time:
            arrived_process = process_queue.popleft()
            if arrived_process.name not in arrived_processes:
                output.append((time, f'{arrived_process.name} arrived'))
                arrived_processes.add(arrived_process.name)
            process_queue.appendleft(arrived_process)
            break

        if process_queue and process_queue[0].arrival <= time:
            process = process_queue.popleft()
            if process.start_time == -1:
                process.start_time = time
                process.response_time = time
            if last_selected_process != process:
                output.append((time, f'{process.name} selected (burst {process.burst:3})'))
                last_selected_process = process
            time += process.burst
            process.finish_time = time
            output.append((time, f'{process.name} finished'))
            last_selected_process = None
        else:
            output.append((time, 'Idle'))
            last_selected_process = None
            time += 1

    metrics = calculate_metrics(processes)   

    return output, metrics

#Harper's SJF
def sjf(processes, run_for):
    current_time = 0
    completed = 0
    n = len(processes)
    processes.sort(key=lambda x: x.arrival)
    logs = []
    current_process = None
    arrival_set = set()

    while completed != n or current_time < run_for:

        #Adds newly arrived processes
        for process in processes:
            if process.arrival == current_time and process.name not in arrival_set:
                logs.append((current_time, f'{process.name} arrived'))
                arrival_set.add(process.name)

        idx = -1
        min_remaining_time = float('inf')

        for i in range(n):
            if processes[i].arrival <= current_time and processes[i].remaining_burst > 0:
                if processes[i].remaining_burst < min_remaining_time:
                    min_remaining_time = processes[i].remaining_burst
                    idx = i
                elif processes[i].remaining_burst == min_remaining_time:
                    if processes[i].arrival < processes[idx].arrival:
                        idx = i

        #Uses idx to run through each process within processes
        if idx != -1:
            if processes[idx] != current_process:
                current_process = processes[idx]
                logs.append((current_time, f'{current_process.name} selected (burst {current_process.remaining_burst:3})'))

            #Updates processes start time and response time
            if processes[idx].start_time == -1:
                processes[idx].start_time = current_time
                processes[idx].response_time = current_time

            processes[idx].remaining_burst -= 1
            current_time += 1

            #If process finishes running
            if processes[idx].remaining_burst == 0:
                processes[idx].finish_time = current_time
                completed += 1
                logs.append((current_time, f'{current_process.name} finished'))
        else:
            logs.append((current_time, 'Idle'))
            current_time += 1

    while current_time < run_for:
        logs.append((current_time, 'Idle'))
        current_time += 1

    metrics = calculate_metrics(processes)    

    return logs, metrics

#Clayton's RR
def rr(processes, run_for, quantum):
    processes.sort(key=lambda p: p.arrival)
    current_time = 0
    log = []
    queue = []
    metrics = {p.name: {'wait': 0, 'turnaround': 0, 'response': None} for p in processes}
    time_slice = 0
    running_process = None
    burst_times = {p.name: p.burst for p in processes}  # Store original burst times

    while current_time < run_for:
        # Check for new arrivals
        arrivals = [p for p in processes if p.arrival == current_time]
        for process in arrivals:
            log.append((current_time, f'{process.name} arrived'))
            queue.append(process)

        # Handle time slice expiration or process completion
        if running_process and (time_slice == quantum or running_process.burst == 0):
            if running_process.burst > 0:
                queue.append(running_process)
            else:
                log.append((current_time, f'{running_process.name} finished'))
                metrics[running_process.name]['turnaround'] = current_time - running_process.arrival
            running_process = None
            time_slice = 0

        # Select the next process if none is running
        if not running_process and queue:
            running_process = queue.pop(0)
            log.append((current_time, f'{running_process.name} selected (burst {running_process.burst:>3})'))
            if metrics[running_process.name]['response'] is None:
                metrics[running_process.name]['response'] = current_time - running_process.arrival
            if running_process.start_time is None:
                running_process.start_time = current_time

        # Execute the running process
        if running_process:
            running_process.burst -= 1
            time_slice += 1

        # Log idle time if no process is running and no new arrivals
        if not running_process and not queue and not arrivals:
            log.append((current_time, 'Idle'))

        current_time += 1

    # Ensure the log shows idle times until the end of the run time
    while current_time < run_for:
        log.append((current_time, 'Idle'))
        current_time += 1

    # Calculate wait times correctly
    for process in processes:
        turnaround = metrics[process.name]['turnaround']
        burst = burst_times[process.name]
        response = metrics[process.name]['response']
        wait = turnaround - burst
        metrics[process.name] = {
            'wait': wait,
            'turnaround': turnaround,
            'response': response
        }

    return log, metrics

#Clayton's write output
def write_output(file_name, log, metrics, algorithm, quantum, run_for):
    # Generate .out file
    output_file_txt = file_name.replace('.in', '.out')
    with open(output_file_txt, 'w') as file:
        file.write(f"{len(metrics):>3} processes\n")  # Adjusted space to ensure 3-character width
        if algorithm == 'fcfs':
            file.write(f"Using First-Come First-Served\n")
        elif algorithm == 'sjf':
            file.write(f"Using preemptive Shortest Job First\n")  # Ensure consistent naming
        elif algorithm == 'rr':
            file.write(f"Using Round-Robin\n")
            file.write(f"Quantum {quantum:>3}\n\n")
        for entry in log:
            file.write(f"Time {entry[0]:>3} : {entry[1]}\n")
        file.write(f"Finished at time {run_for:>3}\n\n")
        for name, metric in sorted(metrics.items()):
            file.write(f"{name:<2} wait {metric['wait']:>3} turnaround {metric['turnaround']:>3} response {metric['response']:>3}\n")
    
    # Generate .html file
    output_file_html = file_name.replace('.in', '.html')
    with open(output_file_html, 'w') as file:
        file.write("<html><body>\n")
        file.write(f"<h2>{len(metrics)} processes</h2>\n")
        if algorithm == 'fcfs':
            file.write(f"<h3>Using First-Come First-Served</h3>\n")
        elif algorithm == 'sjf':
            file.write(f"<h3>Using preemptive Shortest Job First</h3>\n")
        elif algorithm == 'rr':
            file.write(f"<h3>Using Round-Robin</h3>\n")
            file.write(f"<p>Quantum {quantum}</p>\n")
        
        file.write("<table border='1'>\n")
        file.write("<tr><th>Time</th><th>Event</th></tr>\n")
        for entry in log:
            if "arrived" in entry[1]:
                file.write(f"<tr><td>{entry[0]:>3}</td><td style='color:green'>{entry[1]}</td></tr>\n")  # Green for arrival
            elif "selected" in entry[1]:
                file.write(f"<tr><td>{entry[0]:>3}</td><td style='color:blue'>{entry[1]}</td></tr>\n")  # Blue for selection
            elif "finished" in entry[1]:
                file.write(f"<tr><td>{entry[0]:>3}</td><td style='color:red'>{entry[1]}</td></tr>\n")  # Red for finish
            else:
                file.write(f"<tr><td>{entry[0]:>3}</td><td>{entry[1]}</td></tr>\n")  # Default color for idle
        file.write("</table>\n")

        file.write(f"<p>Finished at time {run_for}</p>\n")

        file.write("<table border='1'>\n")
        file.write("<tr><th>Process</th><th>Wait Time</th><th>Turnaround Time</th><th>Response Time</th></tr>\n")
        for name, metric in sorted(metrics.items()):
            file.write(f"<tr><td>{name}</td><td>{metric['wait']}</td><td>{metric['turnaround']}</td><td>{metric['response']}</td></tr>\n")
        file.write("</table>\n")

        file.write("</body></html>\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    process_count, run_for, algorithm, quantum, processes = parse_input(input_file)

    if algorithm == 'fcfs':
        log, metrics = fcfs(processes, run_for)
    elif algorithm == 'sjf':
        log, metrics = sjf(processes, run_for)
    elif algorithm == 'rr':
        if quantum is None:
            print("Error: Missing quantum parameter when use is 'rr'")
            sys.exit(1)
        log, metrics = rr(processes, run_for, quantum)
    else:
        print(f"Error: Unknown algorithm '{algorithm}'")
        sys.exit(1)

    write_output(input_file, log, metrics, algorithm, quantum, run_for)
