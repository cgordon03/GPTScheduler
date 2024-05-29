import sys

class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining_burst = burst
        self.start_time = None
        self.end_time = None

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

def fcfs(processes, run_for):
    processes.sort(key=lambda p: p.arrival)
    current_time = 0
    log = []
    metrics = {}
    queue = []
    running_process = None

    while current_time < run_for:
        # Check for new arrivals
        arrivals = [p for p in processes if p.arrival == current_time]
        for process in arrivals:
            log.append((current_time, f'{process.name} arrived'))
            queue.append(process)

        # Check if running process finishes
        if running_process and running_process.burst == 0:
            running_process.end_time = current_time
            log.append((current_time, f'{running_process.name} finished'))
            metrics[running_process.name] = {
                'wait': running_process.start_time - running_process.arrival,
                'turnaround': running_process.end_time - running_process.arrival,
                'response': running_process.start_time - running_process.arrival
            }
            running_process = None

        # If there is no running process, select one from the queue
        if running_process is None and queue:
            running_process = queue.pop(0)
            log.append((current_time, f'{running_process.name} selected (burst {running_process.burst:>3})'))
            if running_process.start_time is None:
                running_process.start_time = current_time

        # Execute the running process
        if running_process:
            running_process.burst -= 1

        # Log idle time only if no process is running and no new arrivals
        if running_process is None and not arrivals and not queue:
            log.append((current_time, 'Idle'))

        current_time += 1

    # Ensure the log shows idle times until the end of the run time
    while current_time < run_for:
        log.append((current_time, 'Idle'))
        current_time += 1

    return log, metrics

def sjf(processes, run_for):
    processes.sort(key=lambda p: p.arrival)
    current_time = 0
    log = []
    ready_queue = []
    metrics = {p.name: {'wait': 0, 'turnaround': 0, 'response': None} for p in processes}
    burst_times = {p.name: p.burst for p in processes}
    running_process = None
    last_process_end_time = {p.name: None for p in processes}  # To track the end time of each process

    while current_time < run_for:
        # Check for new arrivals and log them first
        arrivals = [p for p in processes if p.arrival == current_time]
        for process in arrivals:
            log.append((current_time, f'{process.name} arrived'))
            ready_queue.append(process)
            ready_queue.sort(key=lambda p: p.burst)  # Sort by burst time for SJF

        # Execute the running process and handle completion
        if running_process:
            running_process.burst -= 1
            if running_process.burst == 0:
                log.append((current_time, f'{running_process.name} finished'))
                metrics[running_process.name]['turnaround'] = current_time - running_process.arrival
                last_process_end_time[running_process.name] = current_time
                running_process = None

        # Handle preemption if a new process arrives with shorter burst time
        if running_process and ready_queue and ready_queue[0].burst < running_process.burst:
            ready_queue.append(running_process)
            ready_queue.sort(key=lambda p: p.burst)
            running_process = ready_queue.pop(0)
            log.append((current_time, f'{running_process.name} selected (burst {running_process.burst:>3})'))

        # Select the next process if none is running
        if not running_process and ready_queue:
            running_process = ready_queue.pop(0)
            log.append((current_time, f'{running_process.name} selected (burst {running_process.burst:>3})'))
            if metrics[running_process.name]['response'] is None:
                metrics[running_process.name]['response'] = current_time - running_process.arrival
            if running_process.start_time is None:
                running_process.start_time = current_time

        # Log idle time if no process is running and no new arrivals
        if not running_process and not ready_queue and not arrivals:
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

        # Correct the turnaround and wait times
        if last_process_end_time[process.name]:
            turnaround = last_process_end_time[process.name] - process.arrival
            wait = turnaround - burst

        metrics[process.name] = {
            'wait': wait if wait is not None else 0,
            'turnaround': turnaround if turnaround is not None else 0,
            'response': response if response is not None else 0
        }

    return log, metrics

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

def write_output(file_name, log, metrics, algorithm, quantum, run_for):
    output_file = file_name.replace('.in', '.out')  # Added '_test' before the '.out' extension
    with open(output_file, 'w') as file:
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
