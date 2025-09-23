#!/usr/bin/env python3

import pandas as pd
import argparse
import os
import glob
import re

def read_vcf(filepath):
    """Read VCF file, skipping header lines starting with ##"""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find the header line that starts with #CHROM
    header_idx = None
    for line_number, line in enumerate(lines):
        if line.startswith('#CHROM'):
            vcf_header = line_number
            break

    if header_idx is None:
        raise ValueError(f"No #CHROM header found in {filepath}")

    # Read from the header line onwards
    df = pd.read_csv(filepath, sep='\t', skiprows=vcf_header, low_memory=False)

    # Extract sample name and tool from filename using regular expressions
    filename = os.path.basename(filepath)
    sample_match = re.search(r'(.+?)_R1', filename)
    tool_match = re.search(r'001_(.+?)_nonredundant', filename)

    sample_name = sample_match.group(1) if sample_match else "unknown"
    tool_name = tool_match.group(1) if tool_match else "unknown"

    df['sample'] = sample_name
    df['tool'] = tool_name
    df['location'] = df['#CHROM'].astype(str) + ':' + df['POS'].astype(str)

    return df

def combine_vcfs(input_dir, min_callers=3, ancestor_sample=None, output_prefix="filtered_te"):
    """Combine VCF files and filter by minimum number of callers"""

    # Find all VCF files
    vcf_pattern = os.path.join(input_dir, "*.vcf")
    vcf_files = glob.glob(vcf_pattern)

    if not vcf_files:
        raise ValueError(f"No VCF files found in {input_dir}")

    print(f"Found {len(vcf_files)} VCF files")

    # Read and combine all VCF files
    all_dfs = []
    for vcf_file in vcf_files:
        try:
            df = read_vcf(vcf_file)
            all_dfs.append(df)
            print(f"Processed: {os.path.basename(vcf_file)}")
        except Exception as e:
            print(f"Error processing {vcf_file}: {e}")

    if not all_dfs:
        raise ValueError("No VCF files could be processed successfully")

    # Combine all dataframes
    combined_df = pd.concat(all_dfs, ignore_index=True, sort=False)

    # Filter by minimum number of callers per sample per location FIRST
    filtered_df = combined_df.groupby(['sample', 'location']).filter(lambda x: len(x) >= min_callers)

    # Handle ancestor filtering if specified (only filter out high-confidence ancestor calls)
    if ancestor_sample:
        anc_df = filtered_df[filtered_df['sample'] == ancestor_sample]
        anc_locations = set(anc_df['location'])
        filtered_df = filtered_df[~filtered_df['location'].isin(anc_locations)]
        print(f"Filtered out {len(anc_locations)} high-confidence ancestral locations")

    # Create output files
    output_all = f"{output_prefix}_all.txt"
    filtered_df.to_csv(output_all, sep='\t', index=False)
    print(f"Wrote all filtered calls to: {output_all}")

    # Create unique locations file (one entry per sample per location)
    unique_df = filtered_df.groupby(['sample', 'location']).first().reset_index()
    output_unique = f"{output_prefix}_unique.txt"
    unique_df.to_csv(output_unique, sep='\t', index=False)
    print(f"Wrote unique filtered calls to: {output_unique}")

    # Print summary statistics
    print(f"\nSummary:")
    print(f"Total VCF entries processed: {len(combined_df)}")
    print(f"Entries passing {min_callers}+ caller filter: {len(filtered_df)}")
    print(f"Unique locations after filtering: {len(unique_df)}")
    print(f"Samples processed: {combined_df['sample'].nunique()}")
    print(f"Tools used: {combined_df['tool'].nunique()}")

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