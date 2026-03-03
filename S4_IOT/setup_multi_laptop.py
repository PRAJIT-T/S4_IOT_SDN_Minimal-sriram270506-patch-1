#!/usr/bin/env python3
"""
MULTI-LAPTOP DEPLOYMENT SETUP GUIDE
Run this to prepare your system for real-world deployment
"""

import os
import sys
import json
import argparse

def create_multi_laptop_config(controller_ip, ap_ip, monitor_ip, attacker_ip):
    """Create configuration file for multi-laptop setup"""
    
    config = {
        "deployment_type": "multi_laptop",
        "network_type": "real_wifi",
        "controller": {
            "ip": controller_ip,
            "port": 9000,
            "role": "Decision maker - monitors metrics and isolates attackers"
        },
        "ap_agent": {
            "ip": ap_ip,
            "port": 9001,
            "role": "WiFi AP simulator - reports network metrics"
        },
        "monitor_agent": {
            "ip": monitor_ip,
            "port": 9000,
            "role": "Traffic monitor - tracks packet rates"
        },
        "attacker": {
            "ip": attacker_ip,
            "port": 9001,
            "role": "Jamming simulator - floods WiFi channel"
        },
        "wifi_settings": {
            "router": "Your WiFi Router",
            "channel": 6,
            "frequency": "2.4 GHz",
            "note": "All laptops must be on same WiFi network"
        }
    }
    
    with open('config_multi_laptop.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("Created config_multi_laptop.json")
    return config

def print_deployment_guide(config):
    """Print step-by-step deployment guide"""
    
    output = f"""
MULTI-LAPTOP DEPLOYMENT GUIDE
=============================

YOUR CONFIGURATION:
{config['controller']['ip']} - Controller (Laptop 1)
  Role: Decision maker

{config['ap_agent']['ip']} - AP Agent (Laptop 2)  
  Role: Reports metrics

{config['monitor_agent']['ip']} - Monitor (Laptop 3)
  Role: Tracks traffic

{config['attacker']['ip']} - Attacker (Laptop 4)
  Role: Launches jamming

All laptops must connect to SAME WiFi router.


ON LAPTOP 1 (CONTROLLER at {config['controller']['ip']}):
  1. Copy all Python files
  2. Run: python3 sdn_controller_multi_laptop.py --host 0.0.0.0 --port 9000
  3. Wait for: "Listening on 0.0.0.0:9000"
  4. Expected: "Waiting for agent connections..."

ON LAPTOP 2 (AP AGENT at {config['ap_agent']['ip']}):
  1. Copy all Python files
  2. Edit ap_agent.py
     - Line 9:  self.controller_ip = '{config['controller']['ip']}'
     - Line 15: self.listen_socket.bind(('0.0.0.0', 9001))
  3. Run: python3 ap_agent.py
  4. Expected: "Listening on 0.0.0.0:9001"

ON LAPTOP 3 (MONITOR at {config['monitor_agent']['ip']}):
  1. Copy all Python files
  2. Edit monitor_agent.py
     - Line 8: self.controller_ip = '{config['controller']['ip']}'
  3. Run: python3 monitor_agent.py
  4. Expected: "Controller: {config['controller']['ip']}:9000"

ON LAPTOP 4 (ATTACKER at {config['attacker']['ip']}):
  1. Copy all Python files
  2. Wait 10-15 seconds for other components
  3. Run: python3 attacker.py --target-ap {config['ap_agent']['ip']} --controller {config['controller']['ip']} --channel 6 --duration 15
  4. Expected: "STARTING JAMMING ATTACK!"


WHAT YOU'LL SEE ON CONTROLLER (every 5 seconds):

[BASELINE - First 10 seconds]
Throughput: 4.50 Mbps
RSSI: -45 dBm
Packet Rate: 300 pps
Status: Clean

[ATTACK - Seconds 10-15]
Throughput: 0.90 Mbps (ALERT)
RSSI: -70 dBm (ALERT)
Packet Rate: 8200 pps (ALERT)
Status: JAMMING DETECTED

[AFTER ISOLATION]
JAMMING ATTACK DETECTED ON CHANNEL 6!
ISOLATING ATTACKER!
Source IP: {config['attacker']['ip']}


TIMING:
0-5s:   Components connect
5-10s:  Baseline metrics
10s:    Attacker starts
10-15s: Attack in progress
15s:    Attack detected
16s:    Attacker isolated
16+s:   Network recovers


TROUBLESHOOTING:

Connection refused:
  - Start controller FIRST
  - Wait 2-3 seconds

No metrics on controller:
  - Check IPs are correct
  - Verify AP and Monitor are running
  
Attacker won't connect:
  - Verify controller is running
  - Check firewall allows UDP
  
Not on same network:
  - All laptops must use SAME WiFi router
  - Check with: ifconfig | grep 'inet '


KEY POINTS:

This is REAL NETWORK DEPLOYMENT:
✓ Runs across multiple physical laptops
✓ Uses actual WiFi network
✓ Shows real latency and delays
✓ Demonstrates production architecture
✓ Each component runs independently

This is DIFFERENT from simulation:
✓ Simulation uses localhost (127.0.0.1)
✓ Multi-laptop uses real IPs (192.168.x.x)
✓ Simulation is fast and local
✓ Multi-laptop shows real network effects


TO GET YOUR IP ADDRESSES:

On each laptop, run:
  ifconfig | grep 'inet '

Look for line like:
  inet 192.168.1.XXX

Then run this setup script with those IPs:
  python3 setup_multi_laptop.py \\
    --controller-ip 192.168.1.101 \\
    --ap-ip 192.168.1.102 \\
    --monitor-ip 192.168.1.103 \\
    --attacker-ip 192.168.1.104

"""
    print(output)

def main():
    parser = argparse.ArgumentParser(description='Setup multi-laptop deployment')
    parser.add_argument('--controller-ip', required=True, help='Controller IP address')
    parser.add_argument('--ap-ip', required=True, help='AP Agent IP address')
    parser.add_argument('--monitor-ip', required=True, help='Monitor Agent IP address')
    parser.add_argument('--attacker-ip', required=True, help='Attacker IP address')
    
    args = parser.parse_args()
    
    print("\nMULTI-LAPTOP DEPLOYMENT SETUP")
    print("=" * 50)
    print(f"Controller:  {args.controller_ip}")
    print(f"AP Agent:    {args.ap_ip}")
    print(f"Monitor:     {args.monitor_ip}")
    print(f"Attacker:    {args.attacker_ip}")
    print()
    
    # Validate IPs
    for ip in [args.controller_ip, args.ap_ip, args.monitor_ip, args.attacker_ip]:
        parts = ip.split('.')
        if len(parts) != 4 or not all(p.isdigit() for p in parts):
            print(f"ERROR: Invalid IP address: {ip}")
            return 1
    
    # Create configuration
    config = create_multi_laptop_config(
        args.controller_ip,
        args.ap_ip,
        args.monitor_ip,
        args.attacker_ip
    )
    
    # Print guide
    print_deployment_guide(config)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
