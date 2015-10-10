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

import numpy as np

import axis_ep

module = 'sine_dds'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("../rtl/phase_accumulator.v")
srcs.append("../rtl/sine_dds_lut.v")
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_sine_dds(clk,
                 rst,
                 current_test,

                 input_phase_tdata,
                 input_phase_tvalid,
                 input_phase_tready,

                 input_phase_step_tdata,
                 input_phase_step_tvalid,
                 input_phase_step_tready,

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

                input_phase_step_tdata=input_phase_step_tdata,
                input_phase_step_tvalid=input_phase_step_tvalid,
                input_phase_step_tready=input_phase_step_tready,

                output_sample_i_tdata=output_sample_i_tdata,
                output_sample_q_tdata=output_sample_q_tdata,
                output_sample_tvalid=output_sample_tvalid,
                output_sample_tready=output_sample_tready)

def bench():

    # Parameters
    PHASE_WIDTH = 32
    OUTPUT_WIDTH = 16
    INITIAL_PHASE = 0
    INITIAL_PHASE_STEP = 0

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    input_phase_tdata = Signal(intbv(0)[PHASE_WIDTH:])
    input_phase_tvalid = Signal(bool(0))
    input_phase_step_tdata = Signal(intbv(0)[PHASE_WIDTH:])
    input_phase_step_tvalid = Signal(bool(0))
    output_sample_tready = Signal(bool(0))

    # Outputs
    input_phase_tready = Signal(bool(0))
    input_phase_step_tready = Signal(bool(1))
    output_sample_i_tdata = Signal(intbv(0)[OUTPUT_WIDTH:])
    output_sample_q_tdata = Signal(intbv(0)[OUTPUT_WIDTH:])
    output_sample_tvalid = Signal(bool(1))

    # sources and sinks
    phase_source_queue = Queue()
    phase_source_pause = Signal(bool(0))
    phase_step_source_queue = Queue()
    phase_step_source_pause = Signal(bool(0))
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

    phase_step_source = axis_ep.AXIStreamSource(clk,
                                                rst,
                                                tdata=input_phase_step_tdata,
                                                tvalid=input_phase_step_tvalid,
                                                tready=input_phase_step_tready,
                                                fifo=phase_step_source_queue,
                                                pause=phase_step_source_pause,
                                                name='phase_step_source')

    sample_sink = axis_ep.AXIStreamSink(clk,
                                        rst,
                                        tdata=(output_sample_i_tdata, output_sample_q_tdata),
                                        tvalid=output_sample_tvalid,
                                        tready=output_sample_tready,
                                        fifo=sample_sink_queue,
                                        pause=sample_sink_pause,
                                        name='sample_sink')

    # DUT
    dut = dut_sine_dds(clk,
                       rst,
                       current_test,

                       input_phase_tdata,
                       input_phase_tvalid,
                       input_phase_tready,

                       input_phase_step_tdata,
                       input_phase_step_tvalid,
                       input_phase_step_tready,

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
        print("test 1: high frequency")
        current_test.next = 1

        fcw = int(2**PHASE_WIDTH / 100)
        offset = 0

        test_frame1 = axis_ep.AXIStreamFrame()
        test_frame1.data = [offset]
        test_frame2 = axis_ep.AXIStreamFrame()
        test_frame2.data = [fcw]

        phase_source_queue.put(test_frame1)
        phase_step_source_queue.put(test_frame2)

        yield clk.posedge
        yield clk.posedge

        while not sample_sink_queue.empty():
            sample_sink_queue.get(False)

        yield delay(1000)

        for j in range(6):
            sample_sink_queue.get(False)

        for j in range(100):
            rx_frame = sample_sink_queue.get(False)
            INPUT_WIDTH = OUTPUT_WIDTH+2
            x = int((fcw*j + offset) / 2**(PHASE_WIDTH-INPUT_WIDTH))
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
        print("test 2: low frequency")
        current_test.next = 2

        fcw = int(2**PHASE_WIDTH / 10000)
        offset = 0

        test_frame1 = axis_ep.AXIStreamFrame()
        test_frame1.data = [offset]
        test_frame2 = axis_ep.AXIStreamFrame()
        test_frame2.data = [fcw]

        phase_source_queue.put(test_frame1)
        phase_step_source_queue.put(test_frame2)

        yield clk.posedge
        yield clk.posedge

        while not sample_sink_queue.empty():
            sample_sink_queue.get(False)

        yield delay(1000)

        for j in range(6):
            sample_sink_queue.get(False)

        for j in range(100):
            rx_frame = sample_sink_queue.get(False)
            INPUT_WIDTH = OUTPUT_WIDTH+2
            x = int((fcw*j + offset) / 2**(PHASE_WIDTH-INPUT_WIDTH))
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
        print("test 3: phase offset")
        current_test.next = 3

        fcw = int(2**PHASE_WIDTH / 10000)
        offset = 2**(PHASE_WIDTH-2)

        test_frame1 = axis_ep.AXIStreamFrame()
        test_frame1.data = [offset]
        test_frame2 = axis_ep.AXIStreamFrame()
        test_frame2.data = [fcw]

        phase_source_queue.put(test_frame1)
        phase_step_source_queue.put(test_frame2)

        yield clk.posedge
        yield clk.posedge

        while not sample_sink_queue.empty():
            sample_sink_queue.get(False)

        yield delay(1000)

        for j in range(6):
            sample_sink_queue.get(False)

        for j in range(100):
            rx_frame = sample_sink_queue.get(False)
            INPUT_WIDTH = OUTPUT_WIDTH+2
            x = int((fcw*j + offset) / 2**(PHASE_WIDTH-INPUT_WIDTH))
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

        raise StopSimulation

    return dut, phase_source, phase_step_source, sample_sink, clkgen, check

def test_bench():
    sim = Simulation(bench())
    sim.run()

if __name__ == '__main__':
    print("Running test...")
    test_bench()
