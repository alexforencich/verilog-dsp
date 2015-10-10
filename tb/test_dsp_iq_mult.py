#!/usr/bin/env python
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

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

import axis_ep

module = 'dsp_iq_mult'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_dsp_iq_mult(clk,
                    rst,
                    current_test,
                    input_a_i_tdata,
                    input_a_q_tdata,
                    input_a_tvalid,
                    input_a_tready,
                    input_b_i_tdata,
                    input_b_q_tdata,
                    input_b_tvalid,
                    input_b_tready,
                    output_i_tdata,
                    output_q_tdata,
                    output_tvalid,
                    output_tready):

    if os.system(build_cmd):
        raise Exception("Error running build command")
    return Cosimulation("vvp -m myhdl test_%s.vvp -lxt2" % module,
                clk=clk,
                rst=rst,
                current_test=current_test,
                input_a_i_tdata=input_a_i_tdata,
                input_a_q_tdata=input_a_q_tdata,
                input_a_tvalid=input_a_tvalid,
                input_a_tready=input_a_tready,
                input_b_i_tdata=input_b_i_tdata,
                input_b_q_tdata=input_b_q_tdata,
                input_b_tvalid=input_b_tvalid,
                input_b_tready=input_b_tready,
                output_i_tdata=output_i_tdata,
                output_q_tdata=output_q_tdata,
                output_tvalid=output_tvalid,
                output_tready=output_tready)

def bench():

    # Parameters
    WIDTH = 16

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    input_a_i_tdata = Signal(intbv(0)[WIDTH:])
    input_a_q_tdata = Signal(intbv(0)[WIDTH:])
    input_a_tvalid = Signal(bool(0))
    input_b_i_tdata = Signal(intbv(0)[WIDTH:])
    input_b_q_tdata = Signal(intbv(0)[WIDTH:])
    input_b_tvalid = Signal(bool(0))
    output_tready = Signal(bool(0))

    # Outputs
    input_a_tready = Signal(bool(0))
    input_b_tready = Signal(bool(0))
    output_i_tdata = Signal(intbv(0)[WIDTH*2:])
    output_q_tdata = Signal(intbv(0)[WIDTH*2:])
    output_tvalid = Signal(bool(0))

    # sources and sinks
    input_a_source_queue = Queue()
    input_a_source_pause = Signal(bool(0))
    input_b_source_queue = Queue()
    input_b_source_pause = Signal(bool(0))
    output_sink_queue = Queue()
    output_sink_pause = Signal(bool(0))

    input_a_source = axis_ep.AXIStreamSource(clk,
                                             rst,
                                             tdata=(input_a_i_tdata, input_a_q_tdata),
                                             tvalid=input_a_tvalid,
                                             tready=input_a_tready,
                                             fifo=input_a_source_queue,
                                             pause=input_a_source_pause,
                                             name='input_a_source')

    input_b_source = axis_ep.AXIStreamSource(clk,
                                             rst,
                                             tdata=(input_b_i_tdata, input_b_q_tdata),
                                             tvalid=input_b_tvalid,
                                             tready=input_b_tready,
                                             fifo=input_b_source_queue,
                                             pause=input_b_source_pause,
                                             name='input_b_source')

    output_sink = axis_ep.AXIStreamSink(clk,
                                       rst,
                                       tdata=(output_i_tdata, output_q_tdata),
                                       tvalid=output_tvalid,
                                       tready=output_tready,
                                       fifo=output_sink_queue,
                                       pause=output_sink_pause,
                                       name='output_sink')

    # DUT
    dut = dut_dsp_iq_mult(clk,
                          rst,
                          current_test,
                          input_a_i_tdata,
                          input_a_q_tdata,
                          input_a_tvalid,
                          input_a_tready,
                          input_b_i_tdata,
                          input_b_q_tdata,
                          input_b_tvalid,
                          input_b_tready,
                          output_i_tdata,
                          output_q_tdata,
                          output_tvalid,
                          output_tready)

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
        print("test 1: test multiplier")
        current_test.next = 1

        test_frame1 = axis_ep.AXIStreamFrame()
        test_frame1.data = [[12, 56]] + [[0,0]]*4
        test_frame2 = axis_ep.AXIStreamFrame()
        test_frame2.data = [[34, 78]] + [[0,0]]*4

        input_a_source_queue.put(test_frame1)
        input_b_source_queue.put(test_frame2)

        yield clk.posedge
        yield clk.posedge
        yield clk.posedge
        yield clk.posedge

        while output_sink_queue.empty():
            yield clk.posedge

        yield clk.posedge
        yield clk.posedge

        for i in range(4):
            rx_frame = output_sink_queue.get(False)

        rx_frame = output_sink_queue.get(False)
        assert rx_frame.data[0] == [12*34,56*78]

        yield delay(100)

        raise StopSimulation

    return dut, input_a_source, input_b_source, output_sink, clkgen, check

def test_bench():
    sim = Simulation(bench())
    sim.run()

if __name__ == '__main__':
    print("Running test...")
    test_bench()
