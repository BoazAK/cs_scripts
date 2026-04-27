# This script have some goals :
# - Find subdomains
# - Extract 200 status subdomains
# - Extract 404 status subdomains
# - Look for CNAMEs of the 404 subdomains

import subprocess

# Define the file paths
targets_file = input("Write the target file. (Example : targets.txt) : ")
subdomains_file = "subdomains.txt"
subdomains_200_file = "200_subdomains.txt"
subdomains_404_file = "404_subdomains.txt"
cname_file = "cname.txt"

# Step 1: Run subfinder
subfinder_command = f"subfinder -dL {targets_file} -o {subdomains_file}"
subprocess.run(subfinder_command, shell=True, check=True)
print(f"Subfinder completed. Results saved to {subdomains_file}.")

# Step 2: Run httpx for 200 status code
httpx_200_command = f"httpx -l {subdomains_file} -mc 200 -o {subdomains_200_file}"
subprocess.run(httpx_200_command, shell=True, check=True)
print(f"httpx completed for 200 status code. Results saved to {subdomains_200_file}.")

# Step 3: Run httpx for 404 status code
httpx_404_command = f"httpx -l {subdomains_file} -mc 404 -o {subdomains_404_file}"
subprocess.run(httpx_404_command, shell=True, check=True)
print(f"httpx completed for 404 status code. Results saved to {subdomains_404_file}.")

# Step 4: Run dig on each line in the 404_subdomains.txt file and save to cname.txt if CNAME exists
with open(subdomains_404_file, "r") as infile, open(cname_file, "w") as outfile:
    for line in infile:
        domain = line.strip()
        if domain:
            dig_command = f"dig ns +short {domain}"
            result = subprocess.run(dig_command, shell=True, capture_output=True, text=True)
            cname = result.stdout.strip()
            if cname:  # Only write if CNAME exists
                outfile.write(f"{domain}: {cname}\n\n")

print(f"dig command completed. CNAME results saved to {cname_file}.")
