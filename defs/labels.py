#!/usr/bin/env python3

from collections import OrderedDict
import re
import sys

from bs4 import BeautifulSoup
import requests


class CargoLabel:
    def __init__(self, label, description, bitmask, industries):
        self.label = label
        self.description = description
        self.bitmask = bitmask
        self.industries = industries
        self.classes = set()

    def __contains__(self, item):
        return item in self.classes

    def __iter__(self):
        return iter(self.classes)

    def __str__(self):
        return '{} - {}'.format(self.label, self.description)


def fetch_labels(html_doc=None):

    def match(row):
        if len(row) >= 6 \
                and re.match(r'[A-Z0-9_]', row[0]) \
                and re.match(r'[A-F0-9]{4}', row[2]):
            return True
        return False

    if not html_doc:
        r = requests.get('https://newgrf-specs.tt-wiki.net/wiki/CargoTypes')
        html_doc = r.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    table = soup.find('table')
    labels = []
    for tr in table.find_all('tr'):
        row = list(td.get_text().strip() for td in tr.find_all('td'))
        if row and re.match(r'special cargos', row[0], re.IGNORECASE):
            break
        if not match(row):
            continue
        # Parsing the data is very brittle atm
        label = row[0]
        desc = row[1]
        cc = int(row[2][:4], base=16)
        # Some cargos have different classes in ecs/firs/yeti
        # Some of them are in the notes of the wiki page,
        # try to get the firs classes from these notes
        if len(row) >= 8:
            m = re.search(r'firs[-:., ]+([A-F0-9]{4})', row[7], re.IGNORECASE)
            if m:
                cc = int(m.group(1), base=16)
        industries = [ind for ind in row[3:7] if ind != '']
        labels.append(CargoLabel(label, desc, cc, industries))

    return labels


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8') as f:
            html_doc = f.read()
    else:
        html_doc=None
    lbs = fetch_labels(html_doc)
    for lb in lbs:
        print(lb.__dict__)


if __name__ == '__main__':
    main()
