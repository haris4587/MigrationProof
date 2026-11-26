"""Print a raw SHA-256/byte manifest for a committed public artifact."""
import argparse
import hashlib
import json
import re
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('commit'); p.add_argument('path'); p.add_argument('--publisher',default='haris4587/MigrationProof')
a=p.parse_args()
if not re.fullmatch('[0-9a-f]{40}',a.commit): p.error('full lowercase commit SHA required')
if not re.fullmatch('[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+',a.publisher): p.error('owner/repository required')
if any(not re.fullmatch('[A-Za-z0-9_-][A-Za-z0-9_.-]*',v) or v in ('.','..') for v in a.path.split('/')): p.error('safe repository-relative path required')
root=Path(__file__).resolve().parents[1]
b=(root/a.path).read_bytes()
if not 1<=len(b)<=48000: p.error('artifact must contain 1-48000 bytes')
print(json.dumps(dict(url=f'https://raw.githubusercontent.com/{a.publisher}/{a.commit}/{a.path}',sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)),sort_keys=True,separators=(',',':')))
