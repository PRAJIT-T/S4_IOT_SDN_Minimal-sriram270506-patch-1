# 🎯 SDN WiFi Testbed - Attack Detection & Isolation System

## 📌 Quick Summary

Your project now has a **complete attack detection and isolation demonstration** with:

- ✅ **2 Virtual Nodes** - Connected to WiFi, exchange traffic
- ✅ **Channel Monitoring** - Tracks channels 2, 6, 11 in real-time
- ✅ **Frequent Metrics** - Prints detailed status every 5 seconds
- ✅ **Attacker.py** - Pseudo jamming that impacts network metrics
- ✅ **Auto-Detection** - Controller detects anomalies via 3 metrics
- ✅ **IP Isolation** - Blocks malicious IPs and stops attack
- ✅ **Full Automation** - One-command demo with complete orchestration

---

## 🚀 Quick Start (30 seconds)

```bash
python3 quick_start.py
```

This runs the entire demonstration automatically:
1. Starts all components
2. Shows baseline metrics (0-10s)
3. Launches jamming attack (10-15s)
4. Detects and isolates attacker (15-20s)
5. Shows recovery (20+ seconds)

---

## 📊 What You'll See

### Baseline (Normal Operation)
```
══════════════════════════════════════════════════════════
[CHANNEL 6 METRICS] - Update #1
══════════════════════════════════════════════════════════
  Throughput:        4.50 Mbps
  RSSI:             -45 dBm
  Packet Loss:       0.5%
  Packet Rate:     300 pps
  Phase:           baseline
  Jammer Status:   Clean ✓
```

### Under Attack
```
[Controller] 🔴 JAM PACKET DETECTED!
  Attacker ID: ATTACKER_5432
  Channel: 6
  Source IP: 127.0.0.1

[Controller] 🚨 JAMMING ATTACK DETECTED ON CHANNEL 6!
  Throughput: 0.90 Mbps
  RSSI: -70 dBm
  Packet Rate: 8200 pps
  Decision: Switch from Channel 6 → Channel 11
```

### After Isolation
```
[Controller] 🔒 ISOLATING ATTACKER!
  Attacker ID: ATTACKER_5432
  Source IP: 127.0.0.1
  Action: BLOCKING IP 127.0.0.1

[ATTACKER_5432] 🚨 DETECTED AND ISOLATED BY CONTROLLER!
```

---

## 📁 New Files Created

| File | Purpose |
|------|---------|
| `attacker.py` | Pseudo-jamming attack simulator |
| `demo_attack_scenario.py` | Full orchestration & automation |
| `quick_start.py` | One-command launcher |
| `verify_setup.py` | Validation tool |
| `ATTACK_DETECTION_GUIDE.md` | Complete documentation |
| `PROJECT_SETUP.txt` | Setup & configuration guide |
| `SYSTEM_ARCHITECTURE.txt` | Visual diagrams & flows |
| `EXAMPLES.py` | 10 different run scenarios |
| `IMPLEMENTATION_COMPLETE.txt` | What was implemented |

---

## 🔧 Different Ways to Run

### Option 1: One Command (EASIEST)
```bash
python3 quick_start.py
```

### Option 2: Automated Demo
```bash
python3 demo_attack_scenario.py
```

### Option 3: Manual Setup (4 Terminals)
```bash
# Terminal 1
python3 sdn_controller.py

# Terminal 2
python3 ap_agent.py

# Terminal 3
python3 monitor_agent.py

# Terminal 4 (after 10 seconds)
python3 attacker.py --channel 6 --duration 15
```

### Option 4: With Web Dashboard
```bash
# Terminal 1-3: Same as above
# Terminal 4
python3 dashboard.py

# Terminal 5 (after 10 seconds)
python3 attacker.py --channel 6 --duration 15

# Browser
http://localhost:5000
```

---

## 🎯 How It Works

### 1️⃣ Two Virtual Nodes
- Both connected to WiFi AP on Channel 6 (default)
- Exchange traffic between each other
- Generate realistic network metrics

### 2️⃣ Controller Monitors Channels
- Listens on port 9000 for metrics
- Receives data from AP and Monitor agents
- Tracks metrics by channel (2, 6, 11)
- **Prints detailed status every 5 seconds**

### 3️⃣ Attacker Launches
- Floods WiFi with jamming packets
- Creates realistic impact:
  - Packet Rate: 300 → 8000+ pps (25x)
  - RSSI: -45 → -70 dBm (drops 25 dBm)
  - Throughput: 4.5 → 0.9 Mbps (80% drop)

### 4️⃣ Controller Detects
Uses 3-metric threshold:
```
IF (packet_rate > 5000 AND rssi < -60 AND throughput < 2.0):
    ATTACK DETECTED! 🚨
```

### 5️⃣ Controller Isolates
- Identifies attacker by IP
- Blocks the IP address
- Switches to clean channel
- Sends isolation notice to attacker

### 6️⃣ System Recovers
- Nodes move to channel 11
- Attacker is permanently blocked
- Network returns to normal

---

## 📊 Channel Metrics Output

Every 5 seconds, controller prints:

```
══════════════════════════════════════════════════════════════════════════
[CHANNEL 6 METRICS] - Update #N
══════════════════════════════════════════════════════════════════════════
  Throughput:        X.XX Mbps
  RSSI:             -XX dBm
  Packet Loss:       X.X%
  Packet Rate:     XXXX pps
  Phase:           baseline/attack/recovery
  Jammer Status:   Clean ✓ or DETECTED ⚠️
  
  [Detected Attackers]
    - ATTACKER_5432 (packets: 45000)
  
  [Isolated IPs]
    - 127.0.0.1 🔒
══════════════════════════════════════════════════════════════════════════
```

---

## 🎮 Attacker.py Options

```bash
python3 attacker.py [OPTIONS]

Options:
  --channel N              WiFi channel to jam (2, 6, 11) [default: 6]
  --duration N             Attack duration in seconds [default: 30]
  --delay N                Delay before starting (seconds) [default: 0]
  --target-ap IP           Target AP IP [default: 127.0.0.1]
  --ap-port PORT           Target AP port [default: 9001]
  --controller IP          Controller IP [default: 127.0.0.1]
  --controller-port PORT   Controller port [default: 9000]

Examples:
  # Jam channel 6 for 20 seconds
  python3 attacker.py --channel 6 --duration 20
  
  # Jam after 5 second delay
  python3 attacker.py --channel 11 --delay 5 --duration 30
  
  # Attack on channel 2
  python3 attacker.py --channel 2 --duration 15
```

---

## ⚡ Network Metrics Explained

| Metric | Normal | Under Attack | Detection |
|--------|--------|--------------|-----------|
| **Throughput** | 4-5 Mbps | <1 Mbps | < 2 Mbps ⚠️ |
| **RSSI** | -45 to -50 dBm | -65 to -75 dBm | < -60 dBm ⚠️ |
| **Packet Rate** | 200-500 pps | 8000+ pps | > 5000 pps ⚠️ |
| **Packet Loss** | <1% | >75% | Increases 75x |

---

## 🛠️ Setup Verification

Before running, verify setup:
```bash
python3 verify_setup.py
```

This checks:
- ✅ Python version (3.7+)
- ✅ All required files exist
- ✅ Required Python packages
- ✅ Available network ports

---

## 📈 Expected Timeline

| Time | Event | Status |
|------|-------|--------|
| 0-2s | Components starting | 🔄 Initializing |
| 2-10s | Baseline metrics | 🟢 CLEAN |
| 10s | Attacker launches | 🔴 ATTACK STARTS |
| 12-15s | Metrics degrade | ⚠️ ANOMALY |
| 15s | Attack detected | 🚨 DETECTED |
| 15-16s | IP isolation | 🔒 ISOLATING |
| 16s | Attacker stops | 🛑 STOPPED |
| 18-20s | Recovery | 🟢 RECOVERED |

---

## 📂 Project Structure

```
/home/sriram/S4_IOT/
├── sdn_controller.py           (Enhanced - metrics tracking)
├── ap_agent.py                 (2 virtual nodes on WiFi)
├── monitor_agent.py            (Traffic analysis)
│
├── attacker.py                 ✨ NEW - Jamming simulator
├── demo_attack_scenario.py     ✨ NEW - Automation
├── quick_start.py              ✨ NEW - One-command launcher
├── verify_setup.py             ✨ NEW - Validation
│
├── dashboard.py                (Web visualization)
│
├── ATTACK_DETECTION_GUIDE.md   ✨ NEW - Full guide
├── PROJECT_SETUP.txt           ✨ NEW - Setup info
├── SYSTEM_ARCHITECTURE.txt     ✨ NEW - Diagrams
├── EXAMPLES.py                 ✨ NEW - Run examples
├── IMPLEMENTATION_COMPLETE.txt ✨ NEW - Summary
│
└── controller_results.json     (Generated after run)
```

---

## 🚀 Next Steps

1. **Verify Setup**
   ```bash
   python3 verify_setup.py
   ```

2. **Run the Demo**
   ```bash
   python3 quick_start.py
   ```

3. **Watch the Output**
   - Baseline metrics (0-10s)
   - Attack detection (10-15s)
   - Isolation (15-20s)
   - Recovery (20+s)

4. **Check Results**
   ```bash
   cat controller_results.json
   ```

---

## ❓ FAQ

**Q: How do the 2 virtual nodes communicate?**
A: Through the WiFi AP Agent simulation. Both connect to the same AP on a specific channel and can exchange traffic.

**Q: What channels are monitored?**
A: Three channels: 2, 6, and 11 (standard WiFi channels).

**Q: Why does the controller print metrics every 5 seconds?**
A: To show real-time network status and allow you to see the impact of jamming and recovery.

**Q: Is this real jamming?**
A: No, it's "pseudo jamming" - the attacker simulates the impact by flooding packets and calculating realistic metrics degradation. Real jamming would require actual WiFi hardware.

**Q: How fast is the detection?**
A: Within 2-3 seconds of attack starting, as the controller checks metrics every 2 seconds.

**Q: Can multiple attackers be detected?**
A: Yes! The system tracks all detected attackers and isolates each one independently.

---

## 📖 Documentation

- **ATTACK_DETECTION_GUIDE.md** - Complete reference guide
- **PROJECT_SETUP.txt** - Detailed setup instructions
- **SYSTEM_ARCHITECTURE.txt** - Visual diagrams and flows
- **EXAMPLES.py** - 10 different scenarios to try
- **IMPLEMENTATION_COMPLETE.txt** - Summary of what was built

---

## 🎓 Learning Outcomes

This project demonstrates:

1. **SDN Concepts** - Centralized network control
2. **Attack Detection** - Anomaly-based detection via metrics
3. **Network Monitoring** - Real-time metric collection
4. **Automated Response** - Controller makes decisions
5. **IP Isolation** - Blocking malicious sources
6. **Channel Management** - Dynamic channel switching
7. **System Orchestration** - Coordinating multiple agents

---

**Ready to run the demo?**

```bash
python3 quick_start.py
```

✨ Enjoy the demonstration! ✨
