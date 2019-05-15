#!/usr/bin/env python3

# Parses cargo classes from newgrf wiki
# Outputs python dict elements, nml names have to added manually

from bs4 import BeautifulSoup
import requests


def main():
    r = requests.get('https://newgrf-specs.tt-wiki.net/wiki/Action0/Cargos')
    s = BeautifulSoup(r.text, 'html.parser')
    h = s.find(class_='mw-headline', string='CargoClasses (16)')
    table = h.parent.find_next_sibling('table')
    rows = []
    for tr in table.find_all('tr'):
        rows.append([td.get_text().strip() for td in tr.find_all('td')])
    rows = rows[1:-3]
    for r in rows:
        print('value=0x{}'.format(r[1]))
        print("class_name='{}'".format(r[2]))
        print("wagon_type='{}'".format(r[3]))
        print("usage='{}'".format(r[4]))
        print("tips='{}'".format(r[5]))
        print()


if __name__ == '__main__':
    main()
