#!/bin/bash

# -----------------------------
# Extracts all unique base intel.com domains from a file.
# It looks for any word containing "intel.com", trims off anything after the domain,
# and saves the unique results to an output file.
# -----------------------------
# Usage:
#   ./extract_intel_domains.sh <input-file> [output-file]
# Example:
#   ./extract_intel_links_full.sh myfile.txt
#   ./extract_intel_links_full.sh myfile.txt intel_links.txt
# -----------------------------


# Check for input file
if [ -z "$1" ]; then
  echo "Usage: $0 <input-file> [output-file]"
  exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-intel_links.txt}"  # Default output file if not specified

# Extract intel.com links and write to output file
grep -oE '[^[:space:]"'\''<>]*intel\.com[^[:space:]"'\''<>]*' "$INPUT_FILE" \
  | sort -u > "$OUTPUT_FILE"

echo "-> Base full intel.com domains saved to $OUTPUT_FILE"

