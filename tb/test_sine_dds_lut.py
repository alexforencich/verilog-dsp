#!/usr/bin/env python2
"""

Copyright (c) 2015 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from myhdl import *
import os
from Queue import Queue
import numpy as np

import axis_ep

module = 'sine_dds_lut'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_sine_dds_lut(clk,
                     rst,
                     current_test,

                     input_phase_tdata,
                     input_phase_tvalid,
                     input_phase_tready,

                     output_sample_i_tdata,
                     output_sample_q_tdata,
                     output_sample_tvalid,
                     output_sample_tready):

    if os.system(build_cmd):
        raise Exception("Error running build command")
    return Cosimulation("vvp -m myhdl test_%s.vvp -lxt2" % module,
                clk=clk,
                rst=rst,
                current_test=current_test,

                input_phase_tdata=input_phase_tdata,
                input_phase_tvalid=input_phase_tvalid,
                input_phase_tready=input_phase_tready,

                output_sample_i_tdata=output_sample_i_tdata,
                output_sample_q_tdata=output_sample_q_tdata,
                output_sample_tvalid=output_sample_tvalid,
                output_sample_tready=output_sample_tready)

def bench():

    # Parameters
    OUTPUT_WIDTH = 16
    INPUT_WIDTH = OUTPUT_WIDTH+2

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    input_phase_tdata = Signal(intbv(0)[INPUT_WIDTH:])
    input_phase_tvalid = Signal(bool(0))
    output_sample_tready = Signal(bool(0))

    # Outputs
    input_phase_tready = Signal(bool(0))
    output_sample_i_tdata = Signal(intbv(0)[OUTPUT_WIDTH:])
    output_sample_q_tdata = Signal(intbv(0)[OUTPUT_WIDTH:])
    output_sample_tvalid = Signal(bool(0))

    # sources and sinks
    phase_source_queue = Queue()
    phase_source_pause = Signal(bool(0))
    sample_sink_queue = Queue()
    sample_sink_pause = Signal(bool(0))

    phase_source = axis_ep.AXIStreamSource(clk,
                                           rst,
                                           tdata=input_phase_tdata,
                                           tvalid=input_phase_tvalid,
                                           tready=input_phase_tready,
                                           fifo=phase_source_queue,
                                           pause=phase_source_pause,
                                           name='phase_source')

    sample_sink = axis_ep.AXIStreamSink(clk,
                                        rst,
                                        tdata=(output_sample_i_tdata, output_sample_q_tdata),
                                        tvalid=output_sample_tvalid,
                                        tready=output_sample_tready,
                                        fifo=sample_sink_queue,
                                        pause=sample_sink_pause,
                                        name='sample_sink')

    # DUT
    dut = dut_sine_dds_lut(clk,
                           rst,
                           current_test,

                           input_phase_tdata,
                           input_phase_tvalid,
                           input_phase_tready,

                           output_sample_i_tdata,
                           output_sample_q_tdata,
                           output_sample_tvalid,
                           output_sample_tready)

    @always(delay(4))
    def clkgen():
        clk.next = not clk

    @instance
    def check():
        yield delay(100)
        yield clk.posedge
        rst.next = 1
        yield clk.posedge
        rst.next = 0
        yield clk.posedge
        yield delay(100)
        yield clk.posedge

        # testbench stimulus

        yield clk.posedge
        print("test 1: coarse check")
        current_test.next = 1

        # check single cycle
        test_frame = axis_ep.AXIStreamFrame()
        test_frame.data = list(range(0,2**18,2**10)) + [0]*6

        phase_source_queue.put(test_frame)

        yield clk.posedge
        yield clk.posedge

        while not phase_source_queue.empty() or input_phase_tvalid:
            yield clk.posedge

        yield clk.posedge
        yield clk.posedge

        # pipeline delay
        for j in range(6):
            sample_sink_queue.get(False)

        for j in range(len(test_frame.data)-6):
            rx_frame = sample_sink_queue.get(False)
            x = test_frame.data[j]
            c, s = rx_frame.data[0]

            # sign bit
            if c >= 2**(OUTPUT_WIDTH-1):
                c -= 2**OUTPUT_WIDTH
            if s >= 2**(OUTPUT_WIDTH-1):
                s -= 2**OUTPUT_WIDTH
            
            # reference sine and cosine
            rc = int(np.cos(2*np.pi*(x-2**((INPUT_WIDTH-2)/2-1))/2**INPUT_WIDTH)*(2**(OUTPUT_WIDTH-1)-1))
            rs = int(np.sin(2*np.pi*(x-2**((INPUT_WIDTH-2)/2-1))/2**INPUT_WIDTH)*(2**(OUTPUT_WIDTH-1)-1))

            # assert error of two counts or less
            assert abs(c-rc) <= 2
            assert abs(s-rs) <= 2

        yield clk.posedge
        print("test 2: fine check")
        current_test.next = 2

        # check two zero crossing regions
        test_frame = axis_ep.AXIStreamFrame()
        test_frame.data = list(range(2**18-2**8,2**18-1)) + list(range(0,2**8)) + list(range(2**16-2**8, 2**16+2**8)) + [0]*6

        phase_source_queue.put(test_frame)

        yield clk.posedge
        yield clk.posedge

        while not phase_source_queue.empty() or input_phase_tvalid:
            yield clk.posedge

        yield clk.posedge
        yield clk.posedge

        # pipeline delay
        for j in range(6):
            sample_sink_queue.get(False)

        for j in range(len(test_frame.data)-6):
            rx_frame = sample_sink_queue.get(False)
            x = test_frame.data[j]
            c, s = rx_frame.data[0]

            # sign bit
            if c >= 2**(OUTPUT_WIDTH-1):
                c -= 2**OUTPUT_WIDTH
            if s >= 2**(OUTPUT_WIDTH-1):
                s -= 2**OUTPUT_WIDTH
            
            # reference sine and cosine
            rc = int(np.cos(2*np.pi*(x-2**((INPUT_WIDTH-2)/2-1))/2**INPUT_WIDTH)*(2**(OUTPUT_WIDTH-1)-1))
            rs = int(np.sin(2*np.pi*(x-2**((INPUT_WIDTH-2)/2-1))/2**INPUT_WIDTH)*(2**(OUTPUT_WIDTH-1)-1))

            # assert error of two counts or less
            assert abs(c-rc) <= 2
            assert abs(s-rs) <= 2

        yield delay(100)

        raise StopSimulation

    return dut, phase_source, sample_sink, clkgen, check

def test_bench():
    sim = Simulation(bench())
    sim.run()

if __name__ == '__main__':
    print("Running test...")
    test_bench()
