"""Execute synthetic SQLite migration and export bounded snapshots; no external DB."""
import hashlib
import json
import sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)
def build():
    db=sqlite3.connect(':memory:')
    db.row_factory=sqlite3.Row
    db.executescript('CREATE TABLE accounts(id INTEGER PRIMARY KEY, balance_dollars INTEGER); INSERT INTO accounts VALUES(1,12),(2,0),(3,NULL),(4,-7);')
    before={'accounts':[dict(r) for r in db.execute('SELECT * FROM accounts ORDER BY id')]}
    sql='ALTER TABLE accounts ADD COLUMN balance_cents INTEGER;\nUPDATE accounts SET balance_cents = balance_dollars * 100;\nALTER TABLE accounts DROP COLUMN balance_dollars;'
    db.executescript(sql)
    after={'accounts':[dict(r) for r in db.execute('SELECT * FROM accounts ORDER BY id')]}
    assert [r['balance_cents'] for r in after['accounts']]==[1200,0,None,-700]
    db.executescript('ALTER TABLE accounts ADD COLUMN balance_dollars INTEGER; UPDATE accounts SET balance_dollars=balance_cents/100; ALTER TABLE accounts DROP COLUMN balance_cents;')
    rollback={'accounts':[dict(r) for r in db.execute('SELECT * FROM accounts ORDER BY id')]}
    assert rollback==before
    b={'before_schema':{'accounts':{'id':'int','balance_dollars':'int'}},'after_schema':{'accounts':{'id':'int','balance_cents':'int'}},'before_rows':before,'after_rows':after,'script':sql,'tests':'Synthetic SQLite fixture: input dollars [12,0,NULL,-7] -> output cents [1200,0,NULL,-700]. Full snapshot covers all four fixture rows. Rollback SQL: ALTER TABLE accounts ADD COLUMN balance_dollars INTEGER; UPDATE accounts SET balance_dollars=balance_cents/100; ALTER TABLE accounts DROP COLUMN balance_cents; Restored rows equal original rows including NULL. No claim about production data or overflow beyond fixture values.'}
    p={'before_schema':b['before_schema'],'after_schema':b['after_schema'],'before_rows_hash':hashlib.sha256(canon(before).encode()).hexdigest(),'checks':[{'id':'row_count','kind':'count','table':'accounts','column':'','target':[],'expected':4},{'id':'primary_key','kind':'unique','table':'accounts','column':'id','target':[],'expected':0},{'id':'id_present','kind':'not_null','table':'accounts','column':'id','target':[],'expected':0}], 'rules':[{'id':'units','requirement':'For the supplied complete fixture snapshots, each account id keeps its identity and its non-null balance_dollars maps to balance_cents = balance_dollars * 100; NULL remains NULL. Check positive, zero and negative cases. Limit the conclusion to supplied fixture rows.','severity':'mandatory'},{'id':'rollback','requirement':'For the supplied fixture values, a documented rollback restores original balance_dollars and preserves NULL, with an explicit equality test against original rows.','severity':'advisory'}]}
    for name,data in [('bundle',b),('policy',p)]:
        (ROOT/'fixtures'/f'{name}.json').write_text(canon(data)+'\n')
    (ROOT/'fixtures'/'counterevidence.txt').write_text('Synthetic challenge: original fixture arithmetic and rollback are correct. It does not test signed 64-bit overflow for production balances. The locked units requirement is explicitly limited to fixture rows; do not broaden its scope.\n')
    return p,b
if __name__=='__main__':
    build()
    print('SQLite migration and rollback assertions passed; fixtures regenerated.')
