#!/usr/bin/env python3
"""
FritzBox PoC - Proof of concept to retrieve data from a FritzBox 7490
"""

import argparse
import time
import sys
from datetime import datetime
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzstatus import FritzStatus
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich_argparse import RichHelpFormatter

console = Console()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="FritzBox 7490 Data Retrieval PoC",
        formatter_class=RichHelpFormatter
    )
    parser.add_argument(
        "--ip",
        required=True,
        help="IP address of the FritzBox"
    )
    parser.add_argument(
        "--username",
        required=True,
        help="Username for FritzBox authentication"
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Password for FritzBox authentication"
    )
    parser.add_argument(
        "--suppress-services",
        action="store_true",
        default=True,
        help="Suppress the service list output (default: True)"
    )
    parser.add_argument(
        "--show-services",
        action="store_false",
        dest="suppress_services",
        help="Show the full service list output"
    )
    return parser.parse_args()


def echo_parameters(ip, username, password):
    """Echo the input parameters"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"\n[bold cyan]Timestamp:[/bold cyan] [green]{timestamp}[/green]")
    console.print("\n[bold cyan]Input Parameters:[/bold cyan]")
    console.print(f"  IP Address: [green]{ip}[/green]")
    console.print(f"  Username:   [green]{username}[/green]")
    console.print(f"  Password:   [green]{'*' * len(password)}[/green]\n")


def safe_get_attr(obj, attr, default="N/A"):
    """Safely get attribute from object, return default if not available"""
    try:
        value = getattr(obj, attr, default)
        return value if value is not None else default
    except Exception:
        return default


def format_bytes(bytes_value):
    """Format bytes into human-readable format (GB, TB, etc.)"""
    if bytes_value < 1024**3:  # Less than 1 GB
        return f"{bytes_value / (1024**2):.2f} MB"
    elif bytes_value < 1024**4:  # Less than 1 TB
        return f"{bytes_value / (1024**3):.2f} GB"
    else:
        return f"{bytes_value / (1024**4):.2f} TB"


def retrieve_fritzbox_data(ip, username, password, suppress_services=True):
    """Retrieve and display all available data from FritzBox"""

    data_start_time = time.time()
    total_bytes = 0

    try:
        # Connect to FritzBox
        console.print("[bold yellow]Connecting to FritzBox...[/bold yellow]")
        fc = FritzConnection(address=ip, user=username, password=password)
        fs = FritzStatus(fc=fc)

        # Get device information
        console.print("\n[bold magenta]Device Information:[/bold magenta]")
        device_info = Table(show_header=False, box=None)
        device_info.add_column("Property", style="cyan")
        device_info.add_column("Value", style="green")

        device_info.add_row("Model", fc.modelname)
        device_info.add_row("Firmware Version", fc.system_version)

        console.print(device_info)

        # Get connection status
        console.print("\n[bold magenta]Connection Status:[/bold magenta]")
        status_info = Table(show_header=False, box=None)
        status_info.add_column("Property", style="cyan")
        status_info.add_column("Value", style="green")

        # Use safe attribute access
        is_connected = safe_get_attr(fs, 'is_connected')
        is_linked = safe_get_attr(fs, 'is_linked')
        external_ip = safe_get_attr(fs, 'external_ip')
        max_bit_rate = safe_get_attr(fs, 'max_bit_rate')
        bytes_sent = safe_get_attr(fs, 'bytes_sent')
        bytes_received = safe_get_attr(fs, 'bytes_received')

        # Get uptime from WANIPConn1 service
        uptime_str = "N/A"
        connection_status = str(is_connected)

        try:
            result = fc.call_action('WANIPConn1', 'GetStatusInfo')

            if 'NewUptime' in result:
                uptime_seconds = result['NewUptime']
                connection_status = result.get('NewConnectionStatus', str(is_connected))

                # Calculate uptime in days, hours, minutes
                days = uptime_seconds // 86400
                hours = (uptime_seconds % 86400) // 3600
                minutes = (uptime_seconds % 3600) // 60
                uptime_str = f"{days}d {hours}h {minutes}m ({uptime_seconds:,} seconds)"
        except Exception:
            pass

        status_info.add_row("Connection Status", connection_status)
        status_info.add_row("Is Linked", str(is_linked))
        status_info.add_row("External IP", str(external_ip))
        status_info.add_row("Uptime", uptime_str)

        if max_bit_rate != "N/A" and isinstance(max_bit_rate, (list, tuple)) and len(max_bit_rate) >= 2:
            status_info.add_row("Max Bit Rate (Down)", f"{max_bit_rate[1] / 1000000:.2f} Mbps")
            status_info.add_row("Max Bit Rate (Up)", f"{max_bit_rate[0] / 1000000:.2f} Mbps")
        else:
            status_info.add_row("Max Bit Rate", str(max_bit_rate))

        if bytes_sent != "N/A":
            status_info.add_row("Bytes Sent", f"{bytes_sent:,} ({format_bytes(bytes_sent)})")
        else:
            status_info.add_row("Bytes Sent", "N/A")

        if bytes_received != "N/A":
            status_info.add_row("Bytes Received", f"{bytes_received:,} ({format_bytes(bytes_received)})")
        else:
            status_info.add_row("Bytes Received", "N/A")

        console.print(status_info)

        # Get network devices
        console.print("\n[bold magenta]Network Devices:[/bold magenta]")
        try:
            from fritzconnection.lib.fritzhosts import FritzHosts
            fh = FritzHosts(fc=fc)

            devices_table = Table(show_header=True, box=None)
            devices_table.add_column("Hostname", style="cyan")
            devices_table.add_column("Friendly Name", style="bright_cyan")
            devices_table.add_column("IPv4 Address", style="green")
            devices_table.add_column("IPv6 Address", style="blue")
            devices_table.add_column("MAC Address", style="yellow")
            devices_table.add_column("Status", style="magenta")
            devices_table.add_column("Interface", style="dim")

            # Get all hosts
            hosts = fh.get_hosts_info()

            online_count = 0
            for host in hosts:
                hostname = host.get('name', 'Unknown')
                ip = host.get('ip', 'N/A')
                mac = host.get('mac', 'N/A')
                status = "Online" if host.get('status') else "Offline"
                interface = host.get('interface_type', 'N/A')

                # Try to get friendly name and IPv6 address
                friendly_name = ''
                ipv6 = 'N/A'
                try:
                    if mac != 'N/A':
                        # Get friendly name
                        try:
                            result = fc.call_action('Hosts1', 'X_AVM-DE_GetFriendlyName', NewMACAddress=mac)
                            friendly_name = result.get('NewFriendlyName', '')
                        except:
                            pass
                except:
                    pass

                # Only show online devices by default, or show all if requested
                if host.get('status'):
                    devices_table.add_row(hostname, friendly_name, ip, ipv6, mac, status, interface)
                    online_count += 1

            console.print(f"[dim]Showing {online_count} online devices[/dim]")
            console.print(devices_table)

        except Exception as e:
            console.print(f"[red]Failed to retrieve network devices: {str(e)}[/red]")

        # Get all services and actions (only if not suppressed)
        if not suppress_services:
            console.print("\n[bold magenta]Available Services:[/bold magenta]")
            services = fc.services

            for service_name in sorted(services.keys()):
                service = services[service_name]

                # Create a panel for each service
                service_table = Table(show_header=True, box=None)
                service_table.add_column("Action", style="yellow")
                service_table.add_column("Arguments", style="dim")

                for action_name in sorted(service.actions.keys()):
                    action = service.actions[action_name]
                    args = ", ".join(action.arguments.keys()) if action.arguments else "None"
                    service_table.add_row(action_name, args)
                    total_bytes += len(str(action))

                console.print(Panel(service_table, title=f"[bold blue]{service_name}[/bold blue]", expand=False))
        else:
            console.print("\n[dim]Service list suppressed (use --show-services to display)[/dim]")

        data_end_time = time.time()
        data_retrieval_time = data_end_time - data_start_time

        return data_retrieval_time, total_bytes

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


def main():
    """Main entry point"""
    program_start_time = time.time()

    # Parse arguments
    args = parse_args()

    # Echo parameters
    echo_parameters(args.ip, args.username, args.password)

    # Retrieve data
    data_time, total_bytes = retrieve_fritzbox_data(args.ip, args.username, args.password, args.suppress_services)

    program_end_time = time.time()
    total_program_time = program_end_time - program_start_time

    # Display timing information
    console.print("\n[bold cyan]Performance Metrics:[/bold cyan]")
    metrics = Table(show_header=False, box=None)
    metrics.add_column("Metric", style="cyan")
    metrics.add_column("Value", style="green")

    metrics.add_row("Data Retrieval Time", f"{data_time:.3f} seconds")
    metrics.add_row("Total Bytes Retrieved", f"{total_bytes:,} bytes")
    metrics.add_row("Total Program Execution Time", f"{total_program_time:.3f} seconds")

    console.print(metrics)
    console.print()


if __name__ == "__main__":
    main()
