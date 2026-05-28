#!/usr/bin/env python3
"""Push the backup commit via Git Data API."""
import subprocess, json, base64, os

import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise RuntimeError("环境变量 GITHUB_TOKEN 未设置")
REPO = "repos/penglang12/Pl12"

def gh(*args, input_data=None):
    cmd = ['gh', 'api', f'{REPO}/git'] + list(args)
    r = subprocess.run(cmd, input=input_data, capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

# 1. Get remote head
out, _, _ = gh('refs/heads/main', '--jq', '.object.sha')
print(f"Remote ref: {out}")

# 2. Get remote head commit to find its tree
out, _, _ = gh(f'commits/{out}', '--jq', '.tree.sha')
base_tree = out
print(f"Base tree: {base_tree}")

# 3. Get the tree of our local commit
local_tree = subprocess.run(['git', 'rev-parse', 'HEAD^{tree}'], capture_output=True, text=True, cwd='/c/Users/PC/Pl12').stdout.strip()
print(f"Local tree: {local_tree}")

# 4. Get the tree contents of our local commit
r = subprocess.run(['git', 'cat-file', '-p', local_tree], capture_output=True, text=True, cwd='/c/Users/PC/Pl12')
print(f"Tree entries:\n{r.stdout[:500]}...")

# 5. For each entry in the tree, create a blob and add to entries list
# Actually, let's use a different approach - push the pack file

# Alternative: upload each blob that doesn't exist yet
# Get the list of blobs from the local commit
r = subprocess.run(['git', 'rev-list', '--objects', '--all'], capture_output=True, text=True, cwd='/c/Users/PC/Pl12')
all_objects = r.stdout.strip().split('\n')
blobs = [line.split()[0] for line in all_objects if line.strip()]

print(f"Total objects: {len(blobs)}")

# For each blob that's not a commit, upload it
for i, obj in enumerate(blobs):
    if len(obj) != 40:
        continue
    # Check type
    r = subprocess.run(['git', 'cat-file', '-t', obj], capture_output=True, text=True, cwd='/c/Users/PC/Pl12')
    obj_type = r.stdout.strip()
    if obj_type not in ('blob', 'tree'):
        continue

    r = subprocess.run(['git', 'cat-file', obj_type, obj], capture_output=True, text=True, cwd='/c/Users/PC/Pl12')
    content = r.stdout

    if obj_type == 'blob':
        # Upload as a blob via git data API
        b64 = base64.b64encode(content.encode()).decode()
        data = json.dumps({"content": b64, "encoding": "base64"})
        out, err, code = gh('blobs', '-X', 'POST', '--input', '-', input_data=data)
        if code == 0:
            print(f"  [{i+1}/{len(blobs)}] blob {obj[:8]}: OK")
        else:
            print(f"  [{i+1}/{len(blobs)}] blob {obj[:8]}: {err[:50]}")

    elif obj_type == 'tree':
        # Trees need to reference already-uploaded blobs
        # Skip - we'll create trees after all blobs are uploaded
        pass

print("Blob upload complete")
