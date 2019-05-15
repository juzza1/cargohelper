# Semi-imported from grf wiki


class CargoClass:
    def __init__(self, value, name, name_nml, wagon_type, usage, tips):
        self.value = value
        self.name = name
        self.name_nml = name_nml
        self.wagon_type = wagon_type
        self.usage = usage
        self.tips = tips
        self.labels = set()

    def __contains__(self, item):
        return item in self.labels

    def __iter__(self):
        return iter(self.labels)

    def __str__(self):
        return self.name


passengers = CargoClass(
    value=0x1,
    name='Passengers',
    name_nml='CC_PASSENGERS',
    wagon_type='passenger wagon',
    usage='OR',
    tips='never exclude'
)
mail = CargoClass(
    value=0x2,
    name='Mail',
    name_nml='CC_MAIL',
    wagon_type='closed or mail wagon',
    usage='OR',
    tips='never exclude'
)
express = CargoClass(
    value=0x4,
    name='Express',
    name_nml='CC_EXPRESS',
    wagon_type='closed or mail wagon',
    usage='OR',
    tips='never exclude, suitable for airplane or maglev'
)
armored = CargoClass(
    value=0x8,
    name='Armored',
    name_nml='CC_ARMOURED',
    wagon_type='armored or mail wagon',
    usage='OR',
    tips='never exclude'
)
bulk = CargoClass(
    value=0x10,
    name='Bulk (Uncountable)',
    name_nml='CC_BULK',
    wagon_type='open or hopper wagon',
    usage='OR',
    tips='never exclude'
)
piece_goods = CargoClass(
    value=0x20,
    name='Piece Goods (Countable)',
    name_nml='CC_PIECE_GOODS',
    wagon_type='closed or open wagon',
    usage='OR',
    tips='never exclude'
)
liquid = CargoClass(
    value=0x40,
    name='Liquid',
    name_nml='CC_LIQUID',
    wagon_type='tank wagon',
    usage='OR',
    tips='never exclude'
)
refrigerated = CargoClass(
    value=0x80,
    name='Refrigerated',
    name_nml='CC_REFRIGERATED',
    wagon_type='refrigerated wagon',
    usage='OR/AND NOT',
    tips='only exclude, when Piece Goods included'
)
hazardous = CargoClass(
    value=0x100,
    name='Hazardous',
    name_nml='CC_HAZARDOUS',
    wagon_type='unknown',
    usage='OR/AND NOT',
    tips='only exclude, when special wagons are provided.'
)
covered = CargoClass(
    value=0x200,
    name='Covered (weather protected)',
    name_nml='CC_COVERED',
    wagon_type='closed wagon, any other wagon with tarpaulin or weather cover',
    usage='OR/AND NOT',
    tips='do not exclude for Liquid'
)
oversized = CargoClass(
    value=0x400,
    name='Oversized',
    name_nml='CC_OVERSIZED',
    wagon_type='stake/flatbed wagon',
    usage='OR/AND NOT',
    tips='only exclude, when Piece Goods included'
)
powderized = CargoClass(
    value=0x800,
    name='Powderized (moist protected)',
    name_nml='CC_POWDERIZED',
    wagon_type='powder/silo wagon',
    usage='OR/AND NOT',
    tips='only exclude, when Bulk included'
)
non_pourable = CargoClass(
    value=0x1000,
    name='Not Pourable',
    name_nml='CC_NON_POURABLE',
    wagon_type='open wagon, but not hopper wagon',
    usage='AND NOT',
    tips='only exclude, when Bulk included'
)
all = [
    passengers, mail, express, armored, bulk, piece_goods, liquid,
    refrigerated, hazardous, covered, oversized, powderized, non_pourable
]


if __name__ == '__main__':
    obj_str = lambda obj: '\n'.join(
        [str(i) for i in sorted(obj.__dict__.items())])
    print('\n\n'.join(obj_str(cc) for cc in all))
