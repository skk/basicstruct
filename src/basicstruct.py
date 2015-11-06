# Copyright (c) 2015 Amir Rachum.
# This program is distributed under the MIT license.

"""basicstruct provides BasicStruct, a class for simple struct-like objects."""
from contextlib import suppress

import six
from copy import deepcopy
from six.moves import zip
from itertools import chain

__version__ = '1.0.4-alpha'


class BasicStruct(object):
    """Class for holding struct-like objects."""

    __slots__ = ()  # should be extended by deriving classes

    def __init__(self, *args, **kwargs):
        arg_pairs = zip(self.__slots__, args)
        for key, value in chain(arg_pairs, six.iteritems(kwargs)):
            setattr(self, key, value)

        for key in self.__slots__:
            if not hasattr(self, key):
                default_value = None
                try:
                    default_value = self.__slots__[key]
                except TypeError:
                    pass
                setattr(self, key, default_value)

    def to_dict(self, copy=False):
        """Convert the struct to a dictionary.

        If `copy == True`, returns a deep copy of the values.

        """
        new_dict = {}
        for attr, value in self:
            if copy:
                value = deepcopy(value)
            new_dict[attr] = value

        return new_dict

    def __repr__(self):
        attrs_str = ', '.join('{0}={1!r}'.format(key, getattr(self, key))
                              for key in self.__slots__)
        return '{0}({1})'.format(self.__class__.__name__, attrs_str)

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

    def __hash__(self):
        return hash(self._to_tuple())

    def __iter__(self):
        """Yield pairs of (attrubute_name, value).

        This allows using `dict(my_struct)`.

        """
        return zip(self.__slots__, self._to_tuple())

    def _to_tuple(self):
        return tuple(getattr(self, key) for key in self.__slots__)

    def __getstate__(self):
        return self._to_tuple()

    def __setstate__(self, state):
        for key, value in zip(self.__slots__, state):
            setattr(self, key, value)

