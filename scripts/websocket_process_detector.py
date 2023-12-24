import psutil

def find_procs_by_port(port):
    """Find a list of process names and PIDs listening on the given port."""
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        if proc.info['connections']:  # Check if connections is not None
            for conn in proc.info['connections']:
                if conn.status == 'LISTEN' and conn.laddr.port == port:
                    procs.append(proc.info)
                    break
    return procs

port = 8765
processes = find_procs_by_port(port)

if processes:
    print(f"Processes listening on port {port}:")
    for process in processes:
        print(f" - PID: {process['pid']}, Name: {process['name']}")
else:
    print(f"No processes are listening on port {port}.")
