import six
import pickle
import unittest
import json

from basicstruct import BasicStruct, BasicStructDecoder, BasicStructEncoder


class Foo(BasicStruct):
    __slots__ = ('x', 'y')


class MyTestCase(unittest.TestCase):
    def test_attribute_access(self):
        f = Foo(2, 'blah')
        self.assertEqual(f.x, 2)
        self.assertEqual(f.y, 'blah')

    def test_attribute_access_with_kwargs(self):
        f = Foo(x=2, y='blah')
        self.assertEqual(f.x, 2)
        self.assertEqual(f.y, 'blah')

    def test_attribute_access_partly_kwargs(self):
        f = Foo(2, y='blah')
        self.assertEqual(f.x, 2)
        self.assertEqual(f.y, 'blah')

    def test_attribute_access_missing_values(self):
        f = Foo(2)
        self.assertEqual(f.x, 2)
        self.assertEqual(f.y, None)

    def test_attribute_access_missing_values_partial_kwargs(self):
        f = Foo(y=2)
        self.assertEqual(f.x, None)
        self.assertEqual(f.y, 2)

    def test_comparisons(self):
        small = Foo(1, 'irrelevant')
        medium = Foo(2, 5)
        another_medium = Foo(2, 5)
        large = Foo(2, 15)

        self.assertEqual(medium, another_medium)

        self.assertTrue(small < medium)
        self.assertTrue(small < large)
        self.assertTrue(small <= medium)
        self.assertTrue(small <= large)
        self.assertTrue(medium < large)
        self.assertTrue(medium <= another_medium)
        self.assertTrue(another_medium <= medium)

        self.assertTrue(medium > small)
        self.assertTrue(large > small)
        self.assertTrue(medium >= small)
        self.assertTrue(large >= medium)
        self.assertTrue(large > medium)
        self.assertTrue(medium >= another_medium)
        self.assertTrue(another_medium >= medium)

        self.assertTrue(small != medium)
        self.assertTrue(medium != small)
        self.assertTrue(medium != large)
        self.assertTrue(large != medium)

        # need to call the magic method directly, otherwise the reverse
        # method is called, which is implemented in Python 2.x
        self.assertEqual(small.__gt__(1), NotImplemented)
        self.assertEqual(small.__ge__(1), NotImplemented)
        self.assertEqual(small.__lt__(1), NotImplemented)
        self.assertEqual(small.__le__(1), NotImplemented)
        self.assertEqual(small.__eq__(1), NotImplemented)
        self.assertEqual(small.__ne__(1), NotImplemented)

        if six.PY3:
            with self.assertRaises(TypeError):
                small < 1

            with self.assertRaises(TypeError):
                small <= 1

            with self.assertRaises(TypeError):
                small > 1

            with self.assertRaises(TypeError):
                small >= 1

    def test_repr(self):
        f = Foo(1, 'irrelevant')
        self.assertEqual(repr(f), "Foo(x=1, y='irrelevant')")

    def test_hash(self):
        small = Foo(1, 'irrelevant')
        medium = Foo(2, 5)
        another_medium = Foo(2, 5)
        large = Foo(2, 15)

        self.assertNotEqual(hash(small), hash(medium))
        self.assertNotEqual(hash(medium), hash(large))
        self.assertEqual(hash(medium), hash(another_medium))

    def _json_tester(self, obj):
        json_encoded_obj = json.dumps(obj, cls=BasicStructEncoder)
        obj_from_json = json.loads(json_encoded_obj, cls=BasicStructDecoder)

        self.assertEqual(obj.to_ordered_dict(), obj_from_json.to_ordered_dict())

    def test_json(self):
        self._json_tester(Foo(1, 2))
        self._json_tester(Foo([1, 2, 3], 4))
        self._json_tester(Foo({'a': 1, 'b': 2}, 4))

    def _pickle_tester(self, obj):
        pickle_encoded_obj = pickle.dumps(obj)
        obj_from_pickle = pickle.loads(pickle_encoded_obj)

        self.assertEqual(obj.to_ordered_dict(), obj_from_pickle.to_ordered_dict())

    def test_pickle(self):
        self._pickle_tester(Foo(1, 2))
        self._pickle_tester(Foo([1, 2, 3], 4))
        self._pickle_tester(Foo({'a': 1, 'b': 2}, 4))

    def test_len(self):
        obj1 = Foo(1, 2)
        obj2 = Foo([1, 2, 3], 4)
        self.assertTrue(len(obj1) == len(obj2))
    def test_to_dict(self):
        f = Foo(1, 2)
        d1 = f.to_dict()
        d2 = dict(f)
        expected = {'x': 1, 'y': 2}

        self.assertEqual(d1, expected)
        self.assertEqual(d2, expected)

    def test_to_dict_copy(self):
        l = []
        f = Foo(1, l)
        d1 = f.to_dict()
        d2 = f.to_dict(copy=True)
        l.append(1)

        self.assertEqual(d1, {'x': 1, 'y': [1]})
        self.assertEqual(d2, {'x': 1, 'y': []})


if __name__ == '__main__':
    unittest.main()
