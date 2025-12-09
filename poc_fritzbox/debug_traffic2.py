#!/usr/bin/env python3
"""
Debug script to test specific traffic statistics actions
"""

import argparse
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzhosts import FritzHosts
from rich.console import Console
from rich.pretty import pprint

console = Console()

def parse_args():
    parser = argparse.ArgumentParser(description="Debug FritzBox Traffic Stats")
    parser.add_argument("--ip", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    return parser.parse_args()

def main():
    args = parse_args()

    console.print("[yellow]Connecting to FritzBox...[/yellow]")
    fc = FritzConnection(address=args.ip, user=args.username, password=args.password)
    fh = FritzHosts(fc=fc)

    # Get a sample host
    hosts = fh.get_hosts_info()
    sample_ip = None
    sample_mac = None
    if hosts:
        for host in hosts:
            if host.get('status'):  # Get an online device
                sample_ip = host.get('ip')
                sample_mac = host.get('mac')
                console.print(f"\n[cyan]Using sample device: {host.get('name')} ({sample_ip})[/cyan]")
                break

    # Test WLAN Statistics
    console.print("\n[bold magenta]Testing WLANConfiguration1 GetStatistics:[/bold magenta]")
    try:
        result = fc.call_action('WLANConfiguration1', 'GetStatistics')
        pprint(result)
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")

    console.print("\n[bold magenta]Testing WLANConfiguration1 GetPacketStatistics:[/bold magenta]")
    try:
        result = fc.call_action('WLANConfiguration1', 'GetPacketStatistics')
        pprint(result)
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")

    # Test LAN Statistics
    console.print("\n[bold magenta]Testing LANEthernetInterfaceConfig1 GetStatistics:[/bold magenta]")
    try:
        result = fc.call_action('LANEthernetInterfaceConfig1', 'GetStatistics')
        pprint(result)
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")

    # Test host-specific info
    if sample_ip:
        console.print(f"\n[bold magenta]Testing X_AVM-DE_GetSpecificHostEntryByIP for {sample_ip}:[/bold magenta]")
        try:
            result = fc.call_action('Hosts1', 'X_AVM-DE_GetSpecificHostEntryByIP', NewIPAddress=sample_ip)
            pprint(result)
        except Exception as e:
            console.print(f"[red]Failed: {e}[/red]")

    # Try to get associated device info for Wi-Fi devices
    console.print("\n[bold magenta]Testing GetTotalAssociations:[/bold magenta]")
    try:
        result = fc.call_action('WLANConfiguration1', 'GetTotalAssociations')
        total = result.get('NewTotalAssociations', 0)
        console.print(f"Total Wi-Fi associations: {total}")

        # Try to get info for each associated device
        for i in range(total):
            console.print(f"\n[cyan]Device {i}:[/cyan]")
            try:
                result = fc.call_action('WLANConfiguration1', 'GetGenericAssociatedDeviceInfo', NewAssociatedDeviceIndex=i)
                pprint(result)
            except Exception as e:
                console.print(f"[red]Failed: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")

if __name__ == "__main__":
    main()
