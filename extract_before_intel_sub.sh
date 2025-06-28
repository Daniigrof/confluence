#!/bin/bash

# -----------------------------
# Extracts all unique base intel.com domains from a file.
# It looks for any word containing "intel.com", trims off anything after the domain,
# and saves the unique results to an output file.
# -----------------------------
# Usage:
#   ./extract_before_intel_sub.sh <input-file> [output-file]
# Example:
#   ./extract_before_intel_sub.sh myfile.txt
#   ./extract_before_intel_sub.sh myfile.txt intel_links.txt
# -----------------------------


# Check input
if [ -z "$1" ]; then
  echo "Usage: $0 <input-file> [output-file]"
  exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-intel_domains.txt}"

# Extract all substrings containing 'intel.com'
# And ensures results are unique
grep -oE '[a-zA-Z0-9:/._-]*intel\.com' "$INPUT_FILE" \
  | sed -E 's#^(.*intel\.com).*#\1#' \
  | sort -u > "$OUTPUT_FILE"

echo "-> Base sub intel.com domains saved to $OUTPUT_FILE"

