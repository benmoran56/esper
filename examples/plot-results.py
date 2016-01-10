#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import pickle
import sys

from matplotlib import pyplot as plt

if len(sys.argv) < 2:
    sys.exit("Usage: plot-results.py <pickle file>")

with open(sys.argv[1], 'rb') as pf:
    results = pickle.load(pf)

lines = []
for num, result in results.items():
    x, y = zip(*sorted(result.items()))
    label = '%i Component%s' % (num, '' if num == 1 else 's')
    lines.extend(plt.plot(x, y, label=label))

plt.ylabel("Time (ms)")
plt.xlabel("# Entities")
plt.legend(handles=lines, bbox_to_anchor=(0.5, 1))

plt.show()
