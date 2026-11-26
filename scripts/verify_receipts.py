"""Verify an exported array of canonical on-chain receipt wrappers."""
import hashlib
import json
import sys
from pathlib import Path
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True)
def verify(items):
    if not isinstance(items,list) or not items: raise ValueError('nonempty receipt array required')
    previous=''; domain=None
    for seq,wrapper in enumerate(items,1):
        r=wrapper['receipt']; h=hashlib.sha256(canonical(r).encode()).hexdigest()
        if wrapper['hash']!=h or r['previous']!=previous or r['sequence']!=seq: raise ValueError('receipt hash, previous or sequence mismatch')
        current=(r['version'],r['chain_id'],r['contract'],r['case_id'])
        if domain is not None and current!=domain: raise ValueError('domain mismatch')
        domain=current; previous=h
    return previous
if __name__=='__main__': print(verify(json.loads(Path(sys.argv[1]).read_text())))
