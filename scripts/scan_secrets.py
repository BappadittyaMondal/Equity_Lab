import os
import re

assign_pattern = re.compile(r'([A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD|CLIENT_CODE)[A-Z0-9_]*)\s*[:=]\s*["\'\s]*([^\s"\'#]+)', re.IGNORECASE)

findings = []
for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['.git', '.venv', '__pycache__', '.pytest_cache', 'unnecessary_files_archive', 'Not_Required_Upload']):
        continue
    for file in files:
        filepath = os.path.join(root, file)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    for match in assign_pattern.finditer(line):
                        key, val = match.groups()
                        val_lower = val.lower()
                        if not any(ph in val_lower for ph in ['your_', 'placeholder', 'dummy', 'test', 'none', 'true', 'false', 'os.getenv', 'str', 'int', 'bool', 'secret_key', 'api_key', 'token', 'xxx', 'changeme', 'default', 'example', 'optional', 'schema', 'string', 'header']):
                            if len(val) > 4 and not val.startswith('http') and not val.startswith('app') and not val.startswith('self.'):
                                findings.append((filepath, line_num, key, val))
        except Exception as e:
            pass

print(f"Total findings: {len(findings)}")
for path, line_num, key, val in findings:
    print(f"  {path}:{line_num} -> {key} = {val}")
