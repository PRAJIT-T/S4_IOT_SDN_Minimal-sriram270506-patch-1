#!/usr/bin/env python3
"""
AP Agent — Simulates a WiFi Access Point with 2 connected nodes.
Pure Python, no hostapd, no system commands. Just UDP to controller.
Runs on Laptop 2.
"""

import json
import socket
import threading
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [AP_AGENT] %(message)s')
logger = logging.getLogger(__name__)


class APAgent:
    def __init__(self, config_file):
        with open(config_file) as f:
            self.config = json.load(f)

        self.controller_ip = self.config['network']['controller_ip']
        self.controller_port = self.config['network']['controller_port']
        self.ap_ip = self.config['network']['ap_ip']
        self.command_port = 9001
        self.current_channel = self.config['wifi'].get('ap_channel_initial', 6)

        # 2 simulated WiFi nodes
        self.nodes = {
            'Node-1': {'mac': 'aa:11:22:33:44:01', 'ip': '192.168.88.11', 'rssi': -52},
            'Node-2': {'mac': 'aa:11:22:33:44:02', 'ip': '192.168.88.12', 'rssi': -56},
        }

        self.blacklisted = []
        self.attack_degraded = False
        self.running = True

        # UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.command_port))
        self.sock.setblocking(False)

        self._print_banner()

    def _print_banner(self):
        logger.info("=" * 60)
        logger.info("  AP AGENT STARTED")
        logger.info(f"  AP IP (this laptop):   {self.ap_ip}")
        logger.info(f"  Listening for cmds on: 0.0.0.0:{self.command_port}")
        logger.info(f"  Controller:            {self.controller_ip}:{self.controller_port}")
        logger.info(f"  Channel:               {self.current_channel}")
        logger.info(f"  SSID:                  SDN-TestNet")
        logger.info("-" * 60)
        logger.info("  SIMULATED NODES:")
        for name, n in self.nodes.items():
            logger.info(f"    {name}:  MAC={n['mac']}  IP={n['ip']}  RSSI={n['rssi']} dBm")
        logger.info("=" * 60)

    def start(self):
        threading.Thread(target=self._metrics_sender, daemon=True).start()
        threading.Thread(target=self._command_listener, daemon=True).start()
        logger.info("Sending metrics to controller every 2s...\n")

    def _metrics_sender(self):
        count = 0
        while self.running:
            count += 1

            rssi_per_client = {}
            for n in self.nodes.values():
                base = n['rssi']
                if self.attack_degraded:
                    rssi_per_client[n['mac']] = base - random.randint(12, 20)
                else:
                    rssi_per_client[n['mac']] = base + random.randint(-2, 2)

            chan_util = random.randint(85, 98) if self.attack_degraded else random.randint(15, 35)

            metrics = {
                'source': 'ap_agent',
                'timestamp': time.time(),
                'ap_metrics': {
                    'ap_ip': self.ap_ip,
                    'channel': self.current_channel,
                    'ssid': 'SDN-TestNet',
                    'num_clients': len(self.nodes),
                    'connected_clients': [n['mac'] for n in self.nodes.values()],
                    'rssi_per_client': rssi_per_client,
                    'channel_utilization_percent': chan_util,
                    'tx_power': 20,
                    'bandwidth': '20MHz',
                    'blacklisted': self.blacklisted,
                }
            }

            try:
                self.sock.sendto(json.dumps(metrics).encode(), (self.controller_ip, self.controller_port))
            except Exception as e:
                logger.error(f"Send error: {e}")

            avg_rssi = sum(rssi_per_client.values()) / len(rssi_per_client)
            status = "⚠️ DEGRADED" if self.attack_degraded else "✅ Normal"
            logger.info(
                f"[#{count}] CH={self.current_channel}  Nodes={len(self.nodes)}  "
                f"RSSI={avg_rssi:.0f}dBm  ChanUtil={chan_util}%  "
                f"Blacklisted={len(self.blacklisted)}  [{status}]"
            )
            time.sleep(2)

    def _command_listener(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                cmd = json.loads(data.decode())
                cmd_type = cmd.get('command')

                if cmd_type == 'blacklist_mac':
                    mac = cmd.get('target_mac', '??')
                    self.blacklisted.append(mac)
                    print()
                    logger.info("🔒" + "=" * 58)
                    logger.info(f"  CONTROLLER COMMAND: BLACKLIST MAC")
                    logger.info(f"  Blocked MAC:  {mac}")
                    logger.info(f"  Reason:       {cmd.get('reason', 'jammer')}")
                    logger.info(f"  All blocked:  {self.blacklisted}")
                    logger.info("🔒" + "=" * 58)
                    print()

                elif cmd_type == 'switch_channel':
                    old = self.current_channel
                    new = cmd.get('target_channel', 11)
                    self.current_channel = new
                    self.attack_degraded = False
                    print()
                    logger.info("📡" + "=" * 58)
                    logger.info(f"  CONTROLLER COMMAND: CHANNEL SWITCH")
                    logger.info(f"  Channel:  {old} → {new}")
                    logger.info(f"  Reason:   {cmd.get('reason', 'escape jammer')}")
                    logger.info(f"  Nodes reconnecting on CH {new}...")
                    logger.info("📡" + "=" * 58)
                    print()

                elif cmd_type == 'attack_notify':
                    self.attack_degraded = True
                    logger.warning("⚠️  Attack notification — degrading metrics")

            except BlockingIOError:
                pass
            except Exception:
                pass
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.sock.close()
        logger.info("AP Agent stopped.")


def main():
    import sys
    cfg = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    agent = APAgent(cfg)
    agent.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        agent.stop()


if __name__ == '__main__':
    main()
