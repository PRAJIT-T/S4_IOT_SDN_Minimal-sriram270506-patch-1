# SDN WiFi Testbed - Attack Detection & Isolation

## Overview

This project demonstrates an **Software-Defined Networking (SDN) system** that detects and isolates **pseudo-jamming attacks** on WiFi networks. The system uses 2 virtual nodes communicating on WiFi channels and a controller that monitors metrics to detect attacks.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     WiFi Network                                │
│  Channel 6, 11, 2 (selectable by SDN Controller)               │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │   Virtual Node 1 │  │   Virtual Node 2 │  ← 2 Nodes        │
│  │  (Connected)     │  │  (Connected)     │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
│           └────────────┬────────┘                              │
│                        │ WiFi                                   │
│           ┌────────────▼──────────────┐                        │
│           │   WiFi AP Agent           │                        │
│           │ (Simulates AP, ch 6/11/2) │                        │
│           └────────────┬──────────────┘                        │
│                        │                                        │
│  ┌─────────────────────┼─────────────────────┐                │
│  │ UDP Metrics (9000)  │ UDP Commands (9001) │                │
│  └─────────────────────┼─────────────────────┘                │
│                        │                                        │
└────────────────────────┼────────────────────────────────────────┘
                         │
        ┌────────────────┴─────────────────┐
        │                                  │
   ┌────▼────────┐              ┌──────────▼──────┐
   │ Monitor     │              │ SDN Controller  │
   │ Agent       │              │ (Decision Maker)│
   │ (Traffic    │              │ • Tracks metrics│
   │  Analysis)  │              │ • Detects attack│
   └────┬────────┘              │ • Isolates IPs │
        │                        │ • Logs results │
        │ UDP Metrics            │ • Prints status│
        │ (9000)                 └────────────────┘
        │                              △
        └──────────────────────────────┘
                                        │
                          ┌─────────────┴──────────┐
                          │                        │
                    ┌─────▼──────┐        ┌───────▼────┐
                    │  Attacker   │        │ Dashboard  │
                    │  (Jamming)  │        │ (Web UI)   │
                    │ • Ch 6      │        │ (Port 5000)│
                    │ • Floods IP │        └────────────┘
                    │ • Spoofs ID │
                    └────────────┘
```

## 2 Virtual Nodes Setup

Your system has **2 virtual nodes**:
- Both connected to the WiFi AP Agent
- Communicate on selectable channel (default: 6)
- Can be monitored individually or as a group
- Metrics: Throughput, RSSI, packet loss, packet rate

## Controller Channel Monitoring

The **SDN Controller** tracks metrics by channel:

```
Monitored Channels:
├── Channel 2 (backup)
├── Channel 6 (primary)
└── Channel 11 (primary)

Metrics Tracked (every 5 seconds):
├── Throughput (Mbps)
├── RSSI (dBm)
├── Packet Loss (%)
├── Packet Rate (pps)
├── Phase (baseline/attack/recovery)
└── Jammer Status
```

Sample Output:
```
======================================================================
[CHANNEL 6 METRICS] - Update #1
======================================================================
  Throughput:        4.50 Mbps
  RSSI:             -45 dBm
  Packet Loss:       0.5%
  Packet Rate:     300 pps
  Phase:           baseline
  Jammer Status:   Clean ✓
======================================================================
```

## Attacker.py - Pseudo Jamming Simulation

The attacker simulates a malicious node that jams WiFi:

### How It Works:

1. **Sends Jamming Packets**: Floods the AP with fake jam packets
2. **Spoofs Channel**: Can target specific channels (2, 6, or 11)
3. **Simulates Impact**:
   - Increases packet rate (8000-10000 pps)
   - Reduces RSSI signal
   - Decreases throughput
   - Increases packet loss

### Attack Metrics:

```
Jamming Characteristics:
├── Packet Rate: 8000-10000 pps (vs normal 200-500 pps)
├── RSSI: -65 to -75 dBm (vs normal -45 to -50 dBm)
├── Throughput: 0.8-1.5 Mbps (vs normal 8-9 Mbps)
└── Packet Loss: 75-85% (vs normal 0-1%)
```

## Controller Detection & Isolation

### Detection Algorithm:

The controller analyzes metrics every 2 seconds:

```python
if (packet_rate > 5000 AND rssi < -60 AND throughput < 2.0):
    JAMMER_DETECTED = True
    print("🚨 JAMMING ATTACK DETECTED ON CHANNEL 6!")
```

### Isolation Actions:

When attack detected:

1. **Identify Attacker**:
   ```
   🔴 JAM PACKET DETECTED!
   Attacker ID: ATTACKER_5432
   Channel: 6
   Source IP: 127.0.0.1
   ```

2. **Block IP Address**:
   ```
   🔒 ISOLATING ATTACKER!
   Attacker ID: ATTACKER_5432
   Source IP: 127.0.0.1
   Action: BLOCKING IP 127.0.0.1
   ```

3. **Switch Channel** (if needed):
   ```
   Decision: Switch from Channel 6 → Channel 11
   ```

## Running the Demonstration

### Option 1: Automated Demo (Recommended)

```bash
python3 demo_attack_scenario.py
```

This will:
1. Start SDN Controller (port 9000)
2. Start AP Agent with 2 virtual nodes (port 9001)
3. Start Monitor Agent (traffic analysis)
4. Wait 10 seconds
5. Launch Attacker (15 seconds of jamming)
6. Show detection and isolation in real-time

### Option 2: Manual Startup (4 Terminal Windows)

**Terminal 1 - Controller:**
```bash
python3 sdn_controller.py
```

**Terminal 2 - AP Agent:**
```bash
python3 ap_agent.py
```

**Terminal 3 - Monitor Agent:**
```bash
python3 monitor_agent.py
```

**Terminal 4 - Attacker (start after 10 seconds):**
```bash
python3 attacker.py --channel 6 --duration 15
```

### Option 3: Run with Web Dashboard

```bash
# Terminal 1: Controller
python3 sdn_controller.py

# Terminal 2: AP Agent
python3 ap_agent.py

# Terminal 3: Monitor Agent
python3 monitor_agent.py

# Terminal 4: Dashboard (open browser to http://localhost:5000)
python3 dashboard.py

# Terminal 5: Attacker
python3 attacker.py --channel 6 --duration 15
```

## Attacker.py Command-Line Options

```bash
python3 attacker.py [OPTIONS]

Options:
  --target-ap IP        Target AP IP (default: 127.0.0.1)
  --ap-port PORT        Target AP port (default: 9001)
  --controller IP       Controller IP (default: 127.0.0.1)
  --controller-port P   Controller port (default: 9000)
  --channel N           WiFi channel to jam (default: 6)
  --duration N          Attack duration in seconds (default: 30)
  --delay N             Delay before starting attack (default: 0)

Examples:
  # Jam channel 6 for 20 seconds
  python3 attacker.py --channel 6 --duration 20
  
  # Jam channel 11 after 5 second delay
  python3 attacker.py --channel 11 --delay 5 --duration 30
```

## Expected Output

### Phase 1: Baseline (0-10s)
```
[AP] Ch:6 | 4.50Mbps | RSSI:-45dBm | Phase:baseline
[Monitor] 300 pps | Phase: baseline

[CHANNEL 6 METRICS] - Update #1
  Throughput:        4.50 Mbps
  Jammer Status:   Clean ✓
```

### Phase 2: Attack (10-15s)
```
[ATTACKER_5432] 🔴 STARTING JAMMING ATTACK!
[ATTACKER_5432] Target Channel: 6
[ATTACKER_5432] 🔴 ATTACKING | Packets: 50000 | Rate: 8000 pps

[Controller] 🔴 JAM PACKET DETECTED!
  Attacker ID: ATTACKER_5432
  Channel: 6
  Source IP: 127.0.0.1

[AP] Ch:6 | 0.90Mbps | RSSI:-70dBm | Phase:attack
```

### Phase 3: Detection & Isolation (15-20s)
```
[Controller] 🚨 JAMMING ATTACK DETECTED ON CHANNEL 6!
  Throughput: 0.90 Mbps
  RSSI: -70 dBm
  Packet Rate: 8200 pps
  Decision: Switch from Channel 6 → Channel 11

[Controller] 🔒 ISOLATING ATTACKER!
  Attacker ID: ATTACKER_5432
  Source IP: 127.0.0.1
  Action: BLOCKING IP 127.0.0.1

[ATTACKER_5432] 🚨 DETECTED AND ISOLATED BY CONTROLLER!
```

## Results

After the demo, check `controller_results.json`:

```json
{
  "timestamp": "2026-03-03T10:30:45.123456",
  "system": "SDN WiFi Testbed with Attack Detection",
  "jammer_detected": true,
  "detection_time": "2026-03-03T10:30:55.234567",
  "channels_monitored": [2, 6, 11],
  "current_channel": 11,
  "detected_attackers": ["ATTACKER_5432"],
  "isolated_ips": ["127.0.0.1"],
  "metrics_count": 150
}
```

## Key Features

✅ **2 Virtual Nodes**: Simulated WiFi clients communicating  
✅ **Channel Monitoring**: Tracks metrics on channels 2, 6, 11  
✅ **Frequent Metrics**: Controller prints metrics every 5 seconds  
✅ **Pseudo Jamming**: Attacker floods packets to simulate jamming  
✅ **Attack Detection**: Uses 3 metrics (packet rate, RSSI, throughput)  
✅ **IP Isolation**: Blocks malicious IP addresses  
✅ **Real-time Dashboard**: Web UI to visualize metrics (optional)  

## Files Overview

| File | Purpose |
|------|---------|
| `sdn_controller.py` | Decision maker, detects attacks, isolates IPs |
| `ap_agent.py` | WiFi AP simulator, generates metrics |
| `monitor_agent.py` | Traffic monitor, simulates phases |
| `attacker.py` | **NEW** - Pseudo jamming attacker |
| `dashboard.py` | Web dashboard (optional visualization) |
| `demo_attack_scenario.py` | **NEW** - Automated demonstration |
| `controller_results.json` | Results log |

## Network Ports

| Port | Component | Traffic |
|------|-----------|---------|
| 9000 | Controller | Metrics reception, decision making |
| 9001 | AP Agent | Command reception, control |
| 9002 | Dashboard | Metrics for visualization |
| 9003 | Attacker | Isolation notifications |
| 5000 | Dashboard | HTTP web interface |

## Demonstration Scenarios

### Scenario 1: Single Attack Detection
```bash
python3 demo_attack_scenario.py
```
- Baseline metrics displayed
- Attacker launches on channel 6
- Controller detects and isolates
- System recovers

### Scenario 2: Multi-Channel Attack
```bash
# Terminal 1-3: Start components
python3 sdn_controller.py &
python3 ap_agent.py &
python3 monitor_agent.py &

# Terminal 4: Attack channel 6
python3 attacker.py --channel 6 --duration 10

# Terminal 5: Attack channel 11
python3 attacker.py --channel 11 --delay 15 --duration 10
```

### Scenario 3: Evasion Attempt
```bash
# Quick attacks on different channels
for ch in 6 11 2; do
  python3 attacker.py --channel $ch --delay $((i*5)) --duration 5 &
done
```

## Troubleshooting

**Problem**: Processes won't start  
**Solution**: Check if ports 9000-9003 are available
```bash
lsof -i :9000  # Check if port is in use
```

**Problem**: "Address already in use"  
**Solution**: Kill existing processes
```bash
pkill -f "python3 sdn_controller.py"
pkill -f "python3 ap_agent.py"
```

**Problem**: No metrics printed  
**Solution**: Ensure all 3 components are running and can communicate

**Problem**: Attacker not detected  
**Solution**: Check threshold values in `sdn_controller.py` line 95-96

## Customization

### Change Attack Duration
```bash
python3 attacker.py --duration 60  # Attack for 60 seconds
```

### Change Attack Channel
```bash
python3 attacker.py --channel 11  # Jam channel 11 instead of 6
```

### Adjust Detection Threshold
Edit `sdn_controller.py`:
```python
if (avg_packet_rate > 5000 and      # Change to 3000 for faster detection
    avg_rssi < -60 and               # Change to -55 for lower threshold
    avg_throughput < 2.0):           # Change to 3.0 for higher threshold
```

## Metrics Explained

- **Throughput**: Data transfer rate (Mbps). Attack reduces this to <1 Mbps
- **RSSI**: Signal strength (dBm). More negative = weaker. Attack causes -70+ dBm
- **Packet Loss**: % of packets lost. Attack causes 75%+ loss
- **Packet Rate**: Packets per second. Attack causes 8000+ pps vs normal 200-500 pps
- **Phase**: baseline (normal) → attack (jamming) → recovery (mitigated)

## Security Implications

This testbed demonstrates:

1. **Network Vulnerability**: WiFi is susceptible to jamming attacks
2. **Detection Capability**: Anomaly detection works via metric analysis
3. **Mitigation Strategy**: IP blocking + channel switching can mitigate
4. **SDN Benefits**: Centralized controller enables quick responses
5. **Defense Layers**: 
   - Detection (metric analysis)
   - Identification (IP tracking)
   - Isolation (IP blocking)
   - Recovery (channel switching)

## Future Enhancements

- [ ] Machine learning-based attack detection
- [ ] Automatic channel selection algorithm
- [ ] Multiple attacker detection
- [ ] Real WiFi hardware integration
- [ ] Geographical heat map visualization
- [ ] Automated threat reporting

---

**Created**: 2026-03-03  
**Project**: SDN WiFi Testbed - Attack Detection & Isolation  
**Status**: Active Demonstration
