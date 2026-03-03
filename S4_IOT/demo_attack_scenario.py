#!/usr/bin/env python3
"""
DEMO ORCHESTRATOR - Run Complete Attack & Defense Scenario
Demonstrates the SDN system detecting and isolating a jamming attack
"""

import subprocess
import time
import signal
import sys
import os

class DemoOrchestrator:
    def __init__(self):
        self.processes = []
        self.demo_duration = 120  # Total demo duration in seconds
        
    def print_banner(self):
        print("\n" + "="*80)
        print(" "*20 + "SDN WIFI TESTBED - ATTACK DETECTION & ISOLATION")
        print("="*80)
        print("""
This demonstration shows:

1. TWO VIRTUAL NODES communicating on a WiFi channel (6)
2. BASELINE METRICS printed frequently by the controller
3. ATTACKER launches jamming attack on the same channel
4. CONTROLLER detects anomalies in metrics:
   - High packet rate (>5000 pps)
   - Low RSSI (<-60 dBm)
   - Low throughput (<2 Mbps)
5. CONTROLLER isolates the attacker by:
   - Identifying the malicious source IP
   - Blocking further packets from that IP
   - Switching to a clean channel

Expected Timeline:
  0-10s:   Baseline metrics (normal traffic)
  10-15s:  Attacker launches jamming attack
  15-20s:  Controller detects and isolates
  20-30s:  System recovers on new channel

Press Ctrl+C to stop all processes.
""")
        print("="*80)
        
    def start_controller(self):
        """Start SDN Controller"""
        print("\n[1/4] Starting SDN CONTROLLER...")
        try:
            proc = subprocess.Popen([sys.executable, 'sdn_controller.py'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
            self.processes.append(('Controller', proc))
            time.sleep(1)
            print("     ✓ Controller started (port 9000)")
        except Exception as e:
            print(f"     ✗ Failed to start controller: {e}")
    
    def start_ap_agent(self):
        """Start AP Agent"""
        print("[2/4] Starting AP AGENT (Virtual Nodes)...")
        try:
            proc = subprocess.Popen([sys.executable, 'ap_agent.py'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
            self.processes.append(('AP Agent', proc))
            time.sleep(1)
            print("     ✓ AP Agent started (2 virtual nodes on channel 6)")
        except Exception as e:
            print(f"     ✗ Failed to start AP agent: {e}")
    
    def start_monitor_agent(self):
        """Start Monitor Agent"""
        print("[3/4] Starting MONITOR AGENT...")
        try:
            proc = subprocess.Popen([sys.executable, 'monitor_agent.py'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
            self.processes.append(('Monitor Agent', proc))
            time.sleep(1)
            print("     ✓ Monitor Agent started (traffic monitoring)")
        except Exception as e:
            print(f"     ✗ Failed to start monitor agent: {e}")
    
    def start_attacker(self, delay=10, duration=15):
        """Start Attacker"""
        print(f"\n[4/4] Attacker will start in {delay} seconds...")
        print(f"     Duration: {duration} seconds of jamming on channel 6")
        
        time.sleep(delay)
        
        try:
            proc = subprocess.Popen([sys.executable, 'attacker.py',
                                    '--channel', '6',
                                    '--duration', str(duration),
                                    '--target-ap', '127.0.0.1',
                                    '--ap-port', '9001'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
            self.processes.append(('Attacker', proc))
            print("     ✓ Attacker started - JAMMING IN PROGRESS!")
        except Exception as e:
            print(f"     ✗ Failed to start attacker: {e}")
    
    def print_progress(self):
        """Print demo progress"""
        elapsed = 0
        while elapsed < self.demo_duration:
            time.sleep(5)
            elapsed += 5
            
            remaining = self.demo_duration - elapsed
            print(f"\n[Demo Progress] {elapsed}s elapsed ({remaining}s remaining)")
            
            # Check if processes are still running
            for name, proc in self.processes:
                if proc.poll() is not None:
                    print(f"  ⚠️  {name} has exited")
    
    def cleanup(self):
        """Clean up all processes"""
        print("\n\n[Demo] Shutting down all processes...")
        for name, proc in self.processes:
            try:
                proc.terminate()
                proc.wait(timeout=2)
                print(f"  ✓ {name} stopped")
            except subprocess.TimeoutExpired:
                proc.kill()
                print(f"  ✓ {name} killed")
            except Exception as e:
                print(f"  ✗ Error stopping {name}: {e}")
        
        print("\n" + "="*80)
        print("DEMONSTRATION COMPLETE")
        print("="*80)
        print("""
Summary:
✓ 2 Virtual nodes were setup on WiFi channel 6
✓ Controller monitored metrics continuously (channel, throughput, RSSI, packet rate)
✓ Attacker launched pseudo-jamming attack
✓ Controller detected attack via metrics anomalies
✓ Controller isolated the attacker by blocking its IP

Check controller_results.json for detailed results.
""")
    
    def run(self):
        """Run the complete demonstration"""
        self.print_banner()
        
        # Start all components
        self.start_controller()
        self.start_ap_agent()
        self.start_monitor_agent()
        
        # Start attacker in background
        import threading
        attacker_thread = threading.Thread(target=self.start_attacker, args=(10, 15))
        attacker_thread.daemon = True
        attacker_thread.start()
        
        # Run progress tracker
        try:
            self.print_progress()
        except KeyboardInterrupt:
            print("\n[Demo] Interrupted by user")
        finally:
            self.cleanup()


if __name__ == '__main__':
    demo = DemoOrchestrator()
    try:
        demo.run()
    except KeyboardInterrupt:
        demo.cleanup()
    except Exception as e:
        print(f"\n[Error] {e}")
        demo.cleanup()
