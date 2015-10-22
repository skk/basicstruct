# Copyright (c) 2015 Amir Rachum.
# This program is distributed under the MIT license.

"""This is a placeholder."""
import json
from json.decoder import WHITESPACE
import collections

import six
from itertools import chain

__version__ = '1.0.3'


class BasicStruct(object):
    """Class for holding struct-like objects."""

    __slots__ = ()  # should be extended by deriving classes

    def __init__(self, *args, **kwargs):
        super(BasicStruct, self).__init__()

        arg_pairs = zip(self.__slots__, args)
        for key, value in chain(arg_pairs, six.iteritems(kwargs)):
            setattr(self, key, value)

        for key in self.__slots__:
            if not hasattr(self, key):
                setattr(self, key, None)

    def __repr__(self):
        attrs_str = ', '.join('{0}={1!r}'.format(key, getattr(self, key))
                              for key in self.__slots__)
        return '{0}({1})'.format(self.__class__.__name__, attrs_str)

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.to_tuple() < other.to_tuple()

    def __le__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.to_tuple() <= other.to_tuple()

    def __gt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.to_tuple() > other.to_tuple()

    def __ge__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.to_tuple() >= other.to_tuple()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.to_tuple() == other.to_tuple()

    def __ne__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.to_tuple() != other.to_tuple()

    def __len__(self):
        return len(self.__slots__)

    def __iter__(self):
        for key in self.__slots__:
            yield key

    def __getitem__(self, key):
        if hasattr(self, key):
            val = getattr(self, key)
            return val
        else:
            raise KeyError("key {} not found".format(key))

    def __getstate__(self):
        d = {}
        for attr in self.__slots__:
            val = getattr(self, attr)
            d[attr] = val

        return d

    def __setstate__(self, state):
        for attr in self.__slots__:
            if attr in state:
                val = state[attr]
                setattr(self, attr, val)

    def __hash__(self):
        return hash(self.to_tuple())

    def to_tuple(self):
        return tuple(getattr(self, key) for key in self.__slots__)

    def to_dict(self):
        return {
            key: getattr(self, key)
            for key in self.__slots__
        }

    def to_ordered_dict(self):
        d = collections.OrderedDict()
        for key in sorted(self.__slots__):
            d[key] = getattr(self, key)

        return d


class BasicStructEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BasicStruct):

            data = {}
            for key in obj.__slots__:
                val = getattr(obj, key)

                if isinstance(val, BasicStruct):
                    val = BasicStructEncoder.default(self, val)

                data[key] = val

            return data

        # Let the base class default method raise the TypeError
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError, e:
            raise e

class BasicStructDecoder(json.JSONDecoder):
    def decode(self, obj, _w=WHITESPACE.match):
        json_obj = json.loads(obj)

        class JSONDecoerTest(BasicStruct):
            __slots__ = json_obj.keys()

        basic_struct_obj = JSONDecoerTest()

        for k, v in json_obj.iteritems():
            setattr(basic_struct_obj, k, v)

        return basic_struct_obj

