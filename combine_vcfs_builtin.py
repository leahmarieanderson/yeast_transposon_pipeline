#!/usr/bin/env python3

import csv
import argparse
import os
import glob
import re
from collections import defaultdict, Counter

def read_vcf(filepath):
    """Read VCF file, skipping header lines starting with ##"""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find the header line that starts with #CHROM
    header_idx = None
    for line_number, line in enumerate(lines):
        if line.startswith('#CHROM'):
            header_idx = line_number
            break

    if header_idx is None:
        raise ValueError(f"No #CHROM header found in {filepath}")

    # Get column names from header
    header_line = lines[header_idx].strip()
    columns = header_line.split('\t')

    # Parse data rows
    data_rows = []
    for line in lines[header_idx + 1:]:
        if line.strip():  # Skip empty lines
            row_data = line.strip().split('\t')
            # Create dictionary for this row
            row_dict = {}
            for i, col_name in enumerate(columns):
                if i < len(row_data):
                    row_dict[col_name] = row_data[i]
                else:
                    row_dict[col_name] = ''
            data_rows.append(row_dict)

    # Extract sample name and tool from filename using regular expressions
    filename = os.path.basename(filepath)
    sample_match = re.search(r'(.+?)_R1', filename)
    tool_match = re.search(r'001_(.+?)_nonredundant', filename)

    sample_name = sample_match.group(1) if sample_match else "unknown"
    tool_name = tool_match.group(1) if tool_match else "unknown"

    # Add sample, tool, and location info to each row
    for row in data_rows:
        row['sample'] = sample_name
        row['tool'] = tool_name
        row['location'] = f"{row['#CHROM']}:{row['POS']}"

    return data_rows, columns

def combine_vcfs(input_dir, min_callers=3, ancestor_sample=None, output_prefix="filtered_te"):
    """Combine VCF files and filter by minimum number of callers"""

    # Find all VCF files
    vcf_pattern = os.path.join(input_dir, "*.vcf")
    vcf_files = glob.glob(vcf_pattern)

    if not vcf_files:
        raise ValueError(f"No VCF files found in {input_dir}")

    print(f"Found {len(vcf_files)} VCF files")

    # Read and combine all VCF files
    all_rows = []
    all_columns = set()

    for vcf_file in vcf_files:
        try:
            rows, columns = read_vcf(vcf_file)
            all_rows.extend(rows)
            all_columns.update(columns)
            print(f"Processed: {os.path.basename(vcf_file)}")
        except Exception as e:
            print(f"Error processing {vcf_file}: {e}")

    if not all_rows:
        raise ValueError("No VCF files could be processed successfully")

    # Convert to list and add our custom columns
    all_columns = list(all_columns)
    if 'sample' not in all_columns:
        all_columns.append('sample')
    if 'tool' not in all_columns:
        all_columns.append('tool')
    if 'location' not in all_columns:
        all_columns.append('location')

    print(f"Total VCF entries processed: {len(all_rows)}")

    # Filter by minimum number of callers per sample per location
    # Group by sample and location, count tools
    sample_location_counts = defaultdict(list)
    for row in all_rows:
        key = (row['sample'], row['location'])
        sample_location_counts[key].append(row)

    # Filter groups that have at least min_callers
    filtered_rows = []
    for key, rows in sample_location_counts.items():
        if len(rows) >= min_callers:
            filtered_rows.extend(rows)

    print(f"Entries passing {min_callers}+ caller filter: {len(filtered_rows)}")

    # Handle ancestor filtering if specified
    if ancestor_sample:
        # Find high-confidence ancestor locations (those with min_callers+ support)
        ancestor_locations = set()
        for key, rows in sample_location_counts.items():
            sample, location = key
            if sample == ancestor_sample and len(rows) >= min_callers:
                ancestor_locations.add(location)

        # Filter out these locations from all samples
        filtered_rows = [row for row in filtered_rows
                        if row['location'] not in ancestor_locations]
        print(f"Filtered out {len(ancestor_locations)} high-confidence ancestral locations")

    # Write all filtered calls
    output_all = f"{output_prefix}_all.txt"
    with open(output_all, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_columns, delimiter='\t')
        writer.writeheader()
        writer.writerows(filtered_rows)
    print(f"Wrote all filtered calls to: {output_all}")

    # Create unique locations (one entry per sample per location)
    unique_entries = {}
    for row in filtered_rows:
        key = (row['sample'], row['location'])
        if key not in unique_entries:
            unique_entries[key] = row

    unique_rows = list(unique_entries.values())

    output_unique = f"{output_prefix}_unique.txt"
    with open(output_unique, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_columns, delimiter='\t')
        writer.writeheader()
        writer.writerows(unique_rows)
    print(f"Wrote unique filtered calls to: {output_unique}")

    # Print summary statistics
    samples = set(row['sample'] for row in all_rows)
    tools = set(row['tool'] for row in all_rows)

    print(f"\nSummary:")
    print(f"Total VCF entries processed: {len(all_rows)}")
    print(f"Entries passing {min_callers}+ caller filter: {len(filtered_rows)}")
    print(f"Unique locations after filtering: {len(unique_rows)}")
    print(f"Samples processed: {len(samples)}")
    print(f"Tools used: {len(tools)}")

def main():
    parser = argparse.ArgumentParser(description="Combine VCF files and filter by minimum number of callers")
    parser.add_argument("input_dir", help="Directory containing VCF files")
    parser.add_argument("-m", "--min-callers", type=int, default=3,
                       help="Minimum number of callers required (default: 3)")
    parser.add_argument("-a", "--ancestor", type=str, default=None,
                       help="Name of ancestor sample to filter out (optional)")
    parser.add_argument("-o", "--output-prefix", type=str, default="filtered_te",
                       help="Output file prefix (default: filtered_te)")

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        raise ValueError(f"Input directory does not exist: {args.input_dir}")

    combine_vcfs(args.input_dir, args.min_callers, args.ancestor, args.output_prefix)

if __name__ == "__main__":
    main()