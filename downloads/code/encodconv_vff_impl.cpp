/* -*- c++ -*- */
/* 
 * Copyright 2014 IVAN RODRIGUEZ.
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
#include "encodconv_vff_impl.h"
#include <itpp/itcomm.h>

namespace gr {
  namespace Tu_modulo {

    encodconv_vff::sptr
    encodconv_vff::make(int val1, int val2, int val3)
    {
      return gnuradio::get_initial_sptr
        (new encodconv_vff_impl(val1, val2, val3));
    }

    /*
     * The private constructor
     */
    encodconv_vff_impl::encodconv_vff_impl(int val1, int val2, int val3)
      : gr::sync_block("encodconv_vff",
              gr::io_signature::make(1, 1, sizeof(float) * val3),
              gr::io_signature::make(1, 1, sizeof(float) * val3 * sizeof(val1)))
    {
    	polsize = sizeof(val1);
		cl = val2;
		pz = val3;
  
		for (int i = 0; i < 0x100; i++){
			polynom[i] = i;
		}
		
		memcpy(polynom, (char*)&val1, sizeof(val1));
		
		// -- Channel code parameters --

		itpp::ivec generator(polsize);

		for (int i = 0; i < polsize; i++){
			generator[i] = polynom[i];
		}

		code.set_generator_polynomials(generator, cl);	
    }

    /*
     * Our virtual destructor.
     */
    encodconv_vff_impl::~encodconv_vff_impl()
    {
    }

    int
    encodconv_vff_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const float *in = (const float *) input_items[0];
        float *out = (float *) output_items[0];

        itpp::bvec tempin(pz * sizeof(float));
		itpp::bvec tempout(pz * polsize * sizeof(float));
  
		for (int j = 0; j < (pz * sizeof(float)); j++){
			tempin[j] = in[j];
		}	

		code.encode_tailbite(tempin, tempout);

		for (int k = 0; k < (pz * polsize * sizeof(float)); k++){
			out[k] = tempout[k];
		}

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace Tu_modulo */
} /* namespace gr */

