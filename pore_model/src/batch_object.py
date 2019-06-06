#!/usr/bin/env python
from itertools import cycle
import numpy as np

class batch_object(object):
	"""docstring for batch_object"""
	def __init__(self, data_list, batch_size):
		super(batch_object, self).__init__()
		self.data_list = data_list
		self.batch_size = batch_size
		self.pool = cycle(data_list)
		
	def next_batch(self):
		data_batch = list()
		for i in xrange(self.batch_size):
			data_batch.append(next(self.pool))
		data_batch = np.array(data_batch)
		return data_batch


