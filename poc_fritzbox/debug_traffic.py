#!/usr/bin/env python3
"""
Debug script to find per-device traffic statistics
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
    if hosts:
        sample_host = hosts[0]
        mac = sample_host.get('mac')

        console.print(f"\n[cyan]Sample host data for MAC {mac}:[/cyan]")
        pprint(sample_host)

        # Try to get detailed host info
        console.print(f"\n[cyan]Detailed host info:[/cyan]")
        try:
            details = fh.get_host_details(mac)
            pprint(details)
        except Exception as e:
            console.print(f"[red]Failed: {e}[/red]")

    # Look for LAN-related services that might have traffic stats
    console.print("\n[cyan]Looking for LAN/Host services:[/cyan]")
    lan_services = [s for s in fc.services.keys() if 'LAN' in s or 'Host' in s]

    for service_name in lan_services:
        console.print(f"\n[bold magenta]{service_name}[/bold magenta]")
        service = fc.services[service_name]

        for action_name in service.actions.keys():
            console.print(f"  [yellow]{action_name}[/yellow]")

            # Try to call actions that might return traffic info
            if 'Get' in action_name and 'Info' in action_name:
                try:
                    # Check if action needs index parameter
                    action = service.actions[action_name]
                    if action.arguments:
                        # Try with index 0
                        result = fc.call_action(service_name, action_name, NewIndex=0)
                    else:
                        result = fc.call_action(service_name, action_name)

                    # Look for traffic/byte fields
                    traffic_fields = [k for k in result.keys() if 'Byte' in k or 'Packet' in k or 'Traffic' in k]
                    if traffic_fields:
                        console.print(f"    [green]Found traffic fields:[/green]")
                        for field in traffic_fields:
                            console.print(f"      {field}: {result[field]}")
                except Exception as e:
                    pass

if __name__ == "__main__":
    main()
