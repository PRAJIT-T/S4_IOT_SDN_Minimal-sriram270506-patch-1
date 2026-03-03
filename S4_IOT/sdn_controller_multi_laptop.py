#!/usr/bin/env python3
"""
MULTI-LAPTOP VERSION - sdn_controller.py
Listen on all interfaces for remote connections
"""

import socket
import json
import time
import threading
import argparse
from datetime import datetime
from collections import defaultdict, deque

class SDNController:
    def __init__(self, host='0.0.0.0', port=9000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        
        # Metrics tracking per channel
        self.metrics_by_channel = defaultdict(lambda: {
            "throughput": deque(maxlen=10),
            "rssi": deque(maxlen=10),
            "loss": deque(maxlen=10),
            "packet_rate": deque(maxlen=10),
            "timestamps": deque(maxlen=10)
        })
        
        self.current_metrics = defaultdict(lambda: {"throughput": 0, "rssi": -50, "loss": 0})
        self.jammer_detected = False
        self.current_channel = 6
        self.detection_time = None
        self.all_metrics = []
        
        # Attack tracking
        self.detected_attackers = {}
        self.isolated_ips = set()
        
        print("\n" + "="*70)
        print("SDN CONTROLLER - MULTI-LAPTOP VERSION")
        print("="*70)
        print(f"Listening on {self.host}:{self.port}")
        print(f"Ready for remote connections from:")
        print(f"  - AP Agent")
        print(f"  - Monitor Agent")
        print("="*70 + "\n")
        
    def receive_metrics(self):
        """Receive metrics from AP and Monitor agents"""
        while True:
            try:
                data, addr = self.server_socket.recvfrom(4096)
                message = json.loads(data.decode())
                
                msg_type = message.get('type')
                timestamp = message.get('timestamp')
                channel = 6
                
                if msg_type == 'ap_metrics':
                    data_payload = message.get('data', {})
                    self.current_metrics['ap'] = data_payload
                    channel = data_payload.get('channel', 6)
                    
                    self.metrics_by_channel[channel]['throughput'].append(data_payload.get('throughput', 0))
                    self.metrics_by_channel[channel]['rssi'].append(data_payload.get('rssi', -50))
                    self.metrics_by_channel[channel]['loss'].append(data_payload.get('loss', 0))
                    self.metrics_by_channel[channel]['timestamps'].append(timestamp)
                    
                elif msg_type == 'monitor_metrics':
                    data_payload = message.get('data', {})
                    self.current_metrics['monitor'] = data_payload
                    self.metrics_by_channel[channel]['packet_rate'].append(data_payload.get('packet_rate', 0))
                
                elif msg_type == 'jam_packet':
                    attacker_id = message.get('attacker_id')
                    jam_channel = message.get('channel', 6)
                    self.report_jamming_packet(attacker_id, jam_channel, addr[0])
                
                self.all_metrics.append({
                    'time': timestamp,
                    'type': msg_type,
                    'source_ip': addr[0],
                    'data': message.get('data', {})
                })
                
            except json.JSONDecodeError:
                pass
            except Exception as e:
                pass
    
    def report_jamming_packet(self, attacker_id, channel, source_ip):
        """Report detection of jamming packet"""
        if attacker_id not in self.detected_attackers:
            self.detected_attackers[attacker_id] = {
                'channel': channel,
                'source_ip': source_ip,
                'first_detected': datetime.now(),
                'packet_count': 1
            }
            print(f"\n[Controller] 🔴 JAM PACKET DETECTED!")
            print(f"  Attacker ID: {attacker_id}")
            print(f"  Channel: {channel}")
            print(f"  Source IP: {source_ip}")
        else:
            self.detected_attackers[attacker_id]['packet_count'] += 1
    
    def analyze_and_decide(self):
        """Analyze metrics and make decisions"""
        while True:
            time.sleep(2)
            self.detect_jamming_attack()
            self.isolate_attackers()
    
    def detect_jamming_attack(self):
        """Detect jamming attacks based on channel metrics"""
        for channel, metrics in self.metrics_by_channel.items():
            if not metrics['throughput'] or not metrics['packet_rate']:
                continue
            
            avg_throughput = sum(metrics['throughput']) / len(metrics['throughput'])
            avg_rssi = sum(metrics['rssi']) / len(metrics['rssi'])
            avg_packet_rate = sum(metrics['packet_rate']) / len(metrics['packet_rate']) if metrics['packet_rate'] else 0
            
            if (avg_packet_rate > 5000 and avg_rssi < -60 and avg_throughput < 2.0):
                if not self.jammer_detected:
                    self.jammer_detected = True
                    self.detection_time = datetime.now()
                    
                    print(f"\n[Controller] 🚨 JAMMING ATTACK DETECTED ON CHANNEL {channel}!")
                    print(f"  Throughput: {avg_throughput:.2f} Mbps")
                    print(f"  RSSI: {avg_rssi:.0f} dBm")
                    print(f"  Packet Rate: {avg_packet_rate:.0f} pps")
                    
                    if channel == 6:
                        print(f"  Decision: Switch from Channel 6 → Channel 11")
                        self.send_action('ap_agent', {'action': 'switch_channel', 'new_channel': 11})
                        self.current_channel = 11
    
    def isolate_attackers(self):
        """Isolate detected attackers"""
        for attacker_id, info in list(self.detected_attackers.items()):
            source_ip = info['source_ip']
            packet_count = info['packet_count']
            time_detected = (datetime.now() - info['first_detected']).total_seconds()
            
            if packet_count > 5 or time_detected > 5:
                if source_ip not in self.isolated_ips:
                    self.isolated_ips.add(source_ip)
                    
                    print(f"\n[Controller] 🔒 ISOLATING ATTACKER!")
                    print(f"  Attacker ID: {attacker_id}")
                    print(f"  Source IP: {source_ip}")
                    print(f"  Packets Sent: {packet_count}")
                    print(f"  Time Active: {time_detected:.1f}s")
                    print(f"  Action: BLOCKING IP {source_ip}")
                    
                    self.send_isolation_notice(attacker_id, source_ip)
                    self.send_action('ap_agent', {
                        'action': 'block_ip',
                        'target_ip': source_ip,
                        'reason': 'Jamming attack detected'
                    })
    
    def send_action(self, target, action):
        """Send action to AP agent"""
        try:
            message = json.dumps({
                'type': 'controller_action',
                'timestamp': time.time(),
                'action': action
            })
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message.encode(), ('127.0.0.1', 9001))
            sock.close()
        except:
            pass
    
    def send_isolation_notice(self, attacker_id, source_ip):
        """Send isolation notice to attacker"""
        try:
            message = json.dumps({
                'type': 'isolation_notice',
                'attacker_id': attacker_id,
                'isolated_ip': source_ip,
                'reason': 'Jamming attack detected and isolated',
                'timestamp': time.time()
            })
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message.encode(), ('127.0.0.1', 9003))
            sock.close()
        except:
            pass
    
    def print_channel_metrics(self):
        """Print metrics for current channel frequently"""
        print_count = 0
        while True:
            time.sleep(5)
            print_count += 1
            
            if self.current_metrics['ap'] and self.current_metrics['monitor']:
                ap = self.current_metrics['ap']
                mon = self.current_metrics['monitor']
                channel = ap.get('channel', 6)
                
                print(f"\n{'='*70}")
                print(f"[CHANNEL {channel} METRICS] - Update #{print_count}")
                print(f"{'='*70}")
                print(f"  Throughput:     {ap.get('throughput', 0):6.2f} Mbps")
                print(f"  RSSI:           {ap.get('rssi', -50):6.0f} dBm")
                print(f"  Packet Loss:    {ap.get('loss', 0):6.1f}%")
                print(f"  Packet Rate:    {mon.get('packet_rate', 0):6.0f} pps")
                print(f"  Phase:          {ap.get('phase', 'unknown')}")
                print(f"  Jammer Status:  {'DETECTED ⚠️' if self.jammer_detected else 'Clean ✓'}")
                
                if self.detected_attackers:
                    print(f"\n  Detected Attackers:")
                    for attacker_id, info in self.detected_attackers.items():
                        print(f"    - {attacker_id} (packets: {info['packet_count']})")
                
                if self.isolated_ips:
                    print(f"\n  Isolated IPs:")
                    for ip in self.isolated_ips:
                        print(f"    - {ip} 🔒")
                
                print(f"{'='*70}")
    
    def run(self):
        """Start controller"""
        threading.Thread(target=self.receive_metrics, daemon=True).start()
        threading.Thread(target=self.analyze_and_decide, daemon=True).start()
        threading.Thread(target=self.print_channel_metrics, daemon=True).start()
        
        print("\n[Controller] Waiting for agent connections...\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.save_results()
            print("\n[Controller] Shutting down...")
    
    def save_results(self):
        """Save experiment results"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "system": "SDN WiFi Testbed with Attack Detection",
            "jammer_detected": self.jammer_detected,
            "detection_time": self.detection_time.isoformat() if self.detection_time else None,
            "channels_monitored": [2, 6, 11],
            "current_channel": self.current_channel,
            "detected_attackers": list(self.detected_attackers.keys()),
            "isolated_ips": list(self.isolated_ips),
            "metrics_count": len(self.all_metrics)
        }
        
        with open('controller_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"[Controller] Results saved to controller_results.json")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SDN Controller - Multi-Laptop Version')
    parser.add_argument('--host', default='0.0.0.0', help='Host to listen on (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=9000, help='Port to listen on (default: 9000)')
    
    args = parser.parse_args()
    
    controller = SDNController(host=args.host, port=args.port)
    controller.run()
