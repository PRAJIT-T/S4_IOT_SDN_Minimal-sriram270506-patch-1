#!/usr/bin/env python3
"""
Monitor Agent - Multi-Laptop Version
Tracks packet rates and network traffic patterns
Reports to controller

Usage:
  python3 monitor_agent_multi_laptop.py --controller 192.168.1.100
"""

import socket
import json
import time
import threading
import argparse
import sys
import random
from datetime import datetime

class MonitorAgent:
    def __init__(self, controller_ip, controller_port=9000, my_port=9002):
        self.controller_ip = controller_ip
        self.controller_port = controller_port
        self.my_port = my_port
        
        self.running = True
        self.phase = 'baseline'
        
        print(f"[Monitor Agent] Reporting to controller at {self.controller_ip}:{self.controller_port}")
        
    def generate_traffic_metrics(self):
        """Generate traffic metrics based on phase"""
        if self.phase == 'baseline':
            packet_rate = random.randint(200, 500)
            packet_loss = random.uniform(0.1, 1.0)
            latency = random.uniform(2, 5)
        else:  # attack phase
            packet_rate = random.randint(8000, 10000)
            packet_loss = random.uniform(40, 90)
            latency = random.uniform(50, 150)
        
        return {
            'type': 'monitor_metrics',
            'timestamp': time.time(),
            'channel': 6,
            'packet_rate_pps': packet_rate,
            'packet_loss_percent': round(packet_loss, 1),
            'latency_ms': round(latency, 1),
            'phase': self.phase
        }
    
    def send_metrics(self):
        """Send metrics to controller"""
        metrics = self.generate_traffic_metrics()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = json.dumps(metrics).encode()
            sock.sendto(message, (self.controller_ip, self.controller_port))
            sock.close()
        except Exception as e:
            print(f"[Monitor] Error sending: {e}")
    
    def metrics_loop(self):
        """Send metrics every second"""
        count = 0
        while self.running:
            self.send_metrics()
            count += 1
            time.sleep(1)
    
    def start(self):
        """Start the monitor agent"""
        print(f"\n{'='*70}")
        print(f"Monitor Agent Started")
        print(f"{'='*70}")
        print(f"Status: Monitoring")
        print(f"Controller: {self.controller_ip}:{self.controller_port}")
        print(f"Phase: {self.phase}")
        print(f"{'='*70}\n")
        
        # Start metrics thread
        metrics_thread = threading.Thread(target=self.metrics_loop, daemon=True)
        metrics_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[Monitor] Shutting down...")
            self.running = False

def main():
    parser = argparse.ArgumentParser(description='Monitor Agent - Multi-Laptop Version')
    parser.add_argument('--controller', default='127.0.0.1', help='Controller IP address')
    parser.add_argument('--port', type=int, default=9002, help='Local port')
    
    args = parser.parse_args()
    
    try:
        agent = MonitorAgent(args.controller)
        agent.start()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
