import nmap
import re

def remove_protocol(targets):
    """
    Remove "http://" and "https://" from each target in the list.
    """
    return [re.sub(r'^https?://', '', target) for target in targets]

def nmap_scan(targets, output_file):
    """
    Run an Nmap scan for each target using bug bounty relevant parameters and save results to a file.
    """
    nm = nmap.PortScanner()
    with open(output_file, 'w') as f:
        for target in targets:
            f.write(f"Scanning {target}...\n")
            nm.scan(hosts=target, arguments='-sC -sV -T4 -p-')
            f.write(nm.command_line() + '\n')
            f.write(str(nm.scaninfo()) + '\n')
            for host in nm.all_hosts():
                f.write(f"Host: {host}\n")
                f.write(f"State: {nm[host].state()}\n")
                for proto in nm[host].all_protocols():
                    f.write(f"Protocol: {proto}\n")
                    lport = nm[host][proto].keys()
                    sorted(lport)
                    for port in lport:
                        f.write(f"Port: {port}\tState: {nm[host][proto][port]['state']}\n")
            f.write("\n")  # Add a newline for separation between scans

def main():
    targets_file = input("Enter the path to your targets file: ")
    output_file = input("Enter the path for the output results file: ")
    
    try:
        with open(targets_file, 'r') as f:
            targets = [line.strip() for line in f.readlines()]
            targets = remove_protocol(targets)
            nmap_scan(targets, output_file)
            print(f"Scan results saved to {output_file}")
    except FileNotFoundError:
        print("Targets file not found.")

if __name__ == "__main__":
    main()