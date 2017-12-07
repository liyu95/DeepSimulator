#!/bin/python
import pandas as pd
import numpy as np
with open('mapping.paf', 'r') as f:
	text = f.read()
	lines = text.splitlines()

match = np.array(map(lambda x: float(x.split()[9]), lines))
size = np.array(map(lambda x: float(x.split()[10]), lines))

# df = pd.read_table('mapping.paf', header=None)
# match = df.iloc[:,9].values.astype(float)
# size = df.iloc[:,10].values.astype(float)
acc = match/size
print(acc.mean())