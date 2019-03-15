# Copyright 2019 D-Wave Systems Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# =============================================================================
try:
    import collections.abc as abc
except ImportError:
    import collections as abc

from six.moves import zip

from dimod.variables import Variables


class SampleView(abc.Mapping):
    __slots__ = '_variables', '_data'

    def __init__(self, data, variables):
        self._variables = variables
        self._data = data

    def __getitem__(self, v):
        return self._data[self._variables.index(v)]

    def __iter__(self):
        return iter(self._variables)

    def __len__(self):
        return len(self._variables)

    def __repr__(self):
        return str(dict(self))

    def values(self):
        return IndexValuesView(self)

    def items(self):
        return IndexItemsView(self)


class IndexItemsView(abc.ItemsView):
    """Faster read access to the numpy array"""
    __slots__ = ()

    def __iter__(self):
        # Inherited __init__ puts the Mapping into self._mapping
        return zip(self._mapping._variables, self._mapping._data.flat)


class IndexValuesView(abc.ValuesView):
    """Faster read access to the numpy array"""
    __slots__ = ()

    def __iter__(self):
        # Inherited __init__ puts the Mapping into self._mapping
        return iter(self._mapping._data.flat)


class SamplesArray(abc.Sequence):
    __slots__ = ('_samples', '_variables')

    def __init__(self, samples, variables):
        self._samples = samples

        if isinstance(variables, Variables):
            # we will be treating this as immutable so we don't need to
            # recreate it
            self._variables = variables
        else:
            self._variables = Variables(variables)

    def __getitem__(self, index):
        if isinstance(index, tuple):
            # multiindex, we'd like to do this in the future
            raise IndexError("multiindexing is not yet implemented")

        elif isinstance(index, int):
            # single row
            return SampleView(self._samples[index, :], self._variables)

        else:
            # multiple rows
            return type(self)(self._samples[index, :], self._variables)

    def __iter__(self):
        # __iter__ is a mixin for Sequence but we can speed it up by
        # implementing it ourselves
        variables = self._variables
        for row in self._samples:
            yield SampleView(row, variables)

    def __len__(self):
        return self._samples.shape[0]
