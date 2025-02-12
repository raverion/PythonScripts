import pandas as pd
import re

def parse_datalog(filename):
    """Parses the datalog file and returns a dictionary with part identifiers as keys."""
    data = {}
    with open(filename, 'r') as file:
        content = file.read()
    
    parts = re.split(r'\*+ TEST RESULTS PART \d+ \*+', content)[1:]
    
    for part in parts:
        header_match = re.search(r'Part ID:\s+"(\d+)"\s+Bin:\s+(\d+)\s+Site:\s+(\d+)\s+XPos:\s+(-?\d+)\s+YPos:\s+(-?\d+)\s+Wafer:\s+(\d+)', part)
        if not header_match:
            continue
        
        part_id, bin_num, site, xpos, ypos, wafer = header_match.groups()
        part_key = (xpos, ypos, wafer)
        result = f"Part ID: {part_id} Bin: {bin_num} Site: {site}"
        
        fail_tests = []
        test_matches = re.findall(r'(\d+) \((.*?)\).*?\)\s+([-\d\.]+)\s+\w+\s+<\s*(F?)\s*>\s+MIN\s*:\s*([-\d\.]+)\s*MAX\s*:\s*([-\d\.]+)', part)
        
        for test in test_matches:
            test_num, test_name, measurement, fail_flag, min_val, max_val = test
            if fail_flag:  # Only store failing tests
                fail_tests.append((test_num, test_name, measurement, min_val, max_val))
        
        data[part_key] = {'result': result, 'fail_tests': fail_tests}
    
    return data

def compare_datalogs(first_insertion_file, retest_file, output_file):
    """Compares first insertion and retest datalogs and writes results to an Excel file."""
    first_data = parse_datalog(first_insertion_file)
    retest_data = parse_datalog(retest_file)
    
    output_rows = []
    
    for part_key, first_part in first_data.items():
        xpos, ypos, wafer = part_key
        first_result = first_part['result']
        fail_tests = first_part['fail_tests']
        
        retest_result = retest_data.get(part_key, {}).get('result', 'Not Found')
        retest_fail_tests = {test[0]: test for test in retest_data.get(part_key, {}).get('fail_tests', [])}
        
        output_rows.append([xpos, ypos, wafer, first_result, retest_result])
        
        for test in fail_tests:
            test_num, test_name, measurement, min_val, max_val = test
            retest_measurement = retest_fail_tests.get(test_num, ('', '', ''))[2]
            output_rows.append(['', '', '', f"{test_num} {test_name} {measurement} [{min_val}, {max_val}]", retest_measurement])
    
    df = pd.DataFrame(output_rows, columns=['XPos', 'YPos', 'Wafer', 'First Insertion', 'Retest'])
    df.to_excel(output_file, index=False)
    print(f"Comparison saved to {output_file}")

if __name__ == "__main__":
    # Hardcoded file names (change these if needed)
    first_insertion = "w01a.txt"
    retest = "w01b.txt"
    output = "output.xlsx"

    # Uncomment the lines below if you prefer user input instead
    # first_insertion = input("Enter first insertion datalog file: ")
    # retest = input("Enter retest datalog file: ")
    # output = input("Enter output Excel file name: ")

    compare_datalogs(first_insertion, retest, output)
