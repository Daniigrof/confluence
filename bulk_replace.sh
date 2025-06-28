#!/bin/bash

# -------------------------------
# Bulk string replacement using a JSON map
# Replaces all occurrences of specified old hostnames/domains with new ones
# -------------------------------
# Usage:
#   ./bulk_replace.sh <input-file> <replacements.json> <output-file>
# Example:
#   ./bulk_replace.sh entities.xml replacements.json entities_new.xml
# -------------------------------

# Validate arguments
if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <input-file> <replacements.json> <output-file>"
  exit 1
fi

INPUT_FILE="$1"
REPLACEMENTS_FILE="$2"
OUTPUT_FILE="$3"

# Create a temporary file for processing
TMP_FILE=$(mktemp)
cp "$INPUT_FILE" "$TMP_FILE"

# Process each replacement from the JSON file
# The format is: { "old.domain.com": "new.domain.com", ... }
jq -r 'to_entries[] | "\(.key) \(.value)"' "$REPLACEMENTS_FILE" | while read -r OLD NEW; do

  # Escape special characters for sed
  ESCAPED_OLD=$(echo "$OLD" | sed 's/\./\\./g')
  ESCAPED_NEW=$(echo "$NEW" | sed 's/\//\\\//g')

  # Perform the replacement using sed (in-place, extended regex)
  sed -i -r "s#${ESCAPED_OLD}#${ESCAPED_NEW}#g" "$TMP_FILE"

done

# Move the result to the desired output file
mv "$TMP_FILE" "$OUTPUT_FILE"

echo "-> Replacements complete"

