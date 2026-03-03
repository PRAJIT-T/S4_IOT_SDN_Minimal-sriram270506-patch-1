#!/usr/bin/env python3
"""
ATTACKER - Pseudo Jamming Simulation
Simulates a malicious attacker that floods the WiFi AP with jamming packets
on specific channels to disrupt legitimate traffic.

This represents an attacker with:
- Malicious intent to jam WiFi
- Knowledge of target channel
- Ability to flood packets
"""

import socket
import json
import time
import random
import threading
import argparse
from datetime import datetime

class Attacker:
    def __init__(self, target_ap_ip='127.0.0.1', target_ap_port=9001, 
                 controller_ip='127.0.0.1', controller_port=9000,
                 attack_channel=6, attack_duration=30, attacker_ip='127.0.0.1'):
        """
        Initialize attacker
        
        Args:
            target_ap_ip: IP of target WiFi AP
            target_ap_port: Port of target AP
            controller_ip: IP of SDN Controller (to receive commands)
            controller_port: Port of SDN Controller
            attack_channel: WiFi channel to jam (2-6 or 6-11 range)
            attack_duration: How long to jam in seconds
            attacker_ip: IP address of attacker
        """
        self.target_ap_ip = target_ap_ip
        self.target_ap_port = target_ap_port
        self.controller_ip = controller_ip
        self.controller_port = controller_port
        self.attack_channel = attack_channel
        self.attack_duration = attack_duration
        self.attacker_ip = attacker_ip
        
        self.is_attacking = False
        self.attacker_id = f"ATTACKER_{random.randint(1000, 9999)}"
        self.packets_sent = 0
        self.start_time = None
        self.detected = False
        self.isolated = False
        
        # Socket for listening to controller
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.bind(('0.0.0.0', 9003))
        self.listen_socket.settimeout(2)
        
        print("\n" + "="*70)
        print("ATTACKER - JAMMING SIMULATION")
        print("="*70)
        print(f"🔴 Attacker ID: {self.attacker_id}")
        print(f"🔴 Attacker IP: {self.attacker_ip}")
        print(f"Target AP: {self.target_ap_ip}:{self.target_ap_port}")
        print(f"Target Channel: {self.attack_channel}")
        print(f"Attack Duration: {self.attack_duration} seconds")
        print("="*70)
        
    def generate_jam_packets(self):
        """Generate malicious jamming packets"""
        jam_packets = []
        for i in range(100):  # Generate 100 fake packets per batch
            packet = {
                'type': 'jam_packet',
                'attacker_id': self.attacker_id,
                'sequence': i,
                'timestamp': time.time(),
                'channel': self.attack_channel,
                'power': random.randint(10, 30),  # Fake power levels
                'noise': random.uniform(-90, -70)
            }
            jam_packets.append(packet)
        return jam_packets
    
    def jam_channel(self):
        """Send jamming packets to target AP"""
        print(f"\n[{self.attacker_id}] 🔴 STARTING JAMMING ATTACK!")
        print(f"[{self.attacker_id}] 🔴 Real Attacker IP: {self.attacker_ip}")
        print(f"[{self.attacker_id}] Target Channel: {self.attack_channel}")
        print(f"[{self.attacker_id}] Flooding {self.target_ap_ip}:{self.target_ap_port}...")
        
        self.is_attacking = True
        self.start_time = time.time()
        self.packets_sent = 0
        
        while self.is_attacking:
            try:
                elapsed = time.time() - self.start_time
                
                # Generate and send jam packets
                jam_packets = self.generate_jam_packets()
                
                for packet in jam_packets:
                    if not self.is_attacking:
                        break
                    
                    # Send to AP (simulating jamming)
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.settimeout(1)
                        message = json.dumps(packet)
                        sock.sendto(message.encode(), (self.target_ap_ip, self.target_ap_port))
                        sock.close()
                        self.packets_sent += 1
                    except:
                        pass
                    
                    # Check for isolation signal
                    self.check_for_isolation()
                
                # Print attack status every 2 seconds
                if int(elapsed) % 2 == 0:
                    pps = self.packets_sent / max(1, elapsed)
                    status = "🔴 ATTACKING" if not self.isolated else "🔒 ISOLATED"
                    print(f"[{self.attacker_id}] {status} | Time: {elapsed:.1f}s | Packets: {self.packets_sent} | Rate: {pps:.0f} pps")
                
                # Check if attack duration exceeded
                if elapsed >= self.attack_duration:
                    self.is_attacking = False
                    print(f"\n[{self.attacker_id}] ⏱️  Attack duration ({self.attack_duration}s) reached. Stopping...")
                
                time.sleep(0.01)  # 100 packets per batch per 10ms = 10k pps
                
            except KeyboardInterrupt:
                print(f"\n[{self.attacker_id}] Attack interrupted by user")
                self.is_attacking = False
                break
            except Exception as e:
                print(f"[{self.attacker_id}] Error during jamming: {e}")
                time.sleep(0.1)
    
    def check_for_isolation(self):
        """Check if controller has isolated this attacker"""
        try:
            data, addr = self.listen_socket.recvfrom(4096)
            message = json.loads(data.decode())
            
            if message.get('type') == 'isolation_notice':
                isolated_id = message.get('attacker_id')
                if isolated_id == self.attacker_id:
                    self.isolated = True
                    self.is_attacking = False
                    print(f"\n[{self.attacker_id}] 🚨 DETECTED AND ISOLATED BY CONTROLLER!")
                    print(f"[{self.attacker_id}] 🚨 My Real IP Detected: {self.attacker_ip}")
                    print(f"[{self.attacker_id}] Reason: {message.get('reason')}")
                    print(f"[{self.attacker_id}] 🔒 ISOLATION IN PROGRESS...")
                    print(f"[{self.attacker_id}] Stopping attack...")
                    return True
        except socket.timeout:
            pass
        except:
            pass
        
        return False
    
    def send_attack_notification(self):
        """Send notification about attack to controller"""
        message = json.dumps({
            'type': 'attack_notification',
            'attacker_id': self.attacker_id,
            'channel': self.attack_channel,
            'packets_sent': self.packets_sent,
            'timestamp': datetime.now().isoformat()
        })
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message.encode(), (self.controller_ip, self.controller_port))
            sock.close()
        except:
            pass
    
    def start_attack(self):
        """Start the jamming attack"""
        # Start jamming in a separate thread
        attack_thread = threading.Thread(target=self.jam_channel, daemon=True)
        attack_thread.start()
        
        # Start listening for isolation commands
        listen_thread = threading.Thread(target=self.listen_for_commands, daemon=True)
        listen_thread.start()
        
        # Wait for attack to complete
        attack_thread.join()
        
        print(f"\n[{self.attacker_id}] Attack completed!")
        print(f"[{self.attacker_id}] Total packets sent: {self.packets_sent}")
        print(f"[{self.attacker_id}] Detected: {self.detected}")
        print(f"[{self.attacker_id}] Isolated: {self.isolated}")
    
    def listen_for_commands(self):
        """Listen for commands from controller"""
        while self.is_attacking:
            try:
                self.check_for_isolation()
                time.sleep(0.5)
            except:
                pass


def main():
    parser = argparse.ArgumentParser(description='WiFi Jammer - Pseudo Jamming Simulation')
    parser.add_argument('--target-ap', default='127.0.0.1', help='Target AP IP (default: 127.0.0.1)')
    parser.add_argument('--ap-port', type=int, default=9001, help='Target AP port (default: 9001)')
    parser.add_argument('--controller', default='127.0.0.1', help='Controller IP (default: 127.0.0.1)')
    parser.add_argument('--controller-port', type=int, default=9000, help='Controller port (default: 9000)')
    parser.add_argument('--channel', type=int, default=6, help='WiFi channel to jam (default: 6)')
    parser.add_argument('--duration', type=int, default=30, help='Attack duration in seconds (default: 30)')
    parser.add_argument('--delay', type=int, default=0, help='Delay before starting attack in seconds (default: 0)')
    parser.add_argument('--attacker-ip', default='127.0.0.1', help='Attacker IP address (default: 127.0.0.1)')
    
    args = parser.parse_args()
    
    # Wait before starting if delay specified
    if args.delay > 0:
        print(f"⏰ Waiting {args.delay} seconds before attack...")
        time.sleep(args.delay)
    
    # Create and start attacker
    attacker = Attacker(
        target_ap_ip=args.target_ap,
        target_ap_port=args.ap_port,
        controller_ip=args.controller,
        controller_port=args.controller_port,
        attack_channel=args.channel,
        attack_duration=args.duration,
        attacker_ip=args.attacker_ip
    )
    
    attacker.start_attack()


if __name__ == '__main__':
    main()
