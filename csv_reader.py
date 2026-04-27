# This script read CSV file and assume that the first row contain the domains and URLs.
# It extract them to a file (scope.txt) and clean each line to have valid domains in "domain.txt" file 

import csv
import re

def extract_domains(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        domains = [row[0] for row in reader]

    with open('scope.txt', 'w') as f:
        for domain in domains:
            f.write(domain + '\n')

def clean_domains(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            line = line.strip()
            # Remove protocol
            if line.startswith('http://') or line.startswith('https://'):
                line = line.split('://')[-1]
            # Remove www.
            if line.startswith('www.'):
                line = line[4:]
            # Remove everything after the first '/' or ' ' (space)
            line = re.split(r'[ /]', line)[0]
            f_out.write(line + '\n')

def main():
    csv_file = input("Enter the name of the CSV file: ")
    extract_domains(csv_file)
    print("Domain names have been extracted and saved to scope.txt")
    
    clean_domains('scope.txt', 'targets.txt')
    print("Cleaned domain names have been saved to targets.txt")

if __name__ == "__main__":
    main()