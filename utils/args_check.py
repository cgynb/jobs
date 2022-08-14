class Check:
    def __init__(self, must=None, must_not=None, args_dict=None):
        if must is None:
            self.must = tuple()
        else:
            self.must = must
        if must_not is None:
            self.must_not = tuple()
        else:
            self.must_not = must_not
        self.args_dict = args_dict

    def check(self):
        for mst in self.must:
            if self.args_dict.get(mst) is None:
                return False
        for mst_nt in self.must_not:
            if self.args_dict.get(mst_nt) is not None:
                return False
        return True
