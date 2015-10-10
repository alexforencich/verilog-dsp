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

module = 'phase_accumulator'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_phase_accumulator(clk,
                          rst,
                          current_test,

                          input_phase_tdata,
                          input_phase_tvalid,
                          input_phase_tready,

                          input_phase_step_tdata,
                          input_phase_step_tvalid,
                          input_phase_step_tready,

                          output_phase_tdata,
                          output_phase_tvalid,
                          output_phase_tready):

    if os.system(build_cmd):
        raise Exception("Error running build command")
    return Cosimulation("vvp -m myhdl test_%s.vvp -lxt2" % module,
                clk=clk,
                rst=rst,
                current_test=current_test,

                input_phase_tdata=input_phase_tdata,
                input_phase_tvalid=input_phase_tvalid,
                input_phase_tready=input_phase_tready,

                input_phase_step_tdata=input_phase_step_tdata,
                input_phase_step_tvalid=input_phase_step_tvalid,
                input_phase_step_tready=input_phase_step_tready,

                output_phase_tdata=output_phase_tdata,
                output_phase_tvalid=output_phase_tvalid,
                output_phase_tready=output_phase_tready)

def bench():

    # Parameters
    WIDTH = 32
    INITIAL_PHASE = 0
    INITIAL_PHASE_STEP = 0

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    input_phase_tdata = Signal(intbv(0)[WIDTH:])
    input_phase_tvalid = Signal(bool(0))
    input_phase_step_tdata = Signal(intbv(0)[WIDTH:])
    input_phase_step_tvalid = Signal(bool(0))
    output_phase_tready = Signal(bool(0))

    # Outputs
    input_phase_tready = Signal(bool(1))
    input_phase_step_tready = Signal(bool(1))
    output_phase_tdata = Signal(intbv(0)[WIDTH:])
    output_phase_tvalid = Signal(bool(1))

    # sources and sinks
    phase_source_queue = Queue()
    phase_source_pause = Signal(bool(0))
    phase_step_source_queue = Queue()
    phase_step_source_pause = Signal(bool(0))
    phase_sink_queue = Queue()
    phase_sink_pause = Signal(bool(0))

    phase_source = axis_ep.AXIStreamSource(clk,
                                           rst,
                                           tdata=input_phase_tdata,
                                           tvalid=input_phase_tvalid,
                                           tready=input_phase_tready,
                                           fifo=phase_source_queue,
                                           pause=phase_source_pause,
                                           name='phase_source')

    phase_step_source = axis_ep.AXIStreamSource(clk,
                                                rst,
                                                tdata=input_phase_step_tdata,
                                                tvalid=input_phase_step_tvalid,
                                                tready=input_phase_step_tready,
                                                fifo=phase_step_source_queue,
                                                pause=phase_step_source_pause,
                                                name='phase_step_source')

    phase_sink = axis_ep.AXIStreamSink(clk,
                                       rst,
                                       tdata=output_phase_tdata,
                                       tvalid=output_phase_tvalid,
                                       tready=output_phase_tready,
                                       fifo=phase_sink_queue,
                                       pause=phase_sink_pause,
                                       name='phase_sink')

    # DUT
    dut = dut_phase_accumulator(clk,
                                rst,
                                current_test,

                                input_phase_tdata,
                                input_phase_tvalid,
                                input_phase_tready,

                                input_phase_step_tdata,
                                input_phase_step_tvalid,
                                input_phase_step_tready,

                                output_phase_tdata,
                                output_phase_tvalid,
                                output_phase_tready)

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
        print("test 1: initial phase")
        current_test.next = 1

        test_frame = axis_ep.AXIStreamFrame()
        test_frame.data = [123456]

        phase_source_queue.put(test_frame)

        yield clk.posedge
        yield clk.posedge

        while not phase_sink_queue.empty():
            phase_sink_queue.get(False)

        yield clk.posedge
        yield clk.posedge

        rx_frame = phase_sink_queue.get(False)
        assert rx_frame.data[0] == 123456

        yield delay(100)

        yield clk.posedge
        print("test 2: phase step")
        current_test.next = 2

        test_frame1 = axis_ep.AXIStreamFrame()
        test_frame1.data = [10000]
        test_frame2 = axis_ep.AXIStreamFrame()
        test_frame2.data = [5000]

        phase_source_queue.put(test_frame1)
        phase_step_source_queue.put(test_frame2)

        yield clk.posedge
        yield clk.posedge

        while not phase_sink_queue.empty():
            phase_sink_queue.get(False)

        yield clk.posedge
        yield clk.posedge
        yield clk.posedge

        rx_frame = phase_sink_queue.get(False)
        assert rx_frame.data[0] == 10000
        rx_frame = phase_sink_queue.get(False)
        assert rx_frame.data[0] == 15000
        rx_frame = phase_sink_queue.get(False)
        assert rx_frame.data[0] == 20000

        yield delay(100)

        raise StopSimulation

    return dut, phase_source, phase_step_source, phase_sink, clkgen, check

def test_bench():
    sim = Simulation(bench())
    sim.run()

if __name__ == '__main__':
    print("Running test...")
    test_bench()
