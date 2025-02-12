import pandas as pd
import re
from typing import Dict, List, Tuple

class ATELogAnalyzer:
    def __init__(self, reference_file: str, retest_file: str):
        self.reference_file = reference_file
        self.retest_file = retest_file
        self.die_data = {}  # Store processed data for each die

    def parse_file(self, filename: str) -> Dict:
        """Parse ATE log file and extract test data for each die."""
        parts_data = {}
        current_part = None
        
        with open(filename, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
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
            test_match = re.search(r'^\s*(\d+)\s*\((.*?)\)\s*([-\d.]+)\s*([^\s<]+)\s*<\s*([F]?)\s*>\s*MIN\s*:\s*([-\d.]+|not specified)\s*MAX\s*:\s*([-\d.]+|not specified)', line)
            if test_match and current_part:
                test_num, test_name, measurement, unit, fail_flag, min_limit, max_limit = test_match.groups()
                if fail_flag == 'F' or filename == self.retest_file:  # Include all tests for retest file
                    parts_data[current_part]['measurements'].append({
                        'test_num': int(test_num),
                        'test_name': test_name.strip(),
                        'measurement': float(measurement),
                        'unit': unit,
                        'min_limit': min_limit if min_limit == 'not specified' else float(min_limit),
                        'max_limit': max_limit if max_limit == 'not specified' else float(max_limit),
                        'fail': fail_flag == 'F'
                    })
        
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
                
                ref_text = (f"Test {ref_meas['test_num']} {ref_meas['test_name']}: "
                           f"{ref_meas['measurement']} {ref_meas['unit']} "
                           f"(MIN: {ref_meas['min_limit']} MAX: {ref_meas['max_limit']})")
                
                retest_text = ''
                if retest_meas:
                    retest_text = (f"Test {retest_meas['test_num']} {retest_meas['test_name']}: "
                                 f"{retest_meas['measurement']} {retest_meas['unit']} "
                                 f"(MIN: {retest_meas['min_limit']} MAX: {retest_meas['max_limit']})")
                
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

def main():
    # Example usage
    analyzer = ATELogAnalyzer('w01a.txt', 'w01b.txt')
    analyzer.generate_report('retest_comparison.xlsx')

if __name__ == "__main__":
    main()