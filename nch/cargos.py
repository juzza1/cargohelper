import nch.labels
import nch.classes


class Cargos:
    def __init__(self, ignore_unknown_labels=True):
        self.labels = []
        self.classes = nch.classes.all
        self.ignore_unknown_labels = ignore_unknown_labels

    def refresh(self):
        self.labels = []
        for lb in nch.labels.fetch_labels():
            if self.ignore_unknown_labels and not lb.industries:
                continue
            self.labels.append(lb)
        self.classes = nch.classes.all
        # Map classes to labels, and vice versa
        for lb in self.labels:
            for cl in self.classes:
                if lb.bitmask & cl.value:
                    lb.classes.add(cl)
                    cl.labels.add(lb)

    def check_inclusion(self, incl_cc, excl_ccs):
        """Check if cargo class is "safe" to be included according to
           https://newgrf-specs.tt-wiki.net/wiki/Action0/Cargos#CargoClasses_.2816.29"""
        if incl_cc == nch.classes.non_pourable:
            return 'Never include this class'
        return None

    def check_exclusion(self, excl_cc, incl_ccs):
        """Check if cargo class is "safe" to be excluded according to
           https://newgrf-specs.tt-wiki.net/wiki/Action0/Cargos#CargoClasses_.2816.29"""

        never_exclude = {nch.classes.passengers, nch.classes.mail,
                         nch.classes.express, nch.classes.armored,
                         nch.classes.bulk, nch.classes.piece_goods,
                         nch.classes.liquid}
        if excl_cc in never_exclude:
            return 'Never exclude this class'
        if excl_cc in {nch.classes.refrigerated, nch.classes.oversized} \
                and nch.classes.piece_goods not in incl_ccs:
            return 'Only exclude when Piece Goods is included'
        if excl_cc == nch.classes.hazardous:
            return 'Only exclude when special wagons are provided'
        if excl_cc == nch.classes.covered and nch.classes.liquid in incl_ccs:
            return 'Do not exclude for Liquid'
        if excl_cc in {nch.classes.powderized, nch.classes.non_pourable} \
                and nch.classes.bulk not in incl_ccs:
            return 'Only exclude when Bulk is included'
        return None
