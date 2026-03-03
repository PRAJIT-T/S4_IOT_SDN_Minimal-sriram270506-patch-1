#!/usr/bin/env python3
"""
SDN Controller - Laptop 1
Monitors network metrics, detects jamming attacks, makes decisions
Tracks metrics by channel and isolates malicious nodes
"""

import socket
import json
import time
import threading
from datetime import datetime
from collections import defaultdict, deque

class SDNController:
    def __init__(self, host='127.0.0.1', port=9000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
        self.detected_attackers = {}  # {attacker_id: {info}}
        self.isolated_ips = set()
        
        # Multi-AP support
        self.registered_aps = {}  # {ap_ip: {info}}
        self.ap_ports = {9001, 9004, 9005, 9006}  # AP listening ports for multi-laptop setup
        
        print("\n" + "="*70)
        print("SDN CONTROLLER - CHANNEL MONITORING & ATTACK ISOLATION")
        print("="*70)
        print(f"Listening on {self.host}:{self.port}")
        print(f"Monitoring channels: 2, 6, 11")
        print(f"Supporting Multi-AP Deployment")
        print("="*70)
        
    def receive_metrics(self):
        """Receive metrics from AP, Monitor agents, and detect attack packets"""
        while True:
            try:
                data, addr = self.server_socket.recvfrom(4096)
                message = json.loads(data.decode())
                
                msg_type = message.get('type')
                timestamp = message.get('timestamp')
                channel = 6  # Default channel
                
                if msg_type == 'ap_metrics':
                    ap_ip = message.get('ap_ip', addr[0])
                    data_payload = message.get('data', {})
                    self.current_metrics['ap'] = data_payload
                    channel = data_payload.get('channel', 6)
                    
                    # Register AP if not already known
                    if ap_ip not in self.registered_aps:
                        self.registered_aps[ap_ip] = {
                            'first_seen': timestamp,
                            'last_seen': timestamp,
                            'port': 9001,
                            'status': 'online'
                        }
                        print(f"\n[Controller] 📡 NEW AP REGISTERED: {ap_ip}")
                    else:
                        self.registered_aps[ap_ip]['last_seen'] = timestamp
                    
                    # Store metrics by channel
                    self.metrics_by_channel[channel]['throughput'].append(data_payload.get('throughput', 0))
                    self.metrics_by_channel[channel]['rssi'].append(data_payload.get('rssi', -50))
                    self.metrics_by_channel[channel]['loss'].append(data_payload.get('loss', 0))
                    self.metrics_by_channel[channel]['timestamps'].append(timestamp)
                    
                elif msg_type == 'monitor_metrics':
                    monitor_ip = message.get('monitor_ip', addr[0])
                    data_payload = message.get('data', {})
                    self.current_metrics['monitor'] = data_payload
                    
                    # Register Monitor if first time
                    if not hasattr(self, '_monitor_registered') or monitor_ip not in self._monitor_registered:
                        if not hasattr(self, '_monitor_registered'):
                            self._monitor_registered = set()
                        self._monitor_registered.add(monitor_ip)
                        print(f"\n[Controller] 📡 MONITOR CONNECTED: {monitor_ip}")
                    
                    # Store packet rate by channel
                    self.metrics_by_channel[channel]['packet_rate'].append(data_payload.get('packet_rate', 0))
                
                elif msg_type == 'attack_report':
                    # Monitor detected attack
                    attack_id = message.get('attack_id')
                    monitor_ip = message.get('monitor_ip', addr[0])
                    pps = message.get('packet_rate', 0)
                    print(f"\n[Controller] 🚨 ATTACK ALERT FROM MONITOR!")
                    print(f"[Controller] Attack ID: {attack_id}")
                    print(f"[Controller] Monitor IP: {monitor_ip}")
                    print(f"[Controller] Packet Rate: {pps:.0f} pps")
                    
                elif msg_type == 'jam_packet':
                    # Detected jamming packet
                    attacker_id = message.get('attacker_id')
                    jam_channel = message.get('channel', 6)
                    self.report_jamming_packet(attacker_id, jam_channel, addr[0])
                
                # Store for analysis
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
            time.sleep(2)  # Check every 2 seconds
            
            # Check for attacks
            self.detect_jamming_attack()
            
            # Isolate malicious nodes
            self.isolate_attackers()
    
    def detect_jamming_attack(self):
        """Detect jamming attacks based on channel metrics"""
        for channel, metrics in self.metrics_by_channel.items():
            if not metrics['throughput'] or not metrics['packet_rate']:
                continue
            
            # Calculate averages
            avg_throughput = sum(metrics['throughput']) / len(metrics['throughput'])
            avg_rssi = sum(metrics['rssi']) / len(metrics['rssi'])
            avg_packet_rate = sum(metrics['packet_rate']) / len(metrics['packet_rate']) if metrics['packet_rate'] else 0
            
            # Detection criteria
            if (avg_packet_rate > 5000 and avg_rssi < -60 and avg_throughput < 2.0):
                if not self.jammer_detected:
                    self.jammer_detected = True
                    self.detection_time = datetime.now()
                    
                    # Collect attacker IPs for display
                    attacker_ips = [info['source_ip'] for info in self.detected_attackers.values()]
                    attacker_ip_str = ', '.join(attacker_ips) if attacker_ips else 'Unknown'
                    
                    print(f"\n[Controller] 🚨 JAMMING ATTACK DETECTED ON CHANNEL {channel}!")
                    print(f"  Attacker IP(s): {attacker_ip_str}")
                    print(f"  Throughput: {avg_throughput:.2f} Mbps")
                    print(f"  RSSI: {avg_rssi:.0f} dBm")
                    print(f"  Packet Rate: {avg_packet_rate:.0f} pps")
                    
                    if channel == 6:
                        new_ch = 11
                    elif channel == 11:
                        new_ch = 2
                    else:
                        new_ch = 6
                    
                    reason = f'Jamming attack from {attacker_ip_str} on Ch {channel}'
                    print(f"  Decision: Switch from Channel {channel} → Channel {new_ch}")
                    print(f"  📢 Broadcasting channel switch to ALL APs...")
                    self.broadcast_to_all_aps({'action': 'switch_channel', 'new_channel': new_ch, 'reason': reason})
                    self.current_channel = new_ch
    
    def isolate_attackers(self):
        """Isolate detected attackers"""
        for attacker_id, info in list(self.detected_attackers.items()):
            source_ip = info['source_ip']
            packet_count = info['packet_count']
            time_detected = (datetime.now() - info['first_detected']).total_seconds()
            
            # Isolation threshold: more than 5 jam packets or detected for >5 seconds
            if packet_count > 5 or time_detected > 5:
                if source_ip not in self.isolated_ips:
                    self.isolated_ips.add(source_ip)
                    
                    print(f"\n[Controller] 🔒 ISOLATING ATTACKER!")
                    print(f"  Attacker ID: {attacker_id}")
                    print(f"  🔴 Real Attacker IP: {source_ip}")
                    print(f"  Packets Sent: {packet_count}")
                    print(f"  Time Active: {time_detected:.1f}s")
                    print(f"  Action: BLOCKING IP {source_ip}")
                    print(f"  📢 Notifying ALL AP nodes to block {source_ip}...")
                    
                    # Send isolation notice to attacker's REAL IP
                    self.send_isolation_notice(attacker_id, source_ip)
                    
                    # Broadcast block rule to ALL registered APs
                    self.broadcast_to_all_aps({
                        'action': 'block_ip',
                        'target_ip': source_ip,
                        'reason': f'Attacker {source_ip} detected - Jamming attack isolated'
                    })
    
    def broadcast_to_all_aps(self, action):
        """Broadcast action to ALL registered AP agents"""
        message = json.dumps({
            'type': 'controller_action',
            'timestamp': time.time(),
            'action': action
        }).encode()
        
        # Send to every registered AP
        for ap_ip, ap_info in self.registered_aps.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(message, (ap_ip, ap_info.get('port', 9001)))
                sock.close()
                print(f"  → Sent to AP {ap_ip}")
            except Exception as e:
                print(f"  → Failed to send to AP {ap_ip}: {e}")
        
        # Also send to localhost:9001 as fallback for single-laptop testing
        if not self.registered_aps:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(message, ('127.0.0.1', 9001))
                sock.close()
            except:
                pass
    
    def send_isolation_notice(self, attacker_id, source_ip):
        """Send isolation notice to attacker's real IP"""
        try:
            message = json.dumps({
                'type': 'isolation_notice',
                'attacker_id': attacker_id,
                'isolated_ip': source_ip,
                'reason': f'Jamming attack detected - Your IP {source_ip} has been isolated',
                'timestamp': time.time()
            })
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Send to attacker's real IP on port 9003
            sock.sendto(message.encode(), (source_ip, 9003))
            sock.close()
            print(f"  → Isolation notice sent to attacker at {source_ip}:9003")
        except Exception as e:
            # Fallback to localhost for single-laptop testing
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(message.encode(), ('127.0.0.1', 9003))
                sock.close()
            except:
                pass
    
    def print_channel_metrics(self):
        """Print metrics for current channel frequently"""
        print_count = 0
        while True:
            time.sleep(5)  # Print every 5 seconds
            
            print_count += 1
            
            if self.current_metrics['ap'] and self.current_metrics['monitor']:
                ap = self.current_metrics['ap']
                mon = self.current_metrics['monitor']
                channel = ap.get('channel', 6)
                
                print(f"\n{'='*70}")
                print(f"[CHANNEL {channel} METRICS] - Update #{print_count}")
                print(f"{'='*70}")
                
                # Show connected APs
                if self.registered_aps:
                    print(f"  Connected APs:")
                    for ap_ip in self.registered_aps:
                        print(f"    📡 {ap_ip}")
                
                # Show connected monitors
                if hasattr(self, '_monitor_registered') and self._monitor_registered:
                    print(f"  Connected Monitors:")
                    for m_ip in self._monitor_registered:
                        print(f"    📡 {m_ip}")
                
                print(f"  Throughput:     {ap.get('throughput', 0):6.2f} Mbps")
                print(f"  RSSI:           {ap.get('rssi', -50):6.0f} dBm")
                print(f"  Packet Loss:    {ap.get('loss', 0):6.1f}%")
                print(f"  Packet Rate:    {mon.get('packet_rate', 0):6.0f} pps")
                print(f"  Phase:          {ap.get('phase', 'unknown')}")
                print(f"  Jammer Status:  {'DETECTED ⚠️' if self.jammer_detected else 'Clean ✓'}")
                
                if self.detected_attackers:
                    print(f"\n  Detected Attackers:")
                    for attacker_id, info in self.detected_attackers.items():
                        print(f"    🔴 {attacker_id} | IP: {info['source_ip']} | packets: {info['packet_count']}")
                
                if self.isolated_ips:
                    print(f"\n  Isolated/Blocked IPs:")
                    for ip in self.isolated_ips:
                        print(f"    🔒 {ip} BLOCKED")
                
                print(f"{'='*70}")
    
    def run(self):
        """Start controller"""
        threading.Thread(target=self.receive_metrics, daemon=True).start()
        threading.Thread(target=self.analyze_and_decide, daemon=True).start()
        threading.Thread(target=self.print_channel_metrics, daemon=True).start()
        
        print("\n[Controller] Waiting for agent connections...\n")
        
        # Keep running
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
    controller = SDNController()
    controller.run()
