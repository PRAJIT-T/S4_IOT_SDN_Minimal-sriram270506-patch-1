#!/usr/bin/env python3
"""
SDN Controller — The brain. Receives metrics, detects attacks, sends commands.
Pure Python. No system commands. Runs on Laptop 1.
"""

import json
import socket
import threading
import time
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [CONTROLLER] %(message)s')
logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, config_file):
        with open(config_file) as f:
            self.config = json.load(f)

        self.ip = self.config['network']['controller_ip']
        self.port = self.config['network']['controller_port']
        self.ap_ip = self.config['network']['ap_ip']
        self.monitor_ip = self.config['network']['monitor_ip']

        # Detection thresholds
        det = self.config['detection']
        self.thresh_pkt = det['packet_rate_threshold_pps']
        self.thresh_rssi = det['rssi_degradation_threshold_dbm']
        self.thresh_tp = det['throughput_loss_threshold_percent']
        self.thresh_conf = det['detection_confidence_threshold']
        self.check_interval = det['detection_check_interval_seconds']

        self.new_channel = self.config['wifi']['ap_channel_switch']

        # State
        self.running = True
        self.ap_addr = None
        self.monitor_addr = None
        self.latest_ap = {}
        self.latest_mon = {}
        self.baseline_rssi = None
        self.baseline_tp = 9.0
        self.jammer_detected = False
        self.channel_switched = False
        self.current_channel = 6
        self.update_count = 0

        # UDP socket — bind 0.0.0.0 so we receive on ALL interfaces
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.port))

        self._print_banner()

    def _print_banner(self):
        logger.info("=" * 65)
        logger.info("  SDN CONTROLLER STARTED")
        logger.info(f"  Controller IP (this laptop): {self.ip}:{self.port}")
        logger.info(f"  Expecting AP Agent at:       {self.ap_ip}")
        logger.info(f"  Expecting Monitor at:        {self.monitor_ip}")
        logger.info(f"  Detection thresholds:")
        logger.info(f"    Packet Rate > {self.thresh_pkt} pps  → +40 pts")
        logger.info(f"    RSSI drop   > {self.thresh_rssi} dBm   → +30 pts")
        logger.info(f"    Throughput loss > {self.thresh_tp}%   → +30 pts")
        logger.info(f"    Confidence threshold: {self.thresh_conf} pts")
        logger.info("=" * 65)
        logger.info("Waiting for AP Agent and Monitor to connect...\n")

    def start(self):
        threading.Thread(target=self._listener, daemon=True).start()
        threading.Thread(target=self._detection_loop, daemon=True).start()

    def _listener(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(8192)
                msg = json.loads(data.decode())
                src = msg.get('source')
                if src == 'ap_agent':
                    if self.ap_addr is None:
                        logger.info(f"✓ AP Agent connected from {addr[0]}:{addr[1]}")
                    self.ap_addr = addr
                    self.latest_ap = msg.get('ap_metrics', {})
                elif src == 'monitor_agent':
                    if self.monitor_addr is None:
                        logger.info(f"✓ Monitor Agent connected from {addr[0]}:{addr[1]}")
                    self.monitor_addr = addr
                    self.latest_mon = msg.get('monitor_metrics', {})
            except Exception:
                pass
            time.sleep(0.01)

    def _detection_loop(self):
        start = time.time()
        while self.running:
            time.sleep(self.check_interval)
            if not self.latest_ap or not self.latest_mon:
                continue

            elapsed = time.time() - start
            self.update_count += 1

            # --- Extract metrics ---
            rssi_vals = list(self.latest_ap.get('rssi_per_client', {}).values())
            avg_rssi = sum(rssi_vals) / len(rssi_vals) if rssi_vals else -55
            pkt_rate = self.latest_mon.get('jammer_packet_rate_pps', 0)
            throughput = self.latest_mon.get('local_throughput_mbps', 9.0)
            pkt_loss = self.latest_mon.get('packet_loss_percent', 0)
            chan = self.latest_ap.get('channel', self.current_channel)
            num_clients = self.latest_ap.get('num_clients', 0)
            chan_util = self.latest_ap.get('channel_utilization_percent', 0)
            jammer_on = self.latest_mon.get('jammer_active', False)

            # Establish baseline on first valid data (before attack starts)
            if self.baseline_rssi is None and not jammer_on and pkt_rate < self.thresh_pkt:
                self.baseline_rssi = avg_rssi
                self.baseline_tp = throughput if throughput > 0 else 9.0
                logger.info(f"📊 Baseline set: RSSI={self.baseline_rssi:.0f} dBm, Throughput={self.baseline_tp:.1f} Mbps")

            # --- Print status ---
            print()
            logger.info("━" * 65)
            logger.info(f"  📊 NETWORK STATUS — Update #{self.update_count} (t={elapsed:.0f}s)")
            logger.info("━" * 65)
            logger.info(f"  AP:           {self.latest_ap.get('ap_ip', self.ap_ip)}")
            logger.info(f"  Monitor:      {self.latest_mon.get('monitor_ip', self.monitor_ip)}")
            logger.info(f"  Channel:      {chan}")
            logger.info(f"  Clients:      {num_clients}")
            logger.info(f"  Avg RSSI:     {avg_rssi:.0f} dBm")
            logger.info(f"  Throughput:   {throughput:.1f} Mbps")
            logger.info(f"  Packet Rate:  {pkt_rate} pps")
            logger.info(f"  Packet Loss:  {pkt_loss}%")
            logger.info(f"  Chan Util:    {chan_util}%")

            if self.jammer_detected:
                logger.info(f"  Status:       🔴 ATTACK DETECTED — ISOLATED")
            elif jammer_on or pkt_rate > self.thresh_pkt:
                logger.info(f"  Status:       🟡 SUSPICIOUS")
            else:
                logger.info(f"  Status:       🟢 CLEAN")
            logger.info("━" * 65)

            # --- Detection ---
            if self.baseline_rssi is not None and not self.jammer_detected:
                score = 0
                reasons = []

                if pkt_rate > self.thresh_pkt:
                    score += 40
                    reasons.append(f"pkt_rate={pkt_rate}pps")

                rssi_drop = self.baseline_rssi - avg_rssi
                if rssi_drop > self.thresh_rssi:
                    score += 30
                    reasons.append(f"rssi_drop={rssi_drop:.0f}dBm")

                if self.baseline_tp > 0:
                    tp_loss = ((self.baseline_tp - throughput) / self.baseline_tp) * 100
                    if tp_loss > self.thresh_tp:
                        score += 30
                        reasons.append(f"tp_loss={tp_loss:.0f}%")

                if score >= self.thresh_conf:
                    self.jammer_detected = True
                    suspect_mac = self.latest_mon.get('my_mac', 'unknown')
                    print()
                    logger.warning("🚨" * 20)
                    logger.warning(f"  JAMMING ATTACK DETECTED!")
                    logger.warning(f"  Confidence: {score} pts  ({' + '.join(reasons)})")
                    logger.warning(f"  Suspect MAC: {suspect_mac}")
                    logger.warning(f"  Source: Monitor laptop ({self.monitor_ip})")
                    logger.warning("🚨" * 20)

                    # Action 0: Notify AP of attack (degrades metrics)
                    self._send_to_ap({
                        'command': 'attack_notify',
                        'reason': 'jamming_detected'
                    })
                    logger.info(f"  ✓ Sent ATTACK NOTIFY to AP")

                    # Action 1: Blacklist MAC
                    time.sleep(1)
                    self._send_to_ap({
                        'command': 'blacklist_mac',
                        'target_mac': suspect_mac,
                        'reason': 'jamming_detected'
                    })
                    logger.info(f"  ✓ Sent BLACKLIST command to AP → block {suspect_mac}")

                    # Action 2: Channel switch (after 2 sec)
                    time.sleep(2)
                    self._send_to_ap({
                        'command': 'switch_channel',
                        'target_channel': self.new_channel,
                        'reason': 'jammer_on_current_channel'
                    })
                    self.channel_switched = True
                    self.current_channel = self.new_channel
                    logger.info(f"  ✓ Sent CHANNEL SWITCH to AP → CH 6 → CH {self.new_channel}")
                    logger.info(f"  ✓ Attacker isolated. Network recovering.\n")

    def _send_to_ap(self, cmd):
        if self.ap_addr:
            self.sock.sendto(json.dumps(cmd).encode(), self.ap_addr)

    def stop(self):
        self.running = False
        self.sock.close()
        logger.info("Controller stopped.")


def main():
    import sys
    cfg = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    ctrl = Controller(cfg)
    ctrl.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        ctrl.stop()


if __name__ == '__main__':
    main()
