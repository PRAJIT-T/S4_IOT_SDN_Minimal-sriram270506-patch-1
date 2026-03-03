#!/usr/bin/env python3
"""
Attacker Agent - Multi-Laptop Version
Simulates WiFi jamming attack
Reports to AP and controller

Usage:
  python3 attacker_multi_laptop.py --target-ap 192.168.1.10 --controller 192.168.1.100 --channel 6 --duration 15
"""

import socket
import json
import time
import threading
import argparse
import sys
import random
from datetime import datetime

class AttackerAgent:
    def __init__(self, target_ap_ip, controller_ip, channel=6, duration=15):
        self.target_ap_ip = target_ap_ip
        self.controller_ip = controller_ip
        self.ap_port = 9001
        self.controller_port = 9000
        self.channel = channel
        self.duration = duration
        
        self.running = False
        self.attacker_id = f"ATTACKER_{random.randint(1000, 9999)}"
        
        print(f"[Attacker] ID: {self.attacker_id}")
        print(f"[Attacker] Target AP: {self.target_ap_ip}:{self.ap_port}")
        print(f"[Attacker] Controller: {self.controller_ip}:{self.controller_port}")
        print(f"[Attacker] Channel: {self.channel}")
        print(f"[Attacker] Duration: {self.duration}s")
    
    def send_jam_packets(self):
        """Send jamming packets to AP"""
        count = 0
        start_time = time.time()
        
        while self.running:
            elapsed = time.time() - start_time
            if elapsed >= self.duration:
                print(f"\n[Attacker] Attack duration completed ({self.duration}s)")
                self.running = False
                break
            
            # Generate jam packet
            jam_packet = {
                'type': 'jam_packet',
                'source_id': self.attacker_id,
                'source_ip': '192.168.1.99',
                'channel': self.channel,
                'signal_strength': -80 + random.randint(-10, 10),
                'packet_rate': 8000 + random.randint(0, 500),
                'timestamp': time.time()
            }
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                message = json.dumps(jam_packet).encode()
                sock.sendto(message, (self.target_ap_ip, self.ap_port))
                sock.close()
                count += 1
                
                if count % 10 == 0:
                    print(f"[Attacker] Sent {count} jam packets ({elapsed:.1f}s elapsed)")
            except Exception as e:
                print(f"[Attacker] Error sending jam: {e}")
            
            time.sleep(0.01)  # Send ~100 packets per second
    
    def listen_for_isolation(self):
        """Listen for isolation notice from controller"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 9003))
        sock.settimeout(1.0)
        
        print(f"[Attacker] Listening for isolation notice on port 9003")
        
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                try:
                    msg = json.loads(data.decode())
                    if msg.get('type') == 'isolation_notice':
                        print(f"\n[Attacker] 🔒 ISOLATED by controller!")
                        print(f"[Attacker] Reason: {msg.get('reason')}")
                        self.running = False
                        break
                except json.JSONDecodeError:
                    pass
            except socket.timeout:
                pass
            except Exception as e:
                if self.running:
                    print(f"[Attacker] Listen error: {e}")
        
        sock.close()
    
    def start(self):
        """Start the attacker"""
        print(f"\n{'='*70}")
        print(f"🔴 JAMMING ATTACK SIMULATOR INITIALIZED")
        print(f"{'='*70}")
        print(f"Attacker ID: {self.attacker_id}")
        print(f"Target: {self.target_ap_ip}:{self.ap_port}")
        print(f"Duration: {self.duration} seconds")
        print(f"{'='*70}\n")
        
        print(f"⏳ Starting attack in 3 seconds...")
        time.sleep(3)
        
        self.running = True
        
        # Start listener thread
        listener_thread = threading.Thread(target=self.listen_for_isolation, daemon=True)
        listener_thread.start()
        
        # Start attack
        print(f"\n🔴 STARTING JAMMING ATTACK!\n")
        self.send_jam_packets()
        
        # Cleanup
        print(f"\n[Attacker] Attack completed")
        print(f"[Attacker] Shutting down...")
        time.sleep(2)

def main():
    parser = argparse.ArgumentParser(description='Attacker Agent - Multi-Laptop Version')
    parser.add_argument('--target-ap', required=True, help='Target AP IP address')
    parser.add_argument('--controller', required=True, help='Controller IP address')
    parser.add_argument('--channel', type=int, default=6, help='WiFi channel (default: 6)')
    parser.add_argument('--duration', type=int, default=15, help='Attack duration in seconds (default: 15)')
    
    args = parser.parse_args()
    
    try:
        attacker = AttackerAgent(args.target_ap, args.controller, args.channel, args.duration)
        attacker.start()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
