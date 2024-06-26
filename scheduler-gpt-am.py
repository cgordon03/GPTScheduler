#Amoy's code
#fixed version
import sys
from collections import deque

class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining_burst = burst
        self.start_time = -1
        self.completion_time = -1
        self.response_time = -1

def parse_input(file_name):
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found")
        sys.exit(1)

    process_count = None
    run_for = None
    use = None
    quantum = None
    processes = []

    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue

        if parts[0] == 'processcount':
            process_count = int(parts[1])
        elif parts[0] == 'runfor':
            run_for = int(parts[1])
        elif parts[0] == 'use':
            use = parts[1]
        elif parts[0] == 'quantum':
            quantum = int(parts[1])
        elif parts[0] == 'process':
            name = parts[2]
            arrival = int(parts[4])
            burst = int(parts[6])
            processes.append(Process(name, arrival, burst))
        elif parts[0] == 'end':
            break

    if use == 'rr' and quantum is None:
        print("Error: Missing quantum parameter when use is 'rr'")
        sys.exit(1)

    if process_count is None or run_for is None or use is None or len(processes) != process_count:
        print("Error: Missing parameter")
        sys.exit(1)

    return process_count, run_for, use, quantum, processes

def calculate_metrics(processes):
    metrics = {}

    for process in processes:
        turnaround_time = process.completion_time - process.arrival
        wait_time = turnaround_time - process.burst
        response_time = process.response_time - process.arrival

        metrics[process.name] = {
            'wait': wait_time,
            'turnaround': turnaround_time,
            'response': response_time
        }

    return metrics

def fifo_scheduler(processes, run_for):
    time = 0
    process_queue = deque(sorted(processes, key=lambda p: p.arrival))
    output = []
    arrived_processes = set()
    last_selected_process = None

    while time < run_for:
        while process_queue and process_queue[0].arrival <= time:
            arrived_process = process_queue.popleft()
            if arrived_process.name not in arrived_processes:
                output.append(f"Time {time} : {arrived_process.name} arrived")
                arrived_processes.add(arrived_process.name)
            process_queue.appendleft(arrived_process)
            break

        if process_queue and process_queue[0].arrival <= time:
            process = process_queue.popleft()
            if process.start_time == -1:
                process.start_time = time
                process.response_time = time
            if last_selected_process != process:
                output.append(f"Time {time} : {process.name} selected (burst {process.burst})")
                last_selected_process = process
            time += process.burst
            process.completion_time = time
            output.append(f"Time {time} : {process.name} finished")
            last_selected_process = None
        else:
            output.append(f"Time {time} : Idle")
            last_selected_process = None
            time += 1

    return output, processes

def sjf_scheduler(processes, run_for):
    time = 0
    process_queue = sorted(processes, key=lambda p: (p.arrival, p.burst))
    ready_queue = []
    output = []
    arrived_processes = set()
    last_selected_process = None

    while time < run_for:
        while process_queue and process_queue[0].arrival <= time:
            arrived_process = process_queue.pop(0)
            if arrived_process.name not in arrived_processes:
                output.append(f"Time {time} : {arrived_process.name} arrived")
                arrived_processes.add(arrived_process.name)
            ready_queue.append(arrived_process)

        if ready_queue:
            ready_queue.sort(key=lambda p: p.remaining_burst)
            process = ready_queue.pop(0)
            if process.start_time == -1:
                process.start_time = time
                process.response_time = time
            if last_selected_process != process:
                output.append(f"Time {time} : {process.name} selected (burst {process.remaining_burst})")
                last_selected_process = process
            time += 1
            process.remaining_burst -= 1
            if process.remaining_burst == 0:
                process.completion_time = time
                output.append(f"Time {time} : {process.name} finished")
                last_selected_process = None
            else:
                ready_queue.append(process)
        else:
            output.append(f"Time {time} : Idle")
            last_selected_process = None
            time += 1

    return output, processes

def rr_scheduler(processes, run_for, quantum):
    time = 0
    process_queue = deque(sorted(processes, key=lambda p: p.arrival))
    ready_queue = deque()
    output = []
    arrived_processes = set()
    last_selected_process = None

    while time < run_for:
        # Add processes to the ready queue as they arrive
        while process_queue and process_queue[0].arrival <= time:
            arrived_process = process_queue.popleft()
            if arrived_process.name not in arrived_processes:
                output.append(f"Time {time} : {arrived_process.name} arrived")
                arrived_processes.add(arrived_process.name)
            ready_queue.append(arrived_process)

        if ready_queue:
            process = ready_queue.popleft()
            if process.start_time == -1:
                process.start_time = time
                process.response_time = time
            # Always print when a process is selected to run
            output.append(f"Time {time} : {process.name} selected (burst {process.remaining_burst})")
            last_selected_process = process

            time_slice = min(quantum, process.remaining_burst)
            for _ in range(time_slice):
                if time >= run_for:
                    break
                time += 1
                process.remaining_burst -= 1
                # Check for new arrivals during the quantum
                while process_queue and process_queue[0].arrival <= time:
                    arrived_process = process_queue.popleft()
                    if arrived_process.name not in arrived_processes:
                        output.append(f"Time {time} : {arrived_process.name} arrived")
                        arrived_processes.add(arrived_process.name)
                    ready_queue.append(arrived_process)
                if process.remaining_burst == 0:
                    break

            if process.remaining_burst == 0:
                process.completion_time = time
                output.append(f"Time {time} : {process.name} finished")
                last_selected_process = None
            else:
                ready_queue.append(process)
                last_selected_process = process
        else:
            output.append(f"Time {time} : Idle")
            last_selected_process = None
            time += 1

    return output, processes

def main():
    if len(sys.argv) != 2:
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not input_file.endswith('.in'):
        print("Error: Input file should have .in extension")
        sys.exit(1)

    process_count, run_for, use, quantum, processes = parse_input(input_file)

    if use == 'fcfs':
        output, processes = fifo_scheduler(processes, run_for)
    elif use == 'sjf':
        output, processes = sjf_scheduler(processes, run_for)
    elif use == 'rr':
        output, processes = rr_scheduler(processes, run_for, quantum)
    else:
        print("Error: Unknown scheduling algorithm")
        sys.exit(1)

    metrics = calculate_metrics(processes)

    output_file = input_file.replace('.in', '.out')
    with open(output_file, 'w') as file:
        file.write(f"{process_count} processes\n")
        file.write(f"Using {use.upper()}\n")
        if use == 'rr':
            file.write(f"Quantum {quantum}\n")
        for line in output:
            file.write(line + "\n")
        file.write(f"Finished at time {run_for}\n")
        for process in processes:
            if process.completion_time > run_for:
                file.write(f"{process.name} did not finish\n")
            else:
                metrics_str = f"{process.name} wait {metrics[process.name]['wait']} turnaround {metrics[process.name]['turnaround']} response {metrics[process.name]['response']}\n"
                file.write(metrics_str)

if __name__ == '__main__':
    main()


#python main.py inputFile.in
#python main.py -i input.in
