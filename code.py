import sys
# print (sys.argv)

class Process:
  def __init__(self, name, arrival, burst):
      self.name = name
      self.arrival = arrival
      self.burst = burst
      self.remaining_burst = burst
      self.start_time = None
      self.finish_time = None
      self.response_time = None
      self.waiting_time = 0

  def __repr__(self):
      return f'Process(name={self.name}, arrival={self.arrival}, burst={self.burst})'

def parse_input(filename):
    processes = []
    with open(filename, 'r') as file:
        lines = file.readlines()

    process_count = 0
    run_for = 0
    algorithm = None
    quantum = None

    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        directive = parts[0]

        if directive == 'processcount':
            process_count = int(parts[1])
        elif directive == 'runfor':
            run_for = int(parts[1])
        elif directive == 'use':
            algorithm = parts[1]
        elif directive == 'quantum':
            quantum = int(parts[1])
        elif directive == 'process':
            name = parts[2]
            arrival = int(parts[4])
            burst = int(parts[6])
            processes.append(Process(name, arrival, burst))
        elif directive == 'end':
            break

    return process_count, run_for, algorithm, quantum, processes

def fifo_scheduling(processes, run_for):
    time = 0
    queue = sorted(processes, key=lambda x: x.arrival)
    output = []
    while time < run_for:
        if queue and queue[0].arrival <= time:
            current = queue.pop(0)
            output.append(f"Time {time}: {current.name} selected (burst {current.burst})")
            current.start_time = time
            while current.remaining_burst > 0:
                time += 1
                current.remaining_burst -= 1
                if time >= run_for:
                    break
            current.finish_time = time
            current.response_time = current.start_time - current.arrival
            current.waiting_time = current.start_time - current.arrival
            output.append(f"Time {time}: {current.name} finished")
        else:
            output.append(f"Time {time}: Idle")
            time += 1
    return output, processes

def sjf_scheduling(processes, run_for):
    time = 0
    output = []
    ready_queue = []
    processes = sorted(processes, key=lambda x: x.arrival)
    arrival_log = set()
    
    while time < run_for:
        while processes and processes[0].arrival <= time:
            p = processes.pop(0)
            ready_queue.append(p)
            ready_queue.sort(key=lambda x: x.remaining_burst)
            if p.arrival not in arrival_log:
                output.append(f"Time {time} : {p.name} arrived")
                arrival_log.add(p.arrival)
                
        if ready_queue:
            current = ready_queue[0]
            if current.start_time is None:
                current.start_time = time
                current.response_time = time - current.arrival
            output.append(f"Time {time}: {current.name} selected (burst {current.remaining_burst})")
            current.remaining_burst -= 1
            time += 1
            if current.remaining_burst == 0:
                current.finish_time = time
                current.waiting_time = current.finish_time - current.arrival - current.burst
                ready_queue.pop(0)
                output.append(f"Time {time}: {current.name} finished")
        else:
            output.append(f"Time {time}: Idle")
            time += 1

    while time < run_for:
        output.append(f"Time {time} : Idle")
        time += 1
    
    return output, processes

def round_robin_scheduling(processes, run_for, quantum):
    time = 0
    output = []
    ready_queue = []
    processes = sorted(processes, key=lambda x: x.arrival)
    while time < run_for:
        while processes and processes[0].arrival <= time:
            ready_queue.append(processes.pop(0))
        if ready_queue:
            current = ready_queue.pop(0)
            if current.start_time is None:
                current.start_time = time
                current.response_time = time - current.arrival
            slice_time = min(quantum, current.remaining_burst)
            output.append(f"Time {time}: {current.name} selected (burst {current.remaining_burst})")
            for _ in range(slice_time):
                if time >= run_for:
                    break
                time += 1
                current.remaining_burst -= 1
                if current.remaining_burst == 0:
                    current.finish_time = time
                    current.waiting_time = current.finish_time - current.arrival - current.burst
                    output.append(f"Time {time}: {current.name} finished")
                    break
            if current.remaining_burst > 0:
                ready_queue.append(current)
        else:
            output.append(f"Time {time}: Idle")
            time += 1
    return output, processes

def calculate_metrics(processes):
    results = []
    for process in processes:
        turnaround_time = process.finish_time - process.arrival if process.finish_time else None
        results.append((process.name, process.waiting_time, turnaround_time, process.response_time))
    return results

def main(input_file):
    process_count, run_for, algorithm, quantum, processes = parse_input(input_file)

    if algorithm == 'fcfs':
        output, processes = fifo_scheduling(processes, run_for)
    elif algorithm == 'sjf':
        output, processes = sjf_scheduling(processes, run_for)
    elif algorithm == 'rr':
        if quantum is None:
            print("Error: Missing quantum parameter when use is 'rr'")
            return
        output, processes = round_robin_scheduling(processes, run_for, quantum)
    else:
        print(f"Error: Invalid scheduling algorithm '{algorithm}'")
        return

    output_file = input_file.replace('.in', '.out')
    with open(output_file, 'w') as file:
        file.write(f"{process_count} processes\n")
        file.write(f"Using {algorithm.upper()}\n")
        if algorithm == 'rr':
            file.write(f"Quantum {quantum}\n")
        for line in output:
            file.write(line + '\n')
        file.write(f"Finished at time {run_for}\n\n")

        metrics = calculate_metrics(processes)
        for name, wait, turnaround, response in metrics:
            if wait is not None:
                file.write(f"{name} wait {wait} turnaround {turnaround} response {response}\n")
            else:
                file.write(f"{name} did not finish\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: scheduler-gpt.py <input file>")
    else:
        main(sys.argv[1])

# python main.py -i
