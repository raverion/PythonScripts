import pandas as pd
import re
from pathlib import Path

class TestResult:
    def __init__(self, part_id, bin_num, site_num, x_pos, y_pos, wafer):
        self.part_id = part_id
        self.bin_num = bin_num
        self.site_num = site_num
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.wafer = wafer
        self.fail_measurements = []

class FailMeasurement:
    def __init__(self, test_num, test_name, measurement, unit, min_limit, max_limit):
        self.test_num = test_num
        self.test_name = test_name
        self.measurement = measurement
        self.unit = unit
        self.min_limit = min_limit
        self.max_limit = max_limit

def parse_part_header(header_line):
    # Extract part information using regex
    part_pattern = r'Part ID:\s*"(\d+)"\s*Bin:\s*(\d+)\s*Site:\s*(\d+)\s*XPos:\s*(\d+)\s*YPos:\s*(\d+)\s*Wafer:\s*(\d+)'
    match = re.search(part_pattern, header_line)
    if match:
        return TestResult(
            part_id=match.group(1),
            bin_num=int(match.group(2)),
            site_num=int(match.group(3)),
            x_pos=int(match.group(4)),
            y_pos=int(match.group(5)),
            wafer=int(match.group(6))
        )
    return None

def parse_measurement_line(line):
    # Extract measurement information using regex
    measurement_pattern = r'^\s*(\d+)\s+\((.*?)\)\s+([-\d.]+)\s+(\w+)?\s*<\s*(F)?\s*>\s*MIN\s*:\s*([-\d.]+|not specified)\s*MAX\s*:\s*([-\d.]+|not specified)'
    match = re.search(measurement_pattern, line)
    if match and match.group(5) == 'F':  # Only capture failing measurements
        return FailMeasurement(
            test_num=int(match.group(1)),
            test_name=match.group(2).strip(),
            measurement=float(match.group(3)),
            unit=match.group(4) if match.group(4) else '',
            min_limit=match.group(6),
            max_limit=match.group(7)
        )
    return None

def read_datalog(file_path):
    results = {}
    current_part = None
    
    with open(file_path, 'r') as f:
        for line in f:
            if 'TEST RESULTS PART' in line:
                next_line = next(f)
                current_part = parse_part_header(next_line)
                if current_part:
                    key = (current_part.x_pos, current_part.y_pos, current_part.wafer)
                    results[key] = current_part
            elif current_part:
                measurement = parse_measurement_line(line)
                if measurement:
                    current_part.fail_measurements.append(measurement)
    
    return results

def find_matching_measurement(test_num, retest_lines):
    measurement_pattern = rf'^\s*{test_num}\s+\((.*?)\)\s+([-\d.]+)\s+(\w+)?\s*<\s*\w*\s*>\s*MIN\s*:\s*([-\d.]+|not specified)\s*MAX\s*:\s*([-\d.]+|not specified)'
    for line in retest_lines:
        match = re.search(measurement_pattern, line)
        if match:
            return FailMeasurement(
                test_num=test_num,
                test_name=match.group(1).strip(),
                measurement=float(match.group(2)),
                unit=match.group(3) if match.group(3) else '',
                min_limit=match.group(4),
                max_limit=match.group(5)
            )
    return None

def compare_datalogs(first_file, retest_file, output_file):
    # Read both datalogs
    first_results = read_datalog(first_file)
    
    # Create Excel writer
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Comparison Results')
    
    # Format headers
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})
    worksheet.write(0, 0, 'Die Location (X, Y, Wafer)', header_format)
    worksheet.write(0, 1, 'First Insertion Results', header_format)
    worksheet.write(0, 2, 'Retest Results', header_format)
    
    row = 1
    
    # Process each failing part from first insertion
    for (x, y, wafer), first_result in first_results.items():
        # Write die location
        worksheet.write(row, 0, f"X:{x}, Y:{y}, W:{wafer}")
        
        # Write first insertion results
        worksheet.write(row, 1, f"Part ID: {first_result.part_id}, Bin: {first_result.bin_num}, Site: {first_result.site_num}")
        
        # Find corresponding retest results
        retest_part = None
        retest_measurements = {}
        
        with open(retest_file, 'r') as f:
            retest_lines = []
            capturing = False
            for line in f:
                if f'XPos: {x:>6}   YPos: {y:>6}   Wafer: {wafer}' in line:
                    capturing = True
                    retest_lines = [line]
                elif capturing and 'TEST RESULTS PART' in line:
                    capturing = False
                elif capturing:
                    retest_lines.append(line)
                    if line.strip() == '':
                        capturing = False
        
        if retest_lines:
            header_line = next((line for line in retest_lines if 'Part ID' in line), None)
            if header_line:
                retest_part = parse_part_header(header_line)
                worksheet.write(row, 2, f"Part ID: {retest_part.part_id}, Bin: {retest_part.bin_num}, Site: {retest_part.site_num}")
        
        row += 1
        
        # Write measurements
        for fail_meas in first_result.fail_measurements:
            # Write first insertion measurement
            worksheet.write(row, 1, f"Test {fail_meas.test_num}: {fail_meas.test_name}\n"
                                  f"Measurement: {fail_meas.measurement} {fail_meas.unit}\n"
                                  f"Limits: MIN={fail_meas.min_limit}, MAX={fail_meas.max_limit}")
            
            # Find and write corresponding retest measurement
            if retest_lines:
                retest_meas = find_matching_measurement(fail_meas.test_num, retest_lines)
                if retest_meas:
                    worksheet.write(row, 2, f"Test {retest_meas.test_num}: {retest_meas.test_name}\n"
                                          f"Measurement: {retest_meas.measurement} {retest_meas.unit}\n"
                                          f"Limits: MIN={retest_meas.min_limit}, MAX={retest_meas.max_limit}")
            row += 1
        
        row += 1  # Add space between parts
    
    # Adjust column widths
    worksheet.set_column(0, 0, 20)
    worksheet.set_column(1, 2, 50)
    
    writer.close()

def main():
    # Get file paths from user
    first_file = input("Enter the path to the first insertion datalog file: ")
    retest_file = input("Enter the path to the retest datalog file: ")
    output_file = input("Enter the desired output Excel file path: ")
    
    try:
        compare_datalogs(first_file, retest_file, output_file)
        print(f"\nComparison completed successfully. Results saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()