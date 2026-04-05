import py7zr
import os
import glob

# Title: Extract.py
# Purpose: This is a script which takes in the raw SPORTVU 
#          tracking data and converts each file into a JSON


# Paths
raw_path = "data/raw/2016.NBA.Raw.SportVU.Game.Logs"
extracted_path = "data/extracted"

# Make sure output folder exists
os.makedirs(extracted_path, exist_ok=True)

# Find all .7z files
files = glob.glob(os.path.join(raw_path, "*.7z"))
total = len(files)

print(f"Found {total} files to extract...")

for i, filepath in enumerate(files, 1):
    filename = os.path.basename(filepath)
    print(f"[{i}/{total}] Extracting {filename}...")
    
    try:
        with py7zr.SevenZipFile(filepath, mode='r') as z:
            z.extractall(path=extracted_path)
    except Exception as e:
        print(f"  ERROR on {filename}: {e}")

print("Done! All files extracted to data/extracted/")