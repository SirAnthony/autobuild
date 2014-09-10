

class AttrDict(dict):

    def __init__(self, indict=None):
        if indict is None:
            indict = {}
        dict.__init__(self, indict)

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            return None

    def __setattr__(self, item, value):
        if item in self.__dict__:
            dict.__setattr__(self, item, value)
        else:
            if isinstance(value, dict):
                self.__setitem__(item, AttrDict(value))
            else:
                self.__setitem__(item, value)
