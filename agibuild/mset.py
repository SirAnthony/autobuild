

class MergableSet(set):

    def merge(self, check_func, add_func):
        for item in list(self):
            if check_func(item):
                self.remove(item)
                self.add(add_func(item))

    def merge_multi_packages(self):
        # TODO: I have no idea what this function must do
        return self
