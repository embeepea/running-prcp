#! /usr/bin/python

import re

class Dly:
    """Load and provide access to data from an NCDC GHCN *.dly file."""

    def __init__(self, file):
        self.data = {}
        self.loadfromfile(file)

    def loadfromfile(self, file):
        """
                  10        20        30        40        50
         123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 ...
        USC00010008198112WT03-9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999  
        """
        f = open(file, 'r')
        for line in [x.strip() for x in f]:
            m = re.match(r'^(\S+)(\d{4})(\d{2})(\S{4})\s+.*$', line)
            if m:
                station_id = m.group(1)
                yyyy       = m.group(2)
                mm         = m.group(3)
                element    = m.group(4)
                if element not in self.data:
                    self.data[element] = []
                self.data[element].append({ 'year' : int(yyyy), 'month' : int(mm), 'values' : [ int(line[21+8*i:26+8*i].strip()) for i in range(0,31) ] })
