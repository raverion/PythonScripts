import pandas as pd
import re
from typing import Dict, List, Tuple
import os

class ATELogAnalyzer:
    def __init__(self, reference_file: str, retest_file: str):
        self.reference_file = reference_file
        self.retest_file = retest_file
        self.die_data = {}  # Store processed data for each die

    def parse_measurement(self, value_str: str) -> float:
        """Safely parse measurement values, handling special cases."""
        try:
            # Remove any whitespace
            value_str = value_str.strip()
            
            # Handle special cases
            if value_str == 'not specified' or value_str == '':
                return float('nan')
            
            # Try to convert to float
            return float(value_str)
        except ValueError:
            print(f"Warning: Could not parse measurement value: {value_str}")
            return float('nan')

    def parse_file(self, filename: str) -> Dict:
        """Parse ATE log file and extract test data for each die."""
        parts_data = {}
        current_part = None
        
        with open(filename, 'r') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            try:
                # Check for new part section
                if "TEST RESULTS PART" in line:
                    continue
                    
                # Extract part identifiers and result info
                part_match = re.search(r'Part ID:\s*"(\d+)"\s*Bin:\s*(\d+)\s*Site:\s*(\d+)\s*XPos:\s*(\d+)\s*YPos:\s*(\d+)\s*Wafer:\s*(\d+)', line)
                if part_match:
                    part_id, bin_num, site_num, x_pos, y_pos, wafer = part_match.groups()
                    current_part = (int(x_pos), int(y_pos), int(wafer))
                    if current_part not in parts_data:
                        parts_data[current_part] = {
                            'result': f"Part {part_id} Bin {bin_num} Site {site_num}",
                            'measurements': []
                        }
                    continue
                
                # Extract test measurements
                test_match = re.search(r'^\s*(\d+)\s*\((.*?)\)\s*([-+]?\d*\.?\d*(?:[Ee][-+]?\d+)?)\s*([^\s<]*)\s*<\s*([F]?)\s*>\s*MIN\s*:\s*([-+]?\d*\.?\d*(?:[Ee][-+]?\d+)?|not specified)\s*MAX\s*:\s*([-+]?\d*\.?\d*(?:[Ee][-+]?\d+)?|not specified)', line)
                if test_match and current_part:
                    test_num, test_name, measurement, unit, fail_flag, min_limit, max_limit = test_match.groups()
                    
                    # Only process if it's a fail in reference file or if it's the retest file
                    if fail_flag == 'F' or filename == self.retest_file:
                        try:
                            measurement_value = self.parse_measurement(measurement)
                            min_value = self.parse_measurement(min_limit)
                            max_value = self.parse_measurement(max_limit)
                            
                            parts_data[current_part]['measurements'].append({
                                'test_num': int(test_num),
                                'test_name': test_name.strip(),
                                'measurement': measurement_value,
                                'unit': unit.strip(),
                                'min_limit': min_value,
                                'max_limit': max_value,
                                'fail': fail_flag == 'F'
                            })
                        except ValueError as e:
                            print(f"Warning: Error processing measurement in file {filename}, line {line_num}: {e}")
                            continue
                            
            except Exception as e:
                print(f"Warning: Error processing line {line_num} in file {filename}: {e}")
                print(f"Line content: {line.strip()}")
                continue
        
        return parts_data

    def compare_logs(self) -> pd.DataFrame:
        """Compare reference and retest logs and generate comparison data."""
        reference_data = self.parse_file(self.reference_file)
        retest_data = self.parse_file(self.retest_file)
        
        comparison_rows = []
        
        for die_pos, ref_info in reference_data.items():
            # Add die identifier row
            x_pos, y_pos, wafer = die_pos
            comparison_rows.append({
                'Die Location': f"X{x_pos} Y{y_pos} W{wafer}",
                'First Insertion': ref_info['result'],
                'Retest': retest_data.get(die_pos, {}).get('result', 'Not Found')
            })
            
            # Add measurement comparison rows
            for ref_meas in ref_info['measurements']:
                retest_meas = None
                if die_pos in retest_data:
                    for meas in retest_data[die_pos]['measurements']:
                        if meas['test_num'] == ref_meas['test_num']:
                            retest_meas = meas
                            break
                
                # Format measurement string with handling for 'nan' values
                def format_measurement(meas):
                    if pd.isna(meas['measurement']):
                        measurement_str = "N/A"
                    else:
                        measurement_str = f"{meas['measurement']}"
                    
                    min_limit = "not specified" if pd.isna(meas['min_limit']) else f"{meas['min_limit']}"
                    max_limit = "not specified" if pd.isna(meas['max_limit']) else f"{meas['max_limit']}"
                    
                    return (f"Test {meas['test_num']} {meas['test_name']}: "
                           f"{measurement_str} {meas['unit']} "
                           f"(MIN: {min_limit} MAX: {max_limit})")
                
                ref_text = format_measurement(ref_meas)
                retest_text = format_measurement(retest_meas) if retest_meas else ''
                
                comparison_rows.append({
                    'Die Location': '',
                    'First Insertion': ref_text,
                    'Retest': retest_text
                })
            
            # Add blank row between dies
            comparison_rows.append({
                'Die Location': '',
                'First Insertion': '',
                'Retest': ''
            })
        
        return pd.DataFrame(comparison_rows)

    def generate_report(self, output_file: str):
        """Generate Excel report comparing the test results."""
        comparison_df = self.compare_logs()
        
        # Write to Excel with formatting
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            comparison_df.to_excel(writer, index=False, sheet_name='Retest Comparison')
            
            # Get the worksheet
            worksheet = writer.sheets['Retest Comparison']
            
            # Adjust column widths
            worksheet.column_dimensions['A'].width = 15
            worksheet.column_dimensions['B'].width = 50
            worksheet.column_dimensions['C'].width = 50
        
        print(f"\nReport generated successfully: {output_file}")

def get_valid_filename(prompt: str) -> str:
    """Get a valid filename from user input."""
    while True:
        filename = input(prompt).strip()
        if os.path.exists(filename):
            return filename
        print(f"Error: File '{filename}' not found. Please enter a valid filename.")

def get_output_filename(prompt: str) -> str:
    """Get output filename from user input."""
    while True:
        filename = input(prompt).strip()
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        if os.path.exists(filename):
            overwrite = input(f"File '{filename}' already exists. Overwrite? (y/n): ").lower()
            if overwrite == 'y':
                return filename
        else:
            return filename

def main():
    print("\nATE Test Log Comparison Tool")
    print("============================")
    
    # Get input filenames
    print("\nPlease enter the filenames for analysis:")
    ref_file = get_valid_filename("First insertion/touchdown datalog file: ")
    retest_file = get_valid_filename("Retest datalog file: ")
    
    # Get output filename
    output_file = get_output_filename("\nEnter output Excel filename (default extension: .xlsx): ")
    
    print("\nProcessing files...")
    try:
        analyzer = ATELogAnalyzer(ref_file, retest_file)
        analyzer.generate_report(output_file)
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        return
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()