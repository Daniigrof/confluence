# auto_process.py
import os
import zipfile
import shutil
import subprocess

# --- Config ---
# SPACES_DIR = "./spaces"
#SPACES_DIR = "/data/historical_spaces"
SPACES_DIR = "/data/testers"
OUTPUT_DIR = "/data/output"
REPLACEMENTS_JSON = "./replacements.json"
REPLACEMENTS_USERS_JSON = "./intel_to_realsenseai_emails.json"
REPLACE_SCRIPT = "./bulk_replace.sh"
EXTRACT_SUB_URLS_SCRIPT = "./extract_before_intel_sub.sh"
EXTRACT_FULL_URLS_SCRIPT = "./extract_intel_links_full.sh"
URLS_OUTPUT_DIR = "/data/output/urls"

# --- Ensure output directories exist ---
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(URLS_OUTPUT_DIR, exist_ok=True)


# --- Loop through each zip file ---
for index,filename in enumerate(os.listdir(SPACES_DIR)):
    if filename.endswith(".zip"):
        zip_path = os.path.join(SPACES_DIR, filename)
        base_name = filename.replace(".zip", "")
        extract_path = os.path.join(SPACES_DIR, base_name)

        print(f"[{index + 1}] Processing: {filename}")
        print(f"-> Unzip: {filename}")

        # Unzip the file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        entities_path = os.path.join(extract_path, "entities.xml")
        export_descriptor_path = os.path.join(extract_path, "exportDescriptor.properties")

        # Extract spaceKey from exportDescriptor.properties
        space_key = "unknown"
        if os.path.isfile(export_descriptor_path):
            with open(export_descriptor_path) as f:
                for line in f:
                    if line.startswith("spaceKey="):
                        space_key = line.strip().split("=", 1)[1]
                        break

        # Create entities backup folder
        entities_output_dir = os.path.join(OUTPUT_DIR, "entities", space_key)
        os.makedirs(entities_output_dir, exist_ok=True)


        # Copy the original entities.xml file
        original_backup = os.path.join(entities_output_dir, "entities.xml")
        shutil.copyfile(entities_path, original_backup)


        # Log the mapping of zip file to space UID-based URL file
        with open(os.path.join(OUTPUT_DIR, "process.log"), "a") as log_file:
            log_file.write(f"{filename} → {space_key}.txt\n")


        # Run extract_before_intel_sub.sh to extract intel.com sub URLs
        urls_output_path = os.path.join(URLS_OUTPUT_DIR, f"{space_key}_sub.txt")
        subprocess.run([EXTRACT_SUB_URLS_SCRIPT, entities_path, urls_output_path], check=True)


        # Run extract_intel_links_full.sh to extract intel.com full URLs
        urls_output_path = os.path.join(URLS_OUTPUT_DIR, f"{space_key}_full.txt")
        subprocess.run([EXTRACT_FULL_URLS_SCRIPT, entities_path, urls_output_path], check=True)


        # Run the replacement script for users
        subprocess.run([REPLACE_SCRIPT, entities_path, REPLACEMENTS_USERS_JSON, entities_path], check=True)
        print ("-> Finish replace mails for realsense users")


        # Run the replacement script
        subprocess.run([REPLACE_SCRIPT, entities_path, REPLACEMENTS_JSON, entities_path], check=True)
        print (f"-> Finish replace URLs for {filename}")


        # Save the new entities.xml file with the new "entities_new.xml"
        entities_output_dir = os.path.join(OUTPUT_DIR, "entities", space_key)
        shutil.copyfile(entities_path, os.path.join(entities_output_dir, "new_entities.xml"))


        print ("-> Re-zip the folder")
        # Re-zip the folder with _fixed.zip suffix
        fixed_zip_path = os.path.join(OUTPUT_DIR, base_name + "_fixed.zip")
        with zipfile.ZipFile(fixed_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            for root, _, files in os.walk(extract_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, extract_path)
                    new_zip.write(full_path, arcname)

        print(f"-> Save fix zip file to: {fixed_zip_path}")

        # Optional: Cleanup extracted folder
        shutil.rmtree(extract_path)

print("\nAll spaces processed.")

