"""Offline host doubles exercise actual contract and independent validator paths.
Not a GenVM emulator or live consensus claim.
"""
import copy
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Address(str): pass
class TreeMap:
    def __class_getitem__(cls,_): return dict
class Return:
    def __init__(self,v): self.calldata=v
class UserError(Exception): pass
class Contract:
    def __new__(cls,*args):
        o=object.__new__(cls); o.cases={}; o.receipts={}; return o
host=types.SimpleNamespace(Contract=Contract,public=types.SimpleNamespace(write=lambda f:f,view=lambda f:f),message=types.SimpleNamespace(sender_address=Address('owner'),contract_address=Address('contract'),chain_id=61999),vm=types.SimpleNamespace(UserError=UserError,Return=Return),nondet=types.SimpleNamespace(web=types.SimpleNamespace()))
stub=types.ModuleType('genlayer'); stub.__all__=['gl','Address','TreeMap','u256']; stub.gl=host; stub.Address=Address; stub.TreeMap=TreeMap; stub.u256=int
sys.modules['genlayer']=stub
spec=importlib.util.spec_from_file_location('migration_proof',ROOT/'contracts/migration_proof.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class Tests(unittest.TestCase):
    def setUp(self):
        self.p=json.loads((ROOT/'fixtures/policy.json').read_text()); self.b=json.loads((ROOT/'fixtures/bundle.json').read_text())
        self.raw=(ROOT/'fixtures/bundle.json').read_bytes()
        self.desc={'url':'https://raw.githubusercontent.com/haris4587/MigrationProof/'+'a'*40+'/fixtures/bundle.json','sha256':m.hashlib.sha256(self.raw).hexdigest(),'bytes':len(self.raw)}
        host.message.sender_address=Address('owner')
        host.nondet.web.get=lambda url:types.SimpleNamespace(status=200,body=self.raw)
        self.calls=0
        def prompt(_):
            self.calls+=1
            return m.canonical({'checks':[{'id':r['id'],'status':'PASS','reason':'Fixture evidence supports the requirement','source':'tests','quote':'Restored rows equal original rows including NULL.'} for r in self.p['rules']]})
        host.nondet.exec_prompt=prompt
        def run(leader,validator):
            value=leader()
            if not validator(Return(value)): raise RuntimeError('Consensus disagreement')
            return value
        host.vm.run_nondet_unsafe=run
        self.c=m.MigrationProof('haris4587/MigrationProof',Address('reviewer'))
    def create(self): return self.c.create('Dollar to cents',m.canonical(self.p))
    def submitted(self):
        cid=self.create(); self.c.lock(cid); self.c.submit(cid,m.canonical(self.desc)); return cid
    def test_policy(self): self.assertEqual(m.policy(m.canonical(self.p)),self.p)
    def test_sqlite_reproduction(self):
        sp=importlib.util.spec_from_file_location('build',ROOT/'scripts/build_fixtures.py'); mod=importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); self.assertEqual(mod.build(),(self.p,self.b))
    def test_all_checks(self): self.assertTrue(all(m.deterministic(self.p,self.b).values()))
    def test_count_loss(self): self.b['after_rows']['accounts'].pop(); self.assertFalse(m.deterministic(self.p,self.b)['row_count'])
    def test_duplicate_pk(self): self.b['after_rows']['accounts'][1]['id']=1; self.assertFalse(m.deterministic(self.p,self.b)['primary_key'])
    def test_null_pk(self): self.b['after_rows']['accounts'][0]['id']=None; self.assertFalse(m.deterministic(self.p,self.b)['id_present'])
    def test_baseline_tamper(self): self.b['before_rows']['accounts'][0]['balance_dollars']=99; self.assertFalse(m.deterministic(self.p,self.b)['baseline'])
    def test_schema_mismatch(self): self.p['after_schema']['accounts']['extra']='str'; self.assertFalse(m.deterministic(self.p,self.b)['after_schema'])
    def test_type_bool_is_not_int(self): self.b['after_rows']['accounts'][0]['id']=True; self.assertRaises(UserError,m.deterministic,self.p,self.b)
    def test_extra_row_field(self): self.b['after_rows']['accounts'][0]['secret']='x'; self.assertRaises(UserError,m.deterministic,self.p,self.b)
    def test_sum(self):
        self.p['checks']=[dict(id='sum',kind='sum',table='accounts',column='id',target=[],expected=10)]; self.assertTrue(m.deterministic(self.p,self.b)['sum'])
    def test_null_sum(self):
        self.p['checks']=[dict(id='sum',kind='sum',table='accounts',column='balance_cents',target=[],expected=500)]; self.assertFalse(m.deterministic(self.p,self.b)['sum'])
    def test_fk(self):
        self.p['checks']=[dict(id='fk',kind='foreign_key',table='accounts',column='id',target=['accounts','id'],expected=0)]; self.assertTrue(m.deterministic(self.p,self.b)['fk'])
        self.p['checks'][0]['target']=['accounts','balance_cents']; self.assertFalse(m.deterministic(self.p,self.b)['fk'])
    def test_unpinned(self): self.desc['url']=self.desc['url'].replace('a'*40,'main'); self.assertRaises(UserError,m.manifest,m.canonical(self.desc),self.c.publisher)
    def test_ssrf(self): self.desc['url']='http://127.0.0.1/private'; self.assertRaises(UserError,m.manifest,m.canonical(self.desc),self.c.publisher)
    def test_url_attacks(self):
        for tail in ['../x','x?token=a','x%2fy','x#z','x//y','x@evil']:
            d=dict(self.desc,url=self.desc['url'].split('/fixtures')[0]+'/'+tail)
            with self.assertRaises(UserError): m.manifest(m.canonical(d),self.c.publisher)
    def test_wrong_publisher(self): self.assertRaises(UserError,m.manifest,m.canonical(self.desc),'attacker/repo')
    def test_digest_mismatch(self): self.desc['sha256']='0'*64; self.assertRaises(UserError,m.authenticated,self.desc)
    def test_length_mismatch(self): self.desc['bytes']+=1; self.assertRaises(UserError,m.authenticated,self.desc)
    def test_http_failure(self): host.nondet.web.get=lambda _:types.SimpleNamespace(status=404,body=self.raw); self.assertEqual(m.consensus_review(self.p,self.desc,{})['outcome'],'INCONCLUSIVE')
    def test_duplicate_json(self): self.assertRaises(UserError,m.parse,'{"a":1,"a":2}')
    def test_float_nan(self):
        for raw in ['{"x":1.2}','{"x":NaN}','{"x":Infinity}']:
            with self.assertRaises(UserError): m.parse(raw)
    def test_depth_bound(self): self.assertRaises(UserError,m.parse,'['*20+'0'+']'*20)
    def test_array_bound(self): self.assertRaises(UserError,m.parse,m.canonical(list(range(201))))
    def test_byte_bound(self): self.desc['bytes']=48001; self.assertRaises(UserError,m.manifest,m.canonical(self.desc),self.c.publisher)
    def test_empty_rules(self): self.p['rules']=[]; self.assertRaises(UserError,m.policy,m.canonical(self.p))
    def test_duplicate_rule_id(self): self.p['rules'][1]['id']='units'; self.assertRaises(UserError,m.policy,m.canonical(self.p))
    def test_outcomes(self):
        for states,want in [(['PASS','PASS'],'VERIFIED'),(['PASS','FAIL'],'CONDITIONAL'),(['FAIL','UNKNOWN'],'BREAKING'),(['PASS','UNKNOWN'],'INCONCLUSIVE')]:
            sem={'checks':[{'status':s} for s in states]}; self.assertEqual(m.outcome({'x':True},sem,self.p['rules']),want)
        self.assertEqual(m.outcome({'x':False},{'checks':[]},self.p['rules']),'BREAKING')
    def test_fabricated_quote(self):
        answer=json.loads(host.nondet.exec_prompt('')); answer['checks'][0]['quote']='fabricated'
        self.assertRaises(UserError,m.normalize,m.canonical(answer),self.p['rules'],{'tests':self.b['tests']})
    def test_llm_fail_closed(self): host.nondet.exec_prompt=lambda _:'bad json'; self.assertEqual(m.consensus_review(self.p,self.desc,{})['outcome'],'INCONCLUSIVE')
    def test_lifecycle_and_chain(self):
        cid=self.submitted(); h=self.c.review(cid); self.assertGreaterEqual(self.calls,2)
        prev=''
        for seq in range(1,5):
            r=json.loads(self.c.get_receipt(cid,seq)); self.assertEqual(r['receipt']['previous'],prev); self.assertEqual(r['hash'],m.digest(r['receipt'])); prev=r['hash']
        self.assertEqual(prev,h); self.assertEqual(json.loads(self.c.get_case(cid))['outcome'],'VERIFIED')
    def test_owner_only(self): host.message.sender_address=Address('attacker'); self.assertRaises(UserError,self.create)
    def test_reviewer_independent(self): self.assertRaises(UserError,m.MigrationProof,'haris4587/MigrationProof',Address('owner'))
    def test_submit_before_lock(self): self.assertRaises(UserError,self.c.submit,self.create(),m.canonical(self.desc))
    def test_lock_twice(self): cid=self.create(); self.c.lock(cid); self.assertRaises(UserError,self.c.lock,cid)
    def test_no_overwrite(self): cid=self.submitted(); self.assertRaises(UserError,self.c.submit,cid,m.canonical(self.desc))
    def test_terminal_review(self): cid=self.submitted(); self.c.review(cid); self.assertRaises(UserError,self.c.review,cid)
    def test_retry_limit(self):
        cid=self.submitted(); host.nondet.exec_prompt=lambda _:'bad'
        for _ in range(3): self.c.review(cid)
        self.assertRaises(UserError,self.c.review,cid)
    def test_permissionless_review(self): cid=self.submitted(); host.message.sender_address=Address('anyone'); self.c.review(cid)
    def test_challenge_authorization(self): cid=self.submitted(); self.c.review(cid); self.assertRaises(UserError,self.c.challenge,cid,m.canonical(self.desc))
    def test_challenge_and_adjudication(self):
        cid=self.submitted(); self.c.review(cid); host.message.sender_address=Address('reviewer'); self.c.challenge(cid,m.canonical(self.desc)); self.c.review(cid)
        self.assertEqual(json.loads(self.c.get_receipt(cid,6))['receipt']['event'],'ADJUDICATE'); self.assertRaises(UserError,self.c.challenge,cid,m.canonical(self.desc))
    def test_validator_disagreement(self):
        cid=self.submitted()
        def alternating(_):
            self.calls+=1
            return m.canonical({'checks':[{'id':r['id'],'status':'PASS' if self.calls%2 else 'UNKNOWN','reason':'Independent assessment','source':'tests','quote':'Restored rows equal original rows including NULL.'} for r in self.p['rules']]})
        host.nondet.exec_prompt=alternating
        self.assertRaises(RuntimeError,self.c.review,cid); self.assertEqual(json.loads(self.c.get_case(cid))['state'],'SUBMITTED')
    def test_reserved_check_names(self):
        for name in ['baseline','before_schema','after_schema']:
            p=copy.deepcopy(self.p); p['checks'][0]['id']=name
            with self.assertRaises(UserError): m.policy(m.canonical(p))
    def test_mandatory_rule_required(self):
        for r in self.p['rules']: r['severity']='advisory'
        self.assertRaises(UserError,m.policy,m.canonical(self.p))
    def test_negative_sum_policy(self):
        self.p['checks']=[dict(id='sum',kind='sum',table='accounts',column='balance_cents',target=[],expected=-100)]
        self.assertEqual(m.policy(m.canonical(self.p))['checks'][0]['expected'],-100)
    def test_negative_count_rejected(self):
        self.p['checks'][0]['expected']=-1
        self.assertRaises(UserError,m.policy,m.canonical(self.p))
    def test_no_llm_on_deterministic_break(self):
        self.b['after_rows']['accounts'].pop()
        self.raw=(m.canonical(self.b)+'\n').encode(); self.desc['bytes']=len(self.raw); self.desc['sha256']=m.hashlib.sha256(self.raw).hexdigest()
        self.assertEqual(m.consensus_review(self.p,self.desc,{})['outcome'],'BREAKING'); self.assertEqual(self.calls,0)
    def test_unknown_quote_must_be_real(self):
        a=json.loads(host.nondet.exec_prompt('')); a['checks'][0].update(status='UNKNOWN',quote='invented')
        self.assertRaises(UserError,m.normalize,m.canonical(a),self.p['rules'],{'tests':self.b['tests']})
    def test_invalid_leader_quote_rejected(self):
        cid=self.submitted()
        def forged(leader,validator):
            v=leader(); v['semantic']['checks'][0]['quote']='invented quote'
            self.assertFalse(validator(Return(v))); raise RuntimeError('rejected')
        host.vm.run_nondet_unsafe=forged
        self.assertRaises(RuntimeError,self.c.review,cid)
    def test_invalid_leader_error_rejected(self):
        cid=self.submitted()
        def forged(leader,validator):
            self.assertFalse(validator(object())); raise RuntimeError('rejected')
        host.vm.run_nondet_unsafe=forged
        self.assertRaises(RuntimeError,self.c.review,cid)
    def test_distinct_case_ids(self): self.assertNotEqual(self.create(),self.create())
if __name__=='__main__': unittest.main()
