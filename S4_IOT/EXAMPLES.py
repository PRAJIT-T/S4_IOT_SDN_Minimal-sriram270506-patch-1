#!/usr/bin/env python3
"""
EXAMPLES - Different Ways to Run the Attack Demonstration
"""

import subprocess
import sys
import time

def run_example(number, title, commands, description):
    """Run an example scenario"""
    print(f"\n{'='*75}")
    print(f"EXAMPLE {number}: {title}")
    print(f"{'='*75}")
    print(f"\nDescription:")
    print(f"  {description}\n")
    
    print(f"Commands:")
    for i, cmd in enumerate(commands, 1):
        print(f"  Terminal {i}:")
        print(f"    $ {cmd}\n")

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║              SDN ATTACK DETECTION - RUNNING EXAMPLES                 ║
║                                                                       ║
║  How to run the attack detection and isolation demonstration        ║
║  in different configurations                                        ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
""")
    
    # Example 1: One-command quick start
    run_example(
        1,
        "ONE-COMMAND QUICK START (Easiest)",
        ["python3 quick_start.py"],
        "Fully automated! Starts everything and runs the demo."
    )
    
    # Example 2: Automated demo
    run_example(
        2,
        "AUTOMATED DEMO WITH PROGRESS",
        ["python3 demo_attack_scenario.py"],
        "Shows orchestration progress and detailed status updates."
    )
    
    # Example 3: Manual 4-terminal setup
    run_example(
        3,
        "MANUAL SETUP (4 TERMINALS)",
        [
            "python3 sdn_controller.py",
            "python3 ap_agent.py",
            "python3 monitor_agent.py",
            "sleep 10 && python3 attacker.py --channel 6 --duration 15"
        ],
        "Start each component manually in separate terminals."
    )
    
    # Example 4: With web dashboard
    run_example(
        4,
        "WITH WEB DASHBOARD (5 TERMINALS)",
        [
            "python3 sdn_controller.py",
            "python3 ap_agent.py",
            "python3 monitor_agent.py",
            "python3 dashboard.py",
            "sleep 10 && python3 attacker.py --channel 6 --duration 15"
        ],
        """Start core system + web dashboard.
  Then open browser to: http://localhost:5000
  Watch real-time visualization while attack happens."""
    )
    
    # Example 5: Multiple attacks on different channels
    run_example(
        5,
        "MULTIPLE ATTACKS (SEQUENTIAL)",
        [
            "python3 sdn_controller.py",
            "python3 ap_agent.py",
            "python3 monitor_agent.py",
            "sleep 10 && python3 attacker.py --channel 6 --duration 10",
            "sleep 25 && python3 attacker.py --channel 11 --duration 10"
        ],
        """Attack channel 6 first, then channel 11.
  Watch controller handle multiple attacks.
  See how it isolates each attacker independently."""
    )
    
    # Example 6: Attacker with delay
    run_example(
        6,
        "ATTACKER WITH CUSTOM DELAY",
        [
            "python3 sdn_controller.py",
            "python3 ap_agent.py",
            "python3 monitor_agent.py",
            "python3 attacker.py --channel 6 --delay 5 --duration 20"
        ],
        """Attacker waits 5 seconds before starting.
  Use --delay to stagger attacks.
  Useful for observing baseline longer."""
    )
    
    # Example 7: Extended attack
    run_example(
        7,
        "EXTENDED ATTACK (30 SECONDS)",
        [
            "python3 sdn_controller.py",
            "python3 ap_agent.py",
            "python3 monitor_agent.py",
            "sleep 10 && python3 attacker.py --channel 6 --duration 30"
        ],
        """Longer attack to see sustained jamming effects.
  Controller adapts its channel switching strategy.
  More data points for analysis."""
    )
    
    # Example 8: Verify setup
    run_example(
        8,
        "VERIFY SETUP (Before Running)",
        ["python3 verify_setup.py"],
        """Check that all files exist and ports are available.
  Run this first if you have issues."""
    )
    
    # Example 9: Different channels
    run_example(
        9,
        "ATTACK DIFFERENT CHANNELS",
        [
            "python3 sdn_controller.py",
            "python3 ap_agent.py",
            "python3 monitor_agent.py",
            "# Attack on channel 6",
            "python3 attacker.py --channel 6 --delay 5 --duration 10 &",
            "# Attack on channel 11",
            "python3 attacker.py --channel 11 --delay 20 --duration 10 &",
            "# Attack on channel 2",
            "python3 attacker.py --channel 2 --delay 35 --duration 10 &"
        ],
        """Multiple simultaneous attacks on different channels.
  Controller must handle concurrent threats.
  See isolation of multiple attackers."""
    )
    
    # Example 10: Stress test
    run_example(
        10,
        "STRESS TEST (RAPID ATTACKS)",
        [
            "python3 sdn_controller.py",
            "python3 ap_agent.py",
            "python3 monitor_agent.py",
            """python3 attacker.py --channel 6 --delay 5 --duration 3 && \\
python3 attacker.py --channel 6 --delay 10 --duration 3 && \\
python3 attacker.py --channel 6 --delay 15 --duration 3"""
        ],
        """Back-to-back attacks on same channel.
  Test controller's reaction time.
  See if it handles rapid threats."""
    )
    
    # Additional information
    print(f"\n{'='*75}")
    print("RECOMMENDED: Start with Example 1 (One-Command Quick Start)")
    print("='*75\n")
    
    print("\nADVANCED OPTIONS:\n")
    
    print("Kill running processes:")
    print("  pkill -f 'python3 sdn_controller.py'")
    print("  pkill -f 'python3 ap_agent.py'")
    print("  pkill -f 'python3 monitor_agent.py'")
    print("  pkill -f 'python3 attacker.py'\n")
    
    print("Check if ports are in use:")
    print("  lsof -i :9000")
    print("  lsof -i :9001")
    print("  lsof -i :5000\n")
    
    print("Monitor real-time:")
    print("  tail -f controller_results.json")
    print("  grep 'ATTACK' controller_results.json\n")
    
    print("View results after demo:")
    print("  cat controller_results.json")
    print("  python3 -m json.tool < controller_results.json\n")

if __name__ == '__main__':
    main()
