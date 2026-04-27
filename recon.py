import subprocess
import re
import sys

COMMON_SERVICES = {
    "21": "ftp",
    "22": "ssh",
    "23": "telnet",
    "25": "smtp",
    "53": "dns",
    "80": "http",
    "110": "pop3",
    "139": "smb",
    "143": "imap",
    "443": "https",
    "445": "smb",
    "3306": "mysql",
    "3389": "rdp",
    "8080": "http"
}


def print_banner():
    print("=" * 60)
    print("        Automated Nmap Enumeration Script (CTF)")
    print("=" * 60)

    print("\n[+] This script performs the following actions:\n")

    print("  1. TCP quick scan (top ports) with -T4 -Pn")
    print("  2. Full TCP port scan (-p-) with -T4 -Pn")
    print("  3. Detailed scan (-sCV -A) on discovered ports")
    print("  4. UDP scan (top 100 ports)")
    print("  5. Directory fuzzing on detected web services")
    print("  6. Generates access suggestions for common services\n")

    print("[+] Output files generated:\n")

    print("  - scan_simple.txt")
    print("      -> Result of quick TCP scan (fast overview)")

    print("  - scan_all_ports.txt")
    print("      -> Result of full TCP scan (all ports)")

    print("  - scan_detailed.txt")
    print("      -> Detailed scan on open ports (services, versions, OS)")

    print("  - scan_udp.txt")
    print("      -> UDP scan (top 100 ports)")

    print("  - access_simple.txt")
    print("      -> Suggested commands after quick scan")

    print("  - access_detailed.txt")
    print("      -> Suggested commands after full analysis")

    print("  - fuzz_<port>.txt")
    print("      -> Directory fuzzing results per web port\n")

    print("=" * 60 + "\n")


def run_nmap(command, output_file):
    print(f"\n[+] Running: {' '.join(command)}\n")

    with open(output_file, "w") as f:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        for line in process.stdout:
            print(line, end="")
            f.write(line)

        process.wait()

    print(f"\n[+] Results saved in {output_file}\n")


def extract_ports(file):
    ports = []

    with open(file, "r") as f:
        for line in f:
            match = re.match(r"(\d+)/tcp\s+open", line)
            if match:
                ports.append(match.group(1))

    return ports


def generate_access_file(target, ports, filename):
    print("[+] Generating access suggestions...")

    with open(filename, "w") as f:
        for port in ports:
            service = COMMON_SERVICES.get(port)

            if not service:
                continue

            if service == "ssh":
                f.write(f"ssh user@{target} -p {port}\n")

            elif service == "ftp":
                f.write(f"ftp {target} {port}\n")

            elif service == "telnet":
                f.write(f"telnet {target} {port}\n")

            elif service in ["http", "https"]:
                proto = "https" if port == "443" else "http"
                f.write(f"{proto}://{target}:{port}\n")

            elif service == "smb":
                f.write(f"smbclient -L //{target} -p {port} -N\n")

            elif service == "rdp":
                f.write(f"xfreerdp /v:{target}:{port}\n")

            elif service == "mysql":
                f.write(f"mysql -h {target} -P {port} -u root -p\n")

    print(f"[+] Access suggestions saved in {filename}\n")
    

def run_web_fuzzing(target, ports):
    print("[+] Checking for web services...")

    web_ports = []
    for port in ports:
        if port in ["80", "443", "8080", "8000", "8888"]:
            web_ports.append(port)

    if not web_ports:
        print("[-] No web services found.\n")
        return

    for port in web_ports:
        proto = "https" if port == "443" else "http"
        url = f"{proto}://{target}:{port}"

        output_file = f"fuzz_{port}.txt"

        print(f"[+] Running directory fuzzing on {url}\n")

        command = [
            "gobuster", "dir",
            "-u", url,
            "-w", "/usr/share/wordlists/dirb/common.txt",
            "-t", "50",
            "-q"
        ]

        with open(output_file, "w") as f:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in process.stdout:
                print(line, end="")
                f.write(line)

            process.wait()

        print(f"\n[+] Fuzzing results saved in {output_file}\n")


def main():
    print_banner()
    
    if len(sys.argv) != 2:
        print("Usage: python script.py <target>")
        sys.exit(1)

    target = sys.argv[1]

    # 1. Scan simple TCP
    run_nmap(
        ["nmap", "-T4", "-Pn", target],
        "scan_simple.txt"
    )

    ports_simple = extract_ports("scan_simple.txt")
    generate_access_file(target, ports_simple, "access_simple.txt")
    
    # Fuzzing simple scan
    if ports_simple:
        run_web_fuzzing(target, ports_simple)

    # 2. Scan tous les ports TCP
    run_nmap(
        ["nmap", "-p-", "-T4", "-Pn", target],
        "scan_all_ports.txt"
    )

    ports_all = extract_ports("scan_all_ports.txt")

    if not ports_all:
        print("[-] No open TCP ports found.")
        sys.exit(1)

    ports_str = ",".join(ports_all)
    print(f"[+] Open TCP ports: {ports_str}")
    
    # Fuzzing scan détaillé
    if ports_all:
        run_web_fuzzing(target, ports_all)

    # 3. Scan détaillé TCP
    run_nmap(
        ["nmap", "-sCV", "-A", "-T4", "-Pn", "-p", ports_str, target],
        "scan_detailed.txt"
    )

    generate_access_file(target, ports_all, "access_detailed.txt")

    # 4. Scan UDP (rapide)
    run_nmap(
        ["nmap", "-sU", "--top-ports", "100", "-T4", "-Pn", target],
        "scan_udp.txt"
    )


if __name__ == "__main__":
    main()