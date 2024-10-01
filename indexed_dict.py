class IndexedDict:
    def __init__(self, initial_dict=None):
        if initial_dict is None:
            initial_dict = {}
        self._dict = initial_dict
        self._keys = list(self._dict.keys())

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._dict[self._keys[key]]
        else:
            return self._dict[key]

    def __setitem__(self, key, value):
        if key in self._dict:
            self._dict[key] = value
        else:
            self._dict[key] = value
            self._keys.append(key)

    def __delitem__(self, key):
        if key in self._dict:
            del self._dict[key]
            self._keys.remove(key)

    def __repr__(self):
        return repr(self._dict)

    def keys(self):
        return self._keys

    def values(self):
        return list(self._dict.values())

    def items(self):
        return list(self._dict.items())

    def get_index_by_key(self, key):
        if key in self._dict:
            return self._keys.index(key)
        else:
            raise KeyError(f"Key '{key}' not found")

    def get_key_by_index(self, index):
        if 0 <= index < len(self._keys):
            return self._keys[index]
        else:
            raise IndexError(f"Index '{index}' out of range")
