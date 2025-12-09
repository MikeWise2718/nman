#!/usr/bin/env python3
"""
Debug script to find services that contain uptime information
"""

import argparse
from fritzconnection import FritzConnection
from rich.console import Console

console = Console()

def parse_args():
    parser = argparse.ArgumentParser(description="Debug FritzBox Services")
    parser.add_argument("--ip", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    return parser.parse_args()

def main():
    args = parse_args()

    console.print("[yellow]Connecting to FritzBox...[/yellow]")
    fc = FritzConnection(address=args.ip, user=args.username, password=args.password)

    # Look for services related to WAN connection
    wan_services = [s for s in fc.services.keys() if 'WAN' in s or 'Connection' in s]

    console.print(f"\n[cyan]Found {len(wan_services)} WAN-related services:[/cyan]")

    for service_name in wan_services:
        console.print(f"\n[bold magenta]{service_name}[/bold magenta]")
        service = fc.services[service_name]

        # Look for actions that might return status/info
        status_actions = [a for a in service.actions.keys() if 'Status' in a or 'Info' in a]

        for action_name in status_actions:
            try:
                console.print(f"  [yellow]Trying {action_name}...[/yellow]")
                result = fc.call_action(service_name, action_name)

                # Check if result contains uptime-related fields
                uptime_fields = [k for k in result.keys() if 'Uptime' in k or 'Time' in k or 'Connected' in k]

                if uptime_fields:
                    console.print(f"    [green]SUCCESS! Found fields:[/green]")
                    for field in uptime_fields:
                        console.print(f"      {field}: {result[field]}")
                else:
                    console.print(f"    [dim]No uptime fields in result[/dim]")

            except Exception as e:
                console.print(f"    [red]Failed: {str(e)[:80]}[/red]")

if __name__ == "__main__":
    main()
