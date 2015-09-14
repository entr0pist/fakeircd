#!/usr/bin/python2
from struct import pack, unpack

class Struct:
    data  = []
    align = "@"

    class Error(Exception):
        def __init__(self, value):
            self.value = value

        def __repr__(self):
            return repr(self.value)

    def __init__(self, *args, **kwargs):
        if "unpack" in kwargs:
            self.unpack(args[0])
            return

        for index, key in enumerate(self.data):
            key = key[0]
            if key in kwargs:
                self.__dict__[key] = kwargs[key]
            elif index < len(args):
                self.__dict__[key] = args[index]
            else:
                self.__dict__[key] = ""

    def iteritems(self):
        for key, value in self.data:
            yield key, self.__dict__[key]

    def keys(self):
        return [key for key, value in self.data]

    def values(self):
        data = []
        for key, value in self.data:
            if isinstance(self.__dict__[key], Struct):
                data += self.__dict__[key].values()
            else:
                data.append(self.__dict__[key])
        return data

    @classmethod
    def get_types(self):
        pack_string = ""
        for key, value in self.data:
            if type(Struct) == type(value):
                pack_string += value.get_types()
            else:
                pack_string += value
        return pack_string

    @classmethod
    def num_elements(self):
        return len(self.data)

    def pack(self):
        return pack(self.align + self.get_types(), *self.values())

    def unpack(self, struc):
        data = unpack(self.align + self.get_types(), struc)

        index     = 0
        tmp_lst = []

        while data:
            key = self.data[index]
            if type(key[1]) == type(Struct):
                if tmp_lst == []:
                    tmp_len = key[1].num_elements()
                tmp_lst.append(data[0])
                if len(tmp_lst) == tmp_len:
                    self.__dict__[key[0]] = key[1](*tmp_lst)
                    tmp_lst = []
                    index += 1
            else:
                self.__dict__[key[0]] = data[0]
                index += 1
            data = data[1:]

    def valid_key(self, key):
        found = False
        for _key, value in self.data:
            if _key == key:
                found = True
                break
        return found

    def __len__(self):
        return len(self.pack())

    def __setitem__(self, key, value):
        if not self.valid_key(key):
            raise Struct.Error("Item not in Struct")
        self.__dict__[key] = value

    def __getitem__(self, key):
        if not self.valid_key(key):
            raise Struct.Error("Item not in Struct")
        return self.__dict__[key]

    def __iter__(self):
        for key, value in self.data:
            yield key

    def __repr__(self):
        return self.pack()
