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
    """Process VCF files and create filtered output for each sample separately"""

    # Find all VCF files
    vcf_pattern = os.path.join(input_dir, "*.vcf")
    vcf_files = glob.glob(vcf_pattern)

    if not vcf_files:
        raise ValueError(f"No VCF files found in {input_dir}")

    print(f"Found {len(vcf_files)} VCF files")

    # Read and organize all VCF files by sample
    samples_data = defaultdict(list)
    all_columns = set()

    for vcf_file in vcf_files:
        try:
            rows, columns = read_vcf(vcf_file)
            all_columns.update(columns)

            if rows:  # Only process if we got data
                sample_name = rows[0]['sample']  # All rows from same file have same sample
                samples_data[sample_name].extend(rows)
                print(f"Processed: {os.path.basename(vcf_file)} (sample: {sample_name})")
        except Exception as e:
            print(f"Error processing {vcf_file}: {e}")

    if not samples_data:
        raise ValueError("No VCF files could be processed successfully")

    # Convert to list and add our custom columns
    all_columns = list(all_columns)
    if 'sample' not in all_columns:
        all_columns.append('sample')
    if 'tool' not in all_columns:
        all_columns.append('tool')
    if 'location' not in all_columns:
        all_columns.append('location')

    # Get ancestor locations if specified
    ancestor_locations = set()
    if ancestor_sample and ancestor_sample in samples_data:
        print(f"Processing ancestor sample: {ancestor_sample}")
        ancestor_data = samples_data[ancestor_sample]

        # Group ancestor data by location and count tools
        ancestor_location_counts = defaultdict(list)
        for row in ancestor_data:
            ancestor_location_counts[row['location']].append(row)

        # Find high-confidence ancestor locations
        for location, rows in ancestor_location_counts.items():
            if len(rows) >= min_callers:
                ancestor_locations.add(location)

        print(f"Found {len(ancestor_locations)} high-confidence ancestral locations to filter out")

    # Create output directory within the input directory
    output_dir = os.path.join(input_dir, "filtered_results")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Process each sample separately
    total_samples_processed = 0
    total_files_written = 0

    for sample_name, sample_rows in samples_data.items():
        print(f"\nProcessing sample: {sample_name}")

        # Group by location and count tools for this sample
        location_counts = defaultdict(list)
        for row in sample_rows:
            location_counts[row['location']].append(row)

        # Filter by minimum number of callers
        filtered_rows = []
        for location, rows in location_counts.items():
            if len(rows) >= min_callers:
                # Also filter out ancestor locations if specified
                if not ancestor_locations or location not in ancestor_locations:
                    filtered_rows.extend(rows)

        if not filtered_rows:
            print(f"  No entries passed filtering for {sample_name}")
            continue

        # Create unique locations (one entry per location for this sample)
        unique_entries = {}
        for row in filtered_rows:
            location = row['location']
            if location not in unique_entries:
                unique_entries[location] = row

        unique_rows = list(unique_entries.values())

        # Write sample-specific output file in the output directory
        # Create filename that starts with sample name
        if ancestor_sample:
            output_file = os.path.join(output_dir, f"{sample_name}_transposons_ancfiltered.txt")
        else:
            output_file = os.path.join(output_dir, f"{sample_name}_transposons_filtered.txt")
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_columns, delimiter='\t')
            writer.writeheader()
            writer.writerows(unique_rows)

        print(f"  Wrote {len(unique_rows)} unique locations to: {output_file}")
        total_samples_processed += 1
        total_files_written += 1

    # Print summary statistics
    all_samples = list(samples_data.keys())
    print(f"\nSummary:")
    print(f"Total samples found: {len(all_samples)}")
    print(f"Samples processed: {total_samples_processed}")
    print(f"Output files written: {total_files_written}")
    if ancestor_sample:
        print(f"Ancestor locations filtered out: {len(ancestor_locations)}")
    print(f"Minimum callers required: {min_callers}")

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