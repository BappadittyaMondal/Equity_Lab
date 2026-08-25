import re
import glob

files = glob.glob("canonical_source/**/*.md", recursive=True)
cleaned_count = 0

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove lines matching **Paste Target:** or Paste Target:
    new_content = re.sub(r'(?m)^\s*\*?\*?Paste Target:\*?\*?.*$\n?', '', content)
    
    if new_content != content:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
        cleaned_count += 1
        print(f"Cleaned Paste Target from: {fpath}")

print(f"Total files cleaned: {cleaned_count}")
