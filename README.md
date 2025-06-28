# confluence
Automation for Confluence migration
## Pre-requestes
Update the environment variables in auto_process.py to match the current location of your spaces.
In the replacements.json file, define the key-value pairs for the paths you want to replace.

## Usage
python3 auto_process.py
This script runs a bash script as a subprocess and processes all .zip files located in the directory specified by the SPACES_DIR environment variable.
