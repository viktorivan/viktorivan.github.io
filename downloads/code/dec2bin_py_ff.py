#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2015 IVAN RODRIGUEZ.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr

class dec2bin_py_ff(gr.interp_block):
    """
    docstring for block dec2bin_py_ff
    """
    def __init__(self, vec_size):
        gr.interp_block.__init__(self,
            name="dec2bin_py_ff",
            in_sig=[numpy.float32],
            out_sig=[numpy.float32], interp=vec_size)
	self.vec_size=vec_size


    def work(self, input_items, output_items):
		in0 = input_items[0]
		out = output_items[0]
		f=numpy.zeros([len(in0),self.vec_size])
		for i in range(0,len(in0)):
			f[i,:] = numpy.int_([str(x) for x in numpy.binary_repr(in0[i], width = self.vec_size)])*1.0
		out[:] = numpy.hstack(f)
		return len(output_items[0])

