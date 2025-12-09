#!/usr/bin/env python3
"""
Check the raw case of device names from FritzBox
"""

import argparse
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzhosts import FritzHosts
from rich.console import Console

console = Console()

def parse_args():
    parser = argparse.ArgumentParser(description="Check device name case")
    parser.add_argument("--ip", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    return parser.parse_args()

def main():
    args = parse_args()

    fc = FritzConnection(address=args.ip, user=args.username, password=args.password)
    fh = FritzHosts(fc=fc)

    hosts = fh.get_hosts_info()

    console.print("\n[cyan]Raw device names from API:[/cyan]")
    for host in hosts:
        if host.get('status'):  # Only online devices
            name = host.get('name')
            ip = host.get('ip')
            console.print(f"  {ip}: '{name}' (repr: {repr(name)})")

if __name__ == "__main__":
    main()
