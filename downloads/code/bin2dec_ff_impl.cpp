/* -*- c++ -*- */
/* 
 * Copyright 2014 <+YOU OR YOUR COMPANY+>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "bin2dec_ff_impl.h"
#include <math.h>

namespace gr {
  namespace Tu_modulo {

    bin2dec_ff::sptr
    bin2dec_ff::make(int vec_size)
    {
      return gnuradio::get_initial_sptr
        (new bin2dec_ff_impl(vec_size));
    }

    /*
     * The private constructor
     */
    bin2dec_ff_impl::bin2dec_ff_impl(int vec_size)
      : gr::sync_decimator("bin2dec_ff",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(1, 1, sizeof(float)), vec_size)
    {
    	chunk = vec_size;
    }

    /*
     * Our virtual destructor.
     */
    bin2dec_ff_impl::~bin2dec_ff_impl()
    {
    }

    int
    bin2dec_ff_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
   {
        const float *in = (const float *) input_items[0];
        float *out = (float *) output_items[0];

        int j = 0, a = 0;
        for (int i = 0; i < noutput_items * chunk; i = i + chunk){
        	out[j] = 0;
        	a = chunk - 1;
        	for (int k = 0; k < chunk; k++){
        		out[j] = out[j] + (in[i + k] * pow (2,a));
        		a = a - 1;
        	}
        	j++;
        }

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace Tu_modulo */
} /* namespace gr */

