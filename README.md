# SNMPD Monitor

This repository contains a script to monitor the CPU usage of the `snmpd` process and restart it if necessary. The script is designed to run as a systemd service within a `screen` session.

## Prerequisites

- `screen`
- `psutil`
- `systemd`

## Installation

### 1. Install Dependencies

Ensure that `screen`, `termcolor` and `psutil` are installed on your system.

```bash
sudo apt-get update
sudo apt-get install screen python3 python3-pip
pip3 install psutil termcolor --break-system-packages
```

### 2. Clone the Repository

Clone this repository to your desired directory.

```bash
git clone https://github.com/Lostepic/snmpd-monitor /root/snmpd-mon
cd /root/snmpd-mon
```

### 3. Create the Wrapper Script

Create a wrapper script to start the Python script inside a `screen` session.

```bash
sudo nano /usr/local/bin/start_monitor_snmpd.sh
```

Add the following content:

```bash
#!/bin/bash
screen -dmS monitor_snmpd python3 /root/snmpd-mon/monitor_snmpd.py --debug
```

Make the wrapper script executable:

```bash
sudo chmod +x /usr/local/bin/start_monitor_snmpd.sh
```

### 4. Create the Systemd Service File

Create a systemd service file to manage the screen session.

```bash
sudo nano /etc/systemd/system/monitor_snmpd.service
```

Add the following content:

```ini
[Unit]
Description=Monitor snmpd CPU usage and restart if necessary
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/start_monitor_snmpd.sh
ExecStop=/usr/bin/screen -S monitor_snmpd -X quit
ExecReload=/usr/bin/screen -S monitor_snmpd -X quit && /usr/local/bin/start_monitor_snmpd.sh
User=root
WorkingDirectory=/root/snmpd-mon
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5. Reload Systemd and Start the Service

Reload systemd to recognize the new service, then enable and start it.

```bash
sudo systemctl daemon-reload
sudo systemctl enable monitor_snmpd.service
sudo systemctl start monitor_snmpd.service
```

## Managing the Screen Session

- **Attach to the screen session:**

  ```bash
  screen -r monitor_snmpd
```

- **Detach from the screen session:**

  Press `Ctrl+A` followed by `D`.
```

### Debug mode

Running the script with `--debug` will provide more details, by default the script is run with debug in the screen.
