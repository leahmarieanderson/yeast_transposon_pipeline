#!/usr/bin/env python3

import os
import shutil
import argparse
import glob

def collect_vcfs(transposons_dir, output_dir="all_nonredundant_vcfs"):
    """
    Collect all nonredundant VCF files from sample subdirectories into one directory
    """

    # Create output directory
    full_output_dir = os.path.join(transposons_dir, output_dir)
    os.makedirs(full_output_dir, exist_ok=True)
    print(f"Created output directory: {full_output_dir}")

    # Find all sample directories
    sample_dirs = [d for d in os.listdir(transposons_dir)
                   if os.path.isdir(os.path.join(transposons_dir, d))
                   and d != output_dir]  # Don't include our output dir

    if not sample_dirs:
        print(f"No sample directories found in {transposons_dir}")
        return

    print(f"Found {len(sample_dirs)} sample directories: {sample_dirs}")

    total_files = 0

    # Process each sample directory
    for sample_dir in sample_dirs:
        sample_path = os.path.join(transposons_dir, sample_dir)
        nonredundant_path = os.path.join(sample_path, "nonredundant_vcfs")

        if not os.path.exists(nonredundant_path):
            print(f"Warning: {nonredundant_path} not found, skipping {sample_dir}")
            continue

        # Find all VCF files in this sample's nonredundant_vcfs directory
        vcf_pattern = os.path.join(nonredundant_path, "*.vcf")
        vcf_files = glob.glob(vcf_pattern)

        if not vcf_files:
            print(f"Warning: No VCF files found in {nonredundant_path}")
            continue

        print(f"Copying {len(vcf_files)} VCF files from {sample_dir}")

        # Copy each VCF file
        for vcf_file in vcf_files:
            filename = os.path.basename(vcf_file)
            dest_path = os.path.join(full_output_dir, filename)

            # Check if file already exists (shouldn't happen but just in case)
            if os.path.exists(dest_path):
                print(f"Warning: {filename} already exists, skipping")
                continue

            shutil.copy2(vcf_file, dest_path)
            total_files += 1

    print(f"\nSummary:")
    print(f"Total VCF files copied: {total_files}")
    print(f"All files are now in: {full_output_dir}")
    print(f"\nNow you can run:")
    print(f"python3 combine_vcfs.py {full_output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Collect all nonredundant VCF files into one directory")
    parser.add_argument("transposons_dir", help="Path to transposons directory containing sample folders")
    parser.add_argument("-o", "--output-dir", default="all_nonredundant_vcfs",
                       help="Name of output directory (default: all_nonredundant_vcfs)")

    args = parser.parse_args()

    if not os.path.isdir(args.transposons_dir):
        raise ValueError(f"Directory does not exist: {args.transposons_dir}")

    collect_vcfs(args.transposons_dir, args.output_dir)

if __name__ == "__main__":
    main()