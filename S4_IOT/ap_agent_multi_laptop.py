#!/usr/bin/env python3
"""
WiFi AP Agent - Multi-Laptop Version
Simulates a WiFi Access Point with 2 virtual nodes
Reports metrics to controller via UDP
Configurable for multi-laptop deployment

Usage:
  python3 ap_agent_multi_laptop.py --controller 192.168.1.100 --listen 0.0.0.0 --port 9001
"""

import socket
import json
import time
import threading
import argparse
import sys
from datetime import datetime
import random

class APAgent:
    def __init__(self, controller_ip, listen_ip='0.0.0.0', listen_port=9001):
        self.controller_ip = controller_ip
        self.listen_ip = listen_ip
        self.listen_port = listen_port
        self.controller_port = 9000
        
        self.running = True
        self.phase = 'baseline'
        self.isolated_ips = set()
        
        # Get the actual IP address of this machine
        self.ap_ip = self.get_actual_ip()
        
        # Virtual nodes
        self.virtual_nodes = {
            'node1': {'ip': '192.168.1.10', 'mac': 'AA:BB:CC:DD:EE:01'},
            'node2': {'ip': '192.168.1.11', 'mac': 'AA:BB:CC:DD:EE:02'}
        }
        
        # Sockets
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind((self.listen_ip, self.listen_port))
        
        print(f"[AP Agent] Actual IP Address: {self.ap_ip}")
        print(f"[AP Agent] Listening on {self.listen_ip}:{self.listen_port}")
        print(f"[AP Agent] Controller at {self.controller_ip}:{self.controller_port}")
    
    def get_actual_ip(self):
        """Get the actual IP address of this machine"""
        try:
            # Connect to controller to determine our IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((self.controller_ip, self.controller_port))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            # Fallback: try to get from hostname
            try:
                return socket.gethostbyname(socket.gethostname())
            except:
                return "127.0.0.1"
    
    def generate_metrics(self):
        """Generate realistic WiFi metrics"""
        if self.phase == 'baseline':
            throughput = 4.5 + random.uniform(-0.3, 0.3)
            rssi = -45 + random.randint(-2, 2)
            packet_rate = 300 + random.randint(-50, 50)
            packet_loss = 0.5 + random.uniform(-0.2, 0.3)
        else:  # attack phase
            throughput = 0.9 + random.uniform(-0.2, 0.2)
            rssi = -70 + random.randint(-5, 5)
            packet_rate = 8000 + random.randint(0, 500)
            packet_loss = 75 + random.randint(-10, 10)
        
        return {
            'type': 'ap_metrics',
            'timestamp': time.time(),
            'channel': 6,
            'ap_ip': self.ap_ip,  # Include actual AP IP
            'throughput_mbps': round(throughput, 2),
            'rssi_dbm': rssi,
            'packet_rate_pps': int(packet_rate),
            'packet_loss_percent': round(packet_loss, 1),
            'connected_nodes': len(self.virtual_nodes) - len(self.isolated_ips),
            'virtual_nodes': self.virtual_nodes,  # Include node details
            'phase': self.phase
        }
    
    def send_metrics(self):
        """Send metrics to controller"""
        metrics = self.generate_metrics()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = json.dumps(metrics).encode()
            sock.sendto(message, (self.controller_ip, self.controller_port))
            sock.close()
        except Exception as e:
            print(f"[AP Agent] Error sending metrics: {e}")
    
    def receive_commands(self):
        """Listen for commands from controller"""
        self.listen_socket.settimeout(1.0)
        while self.running:
            try:
                data, addr = self.listen_socket.recvfrom(1024)
                try:
                    msg = json.loads(data.decode())
                    if msg.get('type') == 'controller_action':
                        action = msg.get('action')
                        print(f"[AP Agent] Received action: {action}")
                        
                        if action == 'switch_channel':
                            channel = msg.get('channel', 6)
                            self.phase = 'attack'
                            print(f"[AP Agent] Switching to channel {channel}")
                        
                        elif action == 'isolate':
                            target_ip = msg.get('source_ip')
                            self.isolated_ips.add(target_ip)
                            print(f"[AP Agent] ISOLATED {target_ip}")
                except json.JSONDecodeError:
                    pass
            except socket.timeout:
                pass
            except Exception as e:
                if self.running:
                    print(f"[AP Agent] Error: {e}")
    
    def metrics_loop(self):
        """Send metrics every second"""
        while self.running:
            self.send_metrics()
            time.sleep(1)
    
    def start(self):
        """Start the AP agent"""
        print(f"\n{'='*70}")
        print(f"WiFi AP Agent Started")
        print(f"{'='*70}")
        print(f"Status: Ready")
        print(f"Listening: {self.listen_ip}:{self.listen_port}")
        print(f"Controller: {self.controller_ip}:{self.controller_port}")
        print(f"Virtual Nodes: {len(self.virtual_nodes)}")
        print(f"{'='*70}\n")
        
        # Start threads
        cmd_thread = threading.Thread(target=self.receive_commands, daemon=True)
        metrics_thread = threading.Thread(target=self.metrics_loop, daemon=True)
        
        cmd_thread.start()
        metrics_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[AP Agent] Shutting down...")
            self.running = False

def main():
    parser = argparse.ArgumentParser(description='WiFi AP Agent - Multi-Laptop Version')
    parser.add_argument('--controller', default='127.0.0.1', help='Controller IP address')
    parser.add_argument('--listen', default='0.0.0.0', help='Local listen IP')
    parser.add_argument('--port', type=int, default=9001, help='Local listen port')
    
    args = parser.parse_args()
    
    try:
        agent = APAgent(args.controller, args.listen, args.port)
        agent.start()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
