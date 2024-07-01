import time
import psutil
import subprocess
import argparse

# Configuration
CPU_THRESHOLD = 50  # Percentage based on per core, the script will work out per core so setting 50 here is 50% of 1 core
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

def check_cpu_usage(proc, debug=False):
    try:
        if debug:
            print(f"Debug: Checking CPU usage for snmpd process with PID {proc.pid}")
        cpu_usage = proc.cpu_percent(interval=CHECK_INTERVAL) / psutil.cpu_count()
        if debug:
            print(f"Debug: snmpd process {proc.pid} CPU usage: {cpu_usage:.2f}%")
        return cpu_usage
    except psutil.NoSuchProcess:
        if debug:
            print(f"Debug: snmpd process with PID {proc.pid} no longer exists.")
        return None

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
        if debug:
            print("Debug: Monitoring snmpd process...")
        proc = get_snmpd_process(debug)
        if proc:
            cpu_usage = check_cpu_usage(proc, debug)
            if cpu_usage is not None and cpu_usage > CPU_THRESHOLD:
                print(f"CPU usage above threshold ({CPU_THRESHOLD}%). Restarting snmpd...")
                restart_snmpd(debug)
        if debug:
            print(f"Debug: Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor snmpd CPU usage and restart if necessary.")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode to print detailed information.')
    args = parser.parse_args()
    monitor_snmpd(debug=args.debug)
