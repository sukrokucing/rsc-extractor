import pandas as pd
from datetime import datetime
import re
import json
import os

# Captures everything before '=' and trims spaces after '='
def trim_whitespace_after_equal(line):
    # Use regex to find all key=value pairs and trim spaces after '='
    return re.sub(r'(\w+=)\s+', r'\1', line)

# Load patterns from pattern.json
def load_patterns(pattern_file):
    with open(pattern_file, 'r') as file:
        patterns = json.load(file)
    return patterns['patterns']

# Load rsc file
def load_rsc_file(rsc_file):
    with open(rsc_file, 'r') as file:
        rsc_text = file.read()
    return rsc_text

# Process the rsc file
def process_rsc_file(rsc_file):
    text = load_rsc_file(rsc_file)
    lines = text.splitlines()
    output_lines = []
    current_line = ""

    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace
        if line.startswith("add"):
            if current_line:
                output_lines.append(current_line.strip())
            current_line = line
        elif line.endswith("\\"):  # Continuation line
            current_line += " " + line.replace("\\n", "")  # Append the line without '\'
        else:
            current_line += " " + line  # Append the rest of the line

    # Add the last accumulated line
    if current_line:
        output_lines.append(current_line.strip())

    # Trim whitespace after '='
    output_lines = [trim_whitespace_after_equal(line.replace("\\ ", "")) for line in output_lines]

    # Join all output lines into a single string
    return "\n".join(output_lines)

# Extract data based on patterns
def extract_data(processed, patterns):
    result = []  # Store the result

    for line in processed.splitlines():
        data = {}
        for pattern in patterns:
            key_value_pattern = re.compile(pattern['pattern'])
            matches = key_value_pattern.findall(line)
            for match in matches:
                key = pattern['name']
                value = match[0] if match[0] else match[1]
                data[key] = value.strip('"')
        if data:
            data['ip_address']=''
            data['paket']='150K'
            # check if data has key "burst-limit"
            if 'burst-limit' in data:
                # check if burst-limit contain 10M
                if '10M' in data['burst-limit']:
                    # add new key-value pair to data "paket"
                    data['paket'] = '150K'
                elif '20M' in data['burst-limit']:
                    data['paket'] = '200K'
                elif '30M' in data['burst-limit']:
                    data['paket'] = '300K'
            if 'target' in data:
                # split string in 'target' by '/' and get second array
                data['ip_address'] = data['target'].split('/')[0]
            result.append(data)

    return result

# Create Excel file
def create_excel_file(result, patterns, output_file):
    # Create column from pattern['name']
    columns = [pattern['name'] for pattern in patterns]

    # add new column 'ip_address' and 'paket'
    columns.append('ip_address')
    columns.append('paket')

    # Create DataFrame
    df = pd.DataFrame(result, columns=columns)

    # Save the Excel file with the first row frozen and auto-fit column width
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        worksheet = writer.sheets['Sheet1']
        worksheet.freeze_panes(1, 0)

    print(f'{output_file} created')

if __name__ == "__main__":
    current_dir = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    rsc_file = f'{current_dir}/raws.rsc'
    pattern_file = f'{current_dir}/patterns.json'
    output_file = f'{current_dir}/output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

    # Load patterns
    patterns = load_patterns(pattern_file)

    # Process rsc file
    processed = process_rsc_file(rsc_file)

    # Extract data
    result = extract_data(processed, patterns)

    # Create Excel file
    create_excel_file(result, patterns, output_file)
