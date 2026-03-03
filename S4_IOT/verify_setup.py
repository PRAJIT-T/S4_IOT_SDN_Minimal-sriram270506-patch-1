#!/usr/bin/env python3
"""
VERIFY SETUP - Check that all components are ready
"""

import os
import sys
import subprocess
import socket

def check_file_exists(filepath):
    """Check if file exists"""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"  {status} {filepath}")
    return exists

def check_port_available(port):
    """Check if port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except OSError:
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     SDN WiFi TESTBED - SETUP VERIFICATION                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    all_good = True
    
    # Check Python version
    print("\n[1] Python Version:")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"  ✓ Python {version.major}.{version.minor}")
    else:
        print(f"  ✗ Python {version.major}.{version.minor} (need 3.7+)")
        all_good = False
    
    # Check required files
    print("\n[2] Required Files:")
    files = [
        'sdn_controller.py',
        'ap_agent.py',
        'monitor_agent.py',
        'attacker.py',
        'dashboard.py',
        'demo_attack_scenario.py',
        'quick_start.py'
    ]
    
    for f in files:
        if not check_file_exists(f):
            all_good = False
    
    # Check required Python packages
    print("\n[3] Python Packages:")
    packages = {
        'flask': 'Flask (for dashboard)',
        'json': 'JSON (built-in)',
        'socket': 'Socket (built-in)',
        'threading': 'Threading (built-in)',
        'time': 'Time (built-in)'
    }
    
    for pkg, name in packages.items():
        try:
            __import__(pkg)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} (missing)")
            if pkg != 'json' and pkg != 'socket' and pkg != 'threading' and pkg != 'time':
                all_good = False
    
    # Check ports available
    print("\n[4] Network Ports:")
    ports = {
        9000: 'Controller',
        9001: 'AP Agent',
        9002: 'Dashboard (UDP)',
        9003: 'Attacker',
        5000: 'Web Dashboard'
    }
    
    for port, service in ports.items():
        available = check_port_available(port)
        status = "✓" if available else "✗"
        print(f"  {status} Port {port:5d}: {service}")
        if not available:
            print(f"       (Already in use - kill with: pkill -f 'python3')")
            # Don't fail for this, just warn
    
    # Summary
    print("\n" + "="*60)
    
    if all_good:
        print("✓ ALL CHECKS PASSED - Ready to run!")
        print("\nNext step:")
        print("  python3 quick_start.py")
        print("\nOr manually:")
        print("  python3 demo_attack_scenario.py")
        return 0
    else:
        print("✗ Some checks failed. See above for details.")
        print("\nTo fix missing packages:")
        print("  pip install flask")
        return 1

if __name__ == '__main__':
    sys.exit(main())
