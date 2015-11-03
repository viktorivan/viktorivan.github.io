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

class bin2dec_py_ff(gr.decim_block):
    """
    docstring for block bin2dec_py_ff
    """
    def __init__(self, vec_size):
        gr.decim_block.__init__(self,
            name="bin2dec_py_ff",
            in_sig=[numpy.float32],
            out_sig=[numpy.float32], decim=vec_size)
	self.vec_size=vec_size



    def work(self, input_items, output_items):
        in0 = numpy.int_(input_items[0])
        out = output_items[0]
        j=0
        for i in range(self.vec_size,len(in0)+1,self.vec_size):
			out[j]= int(str("".join(str(x) for x in in0[i-self.vec_size:i])),2)
			j += 1
        return len(output_items[0])

