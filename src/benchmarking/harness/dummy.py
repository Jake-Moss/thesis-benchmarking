from benchmarking.harness.generic import Library

ID = {"dummy": {"file": __file__, "env": {}}}


class Dummy(Library):
    def parse_polys(self, polys_collection: dict):
        self.poly_dict = polys_collection

    @staticmethod
    def merge(p1, p2):
        a = list(range(len(p1) + len(p1)))
        return p1 | p2

    @staticmethod
    def do_thing(p1, p2):
        for i in range(3):
            a = list(range(len(p1) + len(p1)))

        return p1 | p2


if __name__ == "__main__":
    Dummy.main()
