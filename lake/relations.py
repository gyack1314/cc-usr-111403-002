"""冻结关系的有序前缀访问接口。"""
from collections import Counter
from bisect import bisect_left
from .storage import digest

class PrefixRelation:
    def __init__(self,columns,rows,order=None):
        self.columns=tuple(columns)
        if len(set(self.columns))!=len(self.columns):raise ValueError('物理列名重复')
        self.order=tuple(order or columns)
        if set(self.order)!=set(columns) or len(self.order)!=len(columns):raise ValueError('列排列不完整')
        self.rows=[tuple(r) for r in rows]
        if any(len(r)!=len(columns) for r in self.rows):raise ValueError('物理行宽度不符')
        self.digest=digest({'columns':self.columns,'rows':self.rows})
        self.counts=Counter(self.rows);self.calls=[]
    def view(self,order,expected_digest):
        if expected_digest!=self.digest:raise ValueError('前缀视图版本过期')
        return PrefixRelation(self.columns,self.rows,order)
    def _tuples(self):
        idx=[self.columns.index(c) for c in self.order]
        return [tuple(r[i] for i in idx) for r in self.rows if all(r[i] is not None for i in idx)]
    def next_values(self,prefix):
        p=tuple(prefix)
        if len(p)>=len(self.order):raise ValueError('前缀已完整')
        self.calls.append({'op':'next','prefix':p})
        return tuple(sorted({r[len(p)] for r in self._tuples() if r[:len(p)]==p}))
    def seek(self,prefix,lower):
        values=self.next_values(prefix);i=bisect_left(values,lower)
        self.calls.append({'op':'seek','lower':lower})
        return values[i] if i<len(values) else None
    def count_exact(self,values):
        if len(values)!=len(self.order):raise ValueError('完整键长度不符')
        if any(v is None for v in values):return 0
        d=dict(zip(self.order,values));self.calls.append({'op':'count','values':tuple(values)})
        return self.counts[tuple(d[c] for c in self.columns)]

def atom_rows(atom):
    variables=atom['vars'];out=Counter()
    for row in atom['rows']:
        if len(row)!=len(variables):raise ValueError('原子宽度不符')
        d={};valid=True
        for name,value in zip(variables,row):
            if value is None or (name in d and d[name]!=value):valid=False;break
            d[name]=value
        if valid:out[tuple(sorted(d.items()))]+=1
    return out
