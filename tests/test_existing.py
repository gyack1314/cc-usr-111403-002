"""已有接口的核心、边界及错误路径。"""
import unittest,tempfile
from pathlib import Path
from lake.storage import read_source,Objects,digest

class StorageTests(unittest.TestCase):
    def test_source_and_corruption(self):
        value=read_source()
        with tempfile.TemporaryDirectory() as d:
            o=Objects(d);key=o.put(value);self.assertEqual(o.get(key),value)
            self.assertEqual(o.put(value),key)
            Path(d,key).write_bytes(b'bad')
            with self.assertRaises(ValueError):o.get(key)
    def test_bad_object_identity(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):Objects(d).get('../bad')

from lake.relations import PrefixRelation,atom_rows

class FeatureTests(unittest.TestCase):
    def test_prefix_multiplicity(self):
        r=PrefixRelation(['a','b'],[[1,2],[1,2],[1,None],[3,4]])
        self.assertEqual(r.next_values(()),(1,3));self.assertEqual(r.seek((),2),3)
        self.assertEqual(r.count_exact([1,2]),2)
        v=r.view(['b','a'],r.digest);self.assertEqual(v.next_values(()),(2,4))
    def test_bad_view(self):
        r=PrefixRelation(['a'],[[1]])
        with self.assertRaises(ValueError):r.view(['a'],'old')
    def test_repeated_variable(self):
        self.assertEqual(sum(atom_rows({'vars':['x','x'],'rows':[[1,1],[1,2],[None,None]]}).values()),1)
