import time
import psutil
import subprocess
import argparse
from datetime import datetime
from termcolor import colored

# Configuration
CPU_THRESHOLD = 50  # Percentage
CHECK_INTERVAL = 60  # Seconds

def get_snmpd_process(debug=False):
    if debug:
        print("Debug: Checking for snmpd process...")
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'snmpd':
            if debug:
                print(f"Debug: Found snmpd process with PID {proc.info['pid']}")
            return proc
    if debug:
        print("Debug: snmpd process not found.")
    return None

def calculate_cpu_usage(proc, interval, debug=False):
    if debug:
        print(f"Debug: Calculating CPU usage for snmpd process with PID {proc.pid}")
    
    cpu_times_before = proc.cpu_times()
    system_cpu_times_before = psutil.cpu_times(percpu=True)
    
    time.sleep(interval)
    
    cpu_times_after = proc.cpu_times()
    system_cpu_times_after = psutil.cpu_times(percpu=True)
    
    cpu_usage_per_core = []
    
    for i in range(len(system_cpu_times_before)):
        system_total_time_before = sum(system_cpu_times_before[i])
        system_total_time_after = sum(system_cpu_times_after[i])
        system_total_time = system_total_time_after - system_total_time_before
        
        proc_total_time_before = cpu_times_before.user + cpu_times_before.system
        proc_total_time_after = cpu_times_after.user + cpu_times_after.system
        proc_total_time = proc_total_time_after - proc_total_time_before
        
        core_usage = (proc_total_time / system_total_time) * 100
        cpu_usage_per_core.append(core_usage)
    
    max_cpu_usage = max(cpu_usage_per_core)
    
    if debug:
        print(f"Debug: snmpd process {proc.pid} CPU usage per core: {cpu_usage_per_core}")
        print(f"Debug: snmpd process {proc.pid} Max CPU usage: {max_cpu_usage:.2f}%")
    
    return max_cpu_usage

def restart_snmpd(debug=False):
    try:
        if debug:
            print("Debug: Restarting snmpd service...")
        subprocess.run(['sudo', 'systemctl', 'restart', 'snmpd'], check=True)
        if debug:
            print("Debug: snmpd service restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart snmpd service: {e}")

def monitor_snmpd(debug=False):
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if debug:
            print(f"{timestamp} - Debug: Monitoring snmpd process...")
        proc = get_snmpd_process(debug)
        if proc:
            cpu_usage = calculate_cpu_usage(proc, CHECK_INTERVAL, debug)
            if cpu_usage > CPU_THRESHOLD:
                message = f"{timestamp} - CPU usage above threshold ({CPU_THRESHOLD}%). Restarting snmpd..."
                print(colored(message, 'red'))
                restart_snmpd(debug)
            else:
                message = f"{timestamp} - snmpd process {proc.pid} Max CPU usage: {cpu_usage:.2f}%"
                print(colored(message, 'green'))
        else:
            message = f"{timestamp} - snmpd process not found."
            print(colored(message, 'yellow'))

        if debug:
            print(f"{timestamp} - Debug: Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor snmpd CPU usage and restart if necessary.")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode to print detailed information.')
    args = parser.parse_args()
    monitor_snmpd(debug=args.debug)
