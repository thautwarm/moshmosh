from copy import copy
import itertools


class NotExhaustive(Exception):
    pass

class ListViewProspectiveGrowError(Exception):
    pass


class ListView(list):
    # noinspection PyMissingConstructor
    def __init__(self, src, view_indices):
        self.src = src
        self.view_indices = view_indices

    def count(self):
        return len(self.view_indices)

    def __getitem__(self, item):
        return self.src[self.view_indices[item]]

    def __setitem__(self, key, value):
        self.src[self.view_indices[key]] = value

    def __iter__(self):
        src = self.src
        for each in self.view_indices:
            yield src[each]

    def __contains__(self, item):
        return item in iter(self)

    def __add__(self, other):
        return list(self) + other

    def copy(self):
        return ListView(self.src, self.view_indices)

    def append(self, _):
        raise ListViewProspectiveGrowError

    def extend(self, _):
        raise ListViewProspectiveGrowError

    def pop(self, _=...):
        raise ListViewProspectiveGrowError

    def clear(self):
        raise ListViewProspectiveGrowError

    def remove(self, obj):
        raise ListViewProspectiveGrowError

    def reverse(self):
        view_indices = self.view_indices
        for i in range(len(view_indices) // 2):
            view_indices[i], view_indices[-i] = view_indices[-i], view_indices[
                i]

    def insert(self, _, __):
        raise ListViewProspectiveGrowError

    def index(self, obj, start=0, stop=None):
        src = self.src
        view_indices = self.view_indices
        n = len(view_indices)
        if stop is None:
            stop = n
        else:
            stop = min(n, stop)

        for i in range(start, stop):
            if src[view_indices[i]] == obj:
                return i
        raise ValueError

    def sort(self, *, key=None, reverse=False):
        src = self.src
        if key:

            def key_(i):
                return key(src[i])
        else:

            def key_(i):
                return src[i]

        if isinstance(self.view_indices, list):
            self.view_indices.sort(key=key_, reverse=reverse)
        else:
            self.view_indices = sorted(
                self.view_indices, key=key_, reverse=reverse)

    def __eq__(self, other):
        xs_l = iter(self)
        xs_r = iter(other)
        for l, r in zip(xs_l, xs_r):
            if l == r:
                continue
            return False
        try:
            next(xs_r)
        except StopIteration:
            return True
        return False

    def __repr__(self):
        return 'View{}'.format(list(self))
