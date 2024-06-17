import sys

class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining_burst = burst
        self.start_time = None
        self.end_time = None
        self.original_burst = burst

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

def calculate_metrics(processes):
    metrics = {}
    for process in processes:
        turnaround_time = process.end_time - process.arrival if process.end_time is not None else 0
        wait_time = turnaround_time- process.original_burst if process.start_time is not None else 0
        response_time = process.start_time - process.arrival if process.start_time is not None else 0
        metrics[process.name] = {
            'wait': wait_time,
            'turnaround': turnaround_time,
            'response': response_time
        }
    return metrics

def fcfs(processes, run_for):
    processes.sort(key=lambda p: p.arrival)
    current_time = 0
    log = []
    queue = []
    running_process = None
    temp_burst = 0

    while current_time < run_for:

        #Check for new arrivals
        arrivals = [p for p in processes if p.arrival == current_time]

        for process in arrivals:
            log.append((current_time, f'{process.name} arrived'))
            queue.append(process)
        
        #Check if running process finishes
        if running_process and running_process.burst == 0:
            running_process.end_time = current_time
            log.append((current_time, f'{running_process.name} finished'))
            running_process = None

        #If there is no running process, select one from the queue
        if running_process is None and queue:
            running_process = queue.pop(0)
            log.append((current_time, f'{running_process.name} selected (burst {running_process.burst:>3})'))
            if running_process.start_time is None:
                running_process.start_time = current_time

        #Execute the running process
        if running_process:
            running_process.burst -= 1

        #Log idle time only if no process is running and no new arrivals
        if running_process is None and not arrivals and not queue:
            log.append((current_time, 'Idle'))

        current_time += 1

    #Ensure the log shows idle times until the end of the run time
    while current_time < run_for:
        log.append((current_time, 'Idle'))
        current_time += 1

    metrics = calculate_metrics(processes)
    return log, metrics

def sjf(processes, run_for):
    processes.sort(key=lambda p: p.arrival)
    current_time = 0
    log = []
    ready_queue = []
    running_process = None

    while current_time < run_for:
        #Check for new arrivals and log them first
        arrivals = [p for p in processes if p.arrival == current_time]
        for process in arrivals:
            log.append((current_time, f'{process.name} arrived'))
            ready_queue.append(process)
            ready_queue.sort(key=lambda p: p.burst)

        #Execute the running process and handle completion
        if running_process:
            running_process.burst -= 1
            if running_process.burst == 0:
                running_process.end_time = current_time
                log.append((current_time, f'{running_process.name} finished'))
                running_process = None

        #Handle preemption if a new process arrives with shorter burst time
        if running_process and ready_queue and ready_queue[0].burst < running_process.burst:
            ready_queue.append(running_process)
            ready_queue.sort(key=lambda p: p.burst)
            running_process = ready_queue.pop(0)
            log.append((current_time, f'{running_process.name} selected (burst {running_process.burst:>3})'))

        #Select the next process if none is running 
        if not running_process and ready_queue:
            running_process = ready_queue.pop(0)
            log.append((current_time, f'{running_process.name} selected (burst {running_process.burst:>3})'))
            if running_process.start_time is None:
                running_process.start_time = current_time

        #Log idle time if no process is running and no new arrivals
        if not running_process and not ready_queue and not arrivals:
            log.append((current_time, 'Idle'))

        current_time += 1
    
    #Ensure the log shows idle times until the end of the run time
    while current_time < run_for:
        log.append((current_time, 'Idle'))
        current_time += 1

    metrics = calculate_metrics(processes)
    return log, metrics

def rr(processes, run_for, quantum):
    processes.sort(key=lambda p: p.arrival)
    current_time = 0
    log = []
    queue = []
    time_slice = 0
    running_process = None

    while current_time < run_for:

        #Check for new arrivals
        arrivals = [p for p in processes if p.arrival == current_time]
        for process in arrivals:
            log.append((current_time, f'{process.name} arrived'))
            queue.append(process)

        #Handle time slice expiration or process completion
        if running_process and (time_slice == quantum or running_process.burst == 0):
            if running_process.burst > 0:
                queue.append(running_process)
            else:
                running_process.end_time = current_time
                log.append((current_time, f'{running_process.name} finished'))
            running_process = None
            time_slice = 0

        #Select the next process if none is running
        if not running_process and queue:
            running_process = queue.pop(0)
            log.append((current_time, f'{running_process.name} selected (burst {running_process.burst:>3})'))
            if running_process.start_time is None:
                running_process.start_time = current_time

        #Execute the running process
        if running_process:
            running_process.burst -= 1
            time_slice += 1

        #Log idle time if no process is running and no new arrivals
        if not running_process and not queue and not arrivals:
            log.append((current_time, 'Idle'))

        current_time += 1
    
    #Ensure the log shows idle times until the end of the run time
    while current_time < run_for:
        log.append((current_time, 'Idle'))
        current_time += 1

    metrics = calculate_metrics(processes)
    return log, metrics

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