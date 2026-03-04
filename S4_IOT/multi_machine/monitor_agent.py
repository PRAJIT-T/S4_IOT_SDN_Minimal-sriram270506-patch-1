#!/usr/bin/env python3
"""
Monitor + Attacker Agent — Monitors network, then launches jamming attack.
Pure Python, no system commands. Runs on Laptop 3.

Timeline:
  0-10s:  Baseline — sends clean metrics, pings AP
  10-20s: ATTACK  — activates jammer, 100% packet loss, 8000 pps
  20s+:   Recovery — jammer off, metrics return to normal
"""

import json
import socket
import threading
import time
import random
import logging
import subprocess
import re

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [MONITOR] %(message)s')
logger = logging.getLogger(__name__)


class MonitorAgent:
    def __init__(self, config_file):
        with open(config_file) as f:
            self.config = json.load(f)

        self.controller_ip = self.config['network']['controller_ip']
        self.controller_port = self.config['network']['controller_port']
        self.monitor_ip = self.config['network']['monitor_ip']
        self.ap_ip = self.config['network']['ap_ip']

        self.jammer_pps = self.config['jammer']['packet_rate_pps']
        self.jammer_pkt_size = self.config['jammer']['packet_size_bytes']

        # Get real MAC
        self.my_mac = self._get_mac()

        self.running = True
        self.jammer_active = False
        self.packet_loss = 0
        self.start_time = time.time()

        # UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._print_banner()

    def _get_mac(self):
        """Try to get real MAC address, fallback to mock"""
        try:
            # Linux
            import glob
            for path in glob.glob('/sys/class/net/*/address'):
                iface = path.split('/')[-2]
                if iface == 'lo':
                    continue
                with open(path) as f:
                    mac = f.read().strip()
                    if mac and mac != '00:00:00:00:00:00':
                        return mac
        except Exception:
            pass
        return 'aa:bb:cc:dd:ee:ff'

    def _print_banner(self):
        logger.info("=" * 60)
        logger.info("  MONITOR + ATTACKER AGENT STARTED")
        logger.info(f"  Monitor IP (this laptop): {self.monitor_ip}")
        logger.info(f"  MAC address:              {self.my_mac}")
        logger.info(f"  Controller:               {self.controller_ip}:{self.controller_port}")
        logger.info(f"  AP (ping target):         {self.ap_ip}")
        logger.info("-" * 60)
        logger.info("  TIMELINE:")
        logger.info("    0-10s:  Baseline (clean metrics)")
        logger.info("    10-20s: JAMMING ATTACK (8000 pps UDP flood)")
        logger.info("    20s+:   Recovery (jammer off)")
        logger.info("=" * 60)

    def start(self):
        threading.Thread(target=self._metrics_loop, daemon=True).start()
        threading.Thread(target=self._attack_scheduler, daemon=True).start()
        logger.info("Monitor running. Sending metrics every 2s...\n")

    def _ping_ap(self):
        """Real ping to AP laptop. During attack → simulate 100% loss."""
        if self.jammer_active:
            self.packet_loss = 100
            return 999.0

        try:
            out = subprocess.check_output(
                ['ping', '-c', '1', '-W', '1', self.ap_ip],
                text=True, stderr=subprocess.STDOUT
            )
            m = re.search(r'time=(\d+\.?\d*)', out)
            if m:
                self.packet_loss = 0
                return float(m.group(1))
            self.packet_loss = 0
            return 5.0
        except Exception:
            self.packet_loss = 100
            return 999.0

    def _metrics_loop(self):
        count = 0
        while self.running:
            count += 1
            elapsed = time.time() - self.start_time
            latency = self._ping_ap()

            if self.jammer_active:
                throughput = round(random.uniform(0.1, 0.5), 2)
                pkt_rate = self.jammer_pps
                loss = 100
            else:
                throughput = round(random.uniform(8.5, 9.5), 2)
                pkt_rate = 0
                loss = self.packet_loss

            metrics = {
                'source': 'monitor_agent',
                'timestamp': time.time(),
                'monitor_metrics': {
                    'monitor_ip': self.monitor_ip,
                    'my_mac': self.my_mac,
                    'ping_target': self.ap_ip,
                    'ping_latency_ms': latency,
                    'packet_loss_percent': loss,
                    'local_throughput_mbps': throughput,
                    'jammer_active': self.jammer_active,
                    'jammer_packet_rate_pps': pkt_rate,
                }
            }

            try:
                self.sock.sendto(json.dumps(metrics).encode(), (self.controller_ip, self.controller_port))
            except Exception as e:
                logger.error(f"Send error: {e}")

            # Print status
            if self.jammer_active:
                logger.info(
                    f"[#{count}] t={elapsed:.0f}s | 🔴 ATTACK | "
                    f"Ping {self.ap_ip}: 100% loss — Dest Unreachable | "
                    f"Throughput: {throughput} Mbps | PktRate: {pkt_rate} pps"
                )
            else:
                logger.info(
                    f"[#{count}] t={elapsed:.0f}s | 🟢 Clean  | "
                    f"Ping {self.ap_ip}: {loss}% loss, {latency:.1f}ms | "
                    f"Throughput: {throughput} Mbps"
                )

            time.sleep(2)

    def _attack_scheduler(self):
        """Auto-schedule: attack at 10s, stop at 20s"""
        # Wait for baseline
        time.sleep(10)

        # START ATTACK
        print()
        logger.warning("🚨" * 20)
        logger.warning("  ACTIVATING JAMMING ATTACK!")
        logger.warning(f"  Source:     {self.monitor_ip} (this laptop)")
        logger.warning(f"  Target:     {self.ap_ip} (AP)")
        logger.warning(f"  Rate:       {self.jammer_pps} packets/sec")
        logger.warning(f"  Pkt size:   {self.jammer_pkt_size} bytes")
        logger.warning("🚨" * 20)
        print()

        self.jammer_active = True

        # Run jammer in separate thread
        jammer_thread = threading.Thread(target=self._jammer_flood, daemon=True)
        jammer_thread.start()

        # Let it run for 10 seconds
        time.sleep(10)

        # STOP ATTACK
        self.jammer_active = False
        print()
        logger.info("=" * 60)
        logger.info("  ✓ JAMMER DEACTIVATED — Network recovering")
        logger.info("=" * 60)
        print()

    def _jammer_flood(self):
        """UDP flood — symbolic only. Sends low-rate packets so real WiFi stays alive.
        Detection is based on reported metrics (8000 pps), not actual flood."""
        jammer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        jammer_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        payload = b'J' * 64  # small packets — symbolic only
        target = self.config['jammer'].get('target_broadcast', '255.255.255.255')
        port = self.config['jammer'].get('target_port', 12345)
        # Low real rate so WiFi stays usable; detection uses reported metric
        interval = 1.0 / 50  # 50 real pps (reported as 8000)

        sent = 0
        try:
            while self.jammer_active:
                try:
                    jammer_sock.sendto(payload, (target, port))
                    sent += 1
                    if sent % 1000 == 0:
                        logger.debug(f"Jammer: sent {sent} packets")
                    time.sleep(interval)
                except Exception:
                    time.sleep(0.001)
        finally:
            jammer_sock.close()
            logger.info(f"Jammer flood done. Total packets sent: {sent}")

    def stop(self):
        self.jammer_active = False
        self.running = False
        self.sock.close()
        logger.info("Monitor Agent stopped.")


def main():
    import sys
    cfg = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    agent = MonitorAgent(cfg)
    agent.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        agent.stop()


if __name__ == '__main__':
    main()
