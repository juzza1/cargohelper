import defs.labels
import defs.classes


class Cargos:
    def __init__(self, ignore_unknown_labels=True):
        self.labels = []
        self.classes = defs.classes.all
        self.ignore_unknown_labels = ignore_unknown_labels

    def refresh(self):
        self.labels = []
        for lb in defs.labels.fetch_labels():
            if self.ignore_unknown_labels and not lb.industries:
                continue
            self.labels.append(lb)
        self.classes = defs.classes.all
        # Map classes to labels, and vice versa
        for lb in self.labels:
            for cl in self.classes:
                if lb.bitmask & cl.value:
                    lb.classes.add(cl)
                    cl.labels.add(lb)

    def check_inclusion(self, incl_cc, excl_ccs):
        """Check if cargo class is "safe" to be included according to
           https://newgrf-specs.tt-wiki.net/wiki/Action0/Cargos#CargoClasses_.2816.29"""
        if incl_cc == defs.classes.non_pourable:
            return 'Never include this class'
        return None

    def check_exclusion(self, excl_cc, incl_ccs):
        """Check if cargo class is "safe" to be excluded according to
           https://newgrf-specs.tt-wiki.net/wiki/Action0/Cargos#CargoClasses_.2816.29"""

        never_exclude = {defs.classes.passengers, defs.classes.mail,
                         defs.classes.express, defs.classes.armored,
                         defs.classes.bulk, defs.classes.piece_goods,
                         defs.classes.liquid}
        if excl_cc in never_exclude:
            return 'Never exclude this class'
        if excl_cc in {defs.classes.refrigerated, defs.classes.oversized} \
                and defs.classes.piece_goods not in incl_ccs:
            return 'Only exclude when Piece Goods is included'
        if excl_cc == defs.classes.hazardous:
            return 'Only exclude when special wagons are provided'
        if excl_cc == defs.classes.covered and defs.classes.liquid in incl_ccs:
            return 'Do not exclude for Liquid'
        if excl_cc in {defs.classes.powderized, defs.classes.non_pourable} \
                and defs.classes.bulk not in incl_ccs:
            return 'Only exclude when Bulk is included'
        return None
