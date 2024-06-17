import sys

class Process:
    def __init__(self, name, arrival_time, burst_time):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_burst_time = burst_time
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1

def parse_input_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Initialize variables
    process_count = None
    run_for = None
    algorithm = None
    quantum = None
    processes = []

    # Parse lines
    for line in lines:
        if line.startswith('processcount'):
            process_count = int(line.split()[1])
        elif line.startswith('runfor'):
            run_for = int(line.split()[1])
        elif line.startswith('use'):
            algorithm = line.split()[1]
        elif line.startswith('quantum'):
            quantum = int(line.split()[1])
        elif line.startswith('process name'):
            parts = line.split()
            name = parts[2]
            arrival = int(parts[4])
            burst = int(parts[6])
            processes.append(Process(name, arrival, burst))
    
    # Check for missing parameters
    if process_count is None:
        raise ValueError("Missing parameter processcount")
    if run_for is None:
        raise ValueError("Missing parameter runfor")
    if algorithm is None:
        raise ValueError("Missing parameter use")
    if algorithm == 'rr' and quantum is None:
        raise ValueError("Missing quantum parameter when use is 'rr'")
    if len(processes) != process_count:
        raise ValueError(f"Expected {process_count} processes, but found {len(processes)}")
    
    return process_count, run_for, algorithm, quantum, processes

def fifo_scheduling(processes, run_for):
    log = []
    processes.sort(key=lambda x: x.arrival_time)
    current_time = 0
    for process in processes:
        if current_time >= run_for:
            break
        if current_time < process.arrival_time:
            current_time = process.arrival_time
        log.append(f'Time {current_time}: {process.name} selected')
        if process.response_time == -1:
            process.response_time = current_time - process.arrival_time
        process.waiting_time = current_time - process.arrival_time
        remaining_time = min(process.burst_time, run_for - current_time)
        process.turnaround_time = process.waiting_time + remaining_time
        process.remaining_burst_time -= remaining_time
        current_time += remaining_time
    while current_time < run_for:
        log.append(f'Time {current_time}: Idle')
        current_time += 1
    log.append(f'Finished at time {run_for}')
    return processes, log

def sjf_scheduling(processes, run_for):
    log = []
    processes.sort(key=lambda x: (x.arrival_time, x.burst_time))
    current_time = 0
    scheduled_processes = []
    while processes and current_time < run_for:
        available_processes = [p for p in processes if p.arrival_time <= current_time]
        if not available_processes:
            current_time = min(p.arrival_time for p in processes)
            continue
        process = min(available_processes, key=lambda x: x.burst_time)
        processes.remove(process)
        log.append(f'Time {current_time}: {process.name} selected')
        if process.response_time == -1:
            process.response_time = current_time - process.arrival_time
        process.waiting_time = current_time - process.arrival_time
        remaining_time = min(process.burst_time, run_for - current_time)
        process.turnaround_time = process.waiting_time + remaining_time
        process.remaining_burst_time -= remaining_time
        current_time += remaining_time
        scheduled_processes.append(process)
    while current_time < run_for:
        log.append(f'Time {current_time}: Idle')
        current_time += 1
    log.append(f'Finished at time {run_for}')
    return scheduled_processes, log

def round_robin_scheduling(processes, run_for, quantum):
    from collections import deque
    log = []
    queue = deque(processes)
    current_time = 0
    while queue and current_time < run_for:
        process = queue.popleft()
        if current_time < process.arrival_time:
            current_time = process.arrival_time
        log.append(f'Time {current_time}: {process.name} selected')
        if process.response_time == -1:
            process.response_time = current_time - process.arrival_time
        time_slice = min(quantum, process.remaining_burst_time, run_for - current_time)
        current_time += time_slice
        process.remaining_burst_time -= time_slice
        if process.remaining_burst_time > 0 and current_time < run_for:
            queue.append(process)
        else:
            process.turnaround_time = current_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
    while current_time < run_for:
        log.append(f'Time {current_time}: Idle')
        current_time += 1
    log.append(f'Finished at time {run_for}')
    return processes, log

def schedule_processes(file_path, output_file_path):
    try:
        process_count, run_for, algorithm, quantum, processes = parse_input_file(file_path)
    except ValueError as e:
        print(f"Error: {str(e)}")
        return
    
    try:
        if algorithm == 'fifo':
            scheduled_processes, log = fifo_scheduling(processes, run_for)
        elif algorithm == 'sjf':
            scheduled_processes, log = sjf_scheduling(processes, run_for)
        elif algorithm == 'rr':
            scheduled_processes, log = round_robin_scheduling(processes, run_for, quantum)
        else:
            raise ValueError("Unknown algorithm specified")
        
        with open(output_file_path, 'w') as output_file:
            output_file.write(f'Number of processes: {process_count}\n')
            output_file.write(f'Algorithm: {algorithm}\n')
            if algorithm == 'rr':
                output_file.write(f'Quantum: {quantum}\n')
            for entry in log:
                output_file.write(f'{entry}\n')
            output_file.write(f'\nProcess details:\n')
            for process in scheduled_processes:
                output_file.write(f'Process {process.name}: Waiting Time = {process.waiting_time}, Turnaround Time = {process.turnaround_time}, Response Time = {process.response_time}\n')
                if process.remaining_burst_time > 0:
                    output_file.write(f'Process {process.name} did not finish\n')

        print(f'Schedule written to {output_file_path}')
    except ValueError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: scheduler-get.py <input file> <output file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    schedule_processes(input_file, output_file)
