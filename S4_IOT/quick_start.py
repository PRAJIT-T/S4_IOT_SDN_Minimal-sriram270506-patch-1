#!/usr/bin/env python3
"""
QUICK START GUIDE - Run this to test the system
"""

import subprocess
import time
import sys
import os

def print_intro():
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║     SDN WiFi TESTBED - ATTACK DETECTION & ISOLATION               ║
║                                                                    ║
║  2 Virtual Nodes → WiFi → Controller → Detects → Isolates         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

WHAT WILL HAPPEN:
  1. Controller starts listening for metrics
  2. AP Agent simulates 2 virtual nodes on WiFi channel 6
  3. Monitor Agent tracks traffic (200-500 pps baseline)
  4. Attacker launches jamming after 10 seconds (8000+ pps)
  5. Controller detects anomalies:
     - Packet rate jumps: 300 pps → 8000 pps ⚠️
     - RSSI drops: -45 dBm → -70 dBm ⚠️
     - Throughput falls: 4.5 Mbps → 0.9 Mbps ⚠️
  6. Controller isolates attacker
  7. System switches to channel 11

DASHBOARD METRICS (printed every 5 seconds):
  ✓ Channel number (6, 11, or 2)
  ✓ Throughput in Mbps
  ✓ RSSI signal strength
  ✓ Packet loss percentage
  ✓ Packet rate (pps)
  ✓ Jammer status
  ✓ Detected attackers
  ✓ Isolated IPs

Ready? Press Enter to start the demo, or Ctrl+C to exit.
""")

def run_command(cmd, name):
    """Run a command and return the process"""
    print(f"Starting {name}...")
    return subprocess.Popen(cmd, shell=True)

if __name__ == '__main__':
    print_intro()
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nExiting without running demo.")
        sys.exit(0)
    
    print("\n" + "="*70)
    print("LAUNCHING AUTOMATED DEMO...")
    print("="*70 + "\n")
    
    # Run the automated demo
    result = subprocess.run([sys.executable, 'demo_attack_scenario.py'])
    sys.exit(result.returncode)
