# Copyright (c) 2015 Amir Rachum.
# This program is distributed under the MIT license.

"""basicstruct provides BasicStruct, a class for simple struct-like objects."""
import json
from json.decoder import WHITESPACE
import collections

import six
from copy import deepcopy
from itertools import chain
from collections import Mapping

__version__ = '1.1.0'
__all__ = ('BasicStruct',)


class BasicStruct(object):
    """Class for holding struct-like objects."""

    __slots__ = ()  # should be extended by deriving classes

    def __init__(self, *args, **kwargs):
        default_values = isinstance(self.__slots__, Mapping)
        ordered = (not type(self.__slots__) == dict and
                   not isinstance(self.__slots__, set))

        if args and not ordered:
            raise ValueError("Can't pass non-keyword arguments to {}, since "
                             "__slots__ was declared with an unordered "
                             "iterable.".format(self.__class__.__name__))

        arg_pairs = zip(self.__slots__, args)
        for key, value in chain(arg_pairs, six.iteritems(kwargs)):
            setattr(self, key, value)

        for key in self.__slots__:
            if not hasattr(self, key):
                default_value = None
                if default_values:
                    default_value = self.__slots__[key]
                setattr(self, key, default_value)

    def _to_dict(self, dict_cls, copy):
        new_dict = dict_cls()
        for attr, value in self:
            if copy:
                value = deepcopy(value)
            new_dict[attr] = value

        return new_dict

    def to_dict(self, copy=False):
        """Convert the struct to a dictionary.

        If `copy == True`, returns a deep copy of the values.

        """
        return self._to_dict(dict, copy=copy)

    def to_ordered_dict(self, copy=False):
        return self._to_dict(collections.OrderedDict, copy=copy)

    def __repr__(self):
        attrs_str = six.u(', ').join(six.u('{0}={1!r}').format(key, getattr(self, key))
                              for key in self.__slots__)
        return six.u('{0}({1})').format(self.__class__.__name__, attrs_str)

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._to_tuple() < other._to_tuple()

    def __le__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._to_tuple() <= other._to_tuple()

    def __gt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._to_tuple() > other._to_tuple()

    def __ge__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._to_tuple() >= other._to_tuple()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._to_tuple() == other._to_tuple()

    def __ne__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._to_tuple() != other._to_tuple()

    def __len__(self):
        return len(self.__slots__)

    def __hash__(self):
        return hash(self._to_tuple())

    def __iter__(self):
        """Yield pairs of (attribute_name, value).

        This allows using `dict(my_struct)`.

        """
        return zip(self.__slots__, self._to_tuple())

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

    def _to_tuple(self):
        return tuple(getattr(self, key) for key in self.__slots__)


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
        except TypeError as e:
            raise e


class BasicStructDecoder(json.JSONDecoder):
    def decode(self, obj, _w=WHITESPACE.match):
        json_obj = json.loads(obj)

        class JSONDecoderTest(BasicStruct):
            __slots__ = json_obj.keys()

        basic_struct_obj = JSONDecoderTest()

        for k, v in six.iteritems(json_obj):
            setattr(basic_struct_obj, k, v)

        return basic_struct_obj
