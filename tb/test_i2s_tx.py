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
import i2s_ep

module = 'i2s_tx'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_i2s_tx(clk,
               rst,
               current_test,
               input_l_tdata,
               input_r_tdata,
               input_tvalid,
               input_tready,
               sck,
               ws,
               sd):

    if os.system(build_cmd):
        raise Exception("Error running build command")
    return Cosimulation("vvp -m myhdl test_%s.vvp -lxt2" % module,
                clk=clk,
                rst=rst,
                current_test=current_test,
                input_l_tdata=input_l_tdata,
                input_r_tdata=input_r_tdata,
                input_tvalid=input_tvalid,
                input_tready=input_tready,
                sck=sck,
                ws=ws,
                sd=sd)

def bench():

    # Parameters
    WIDTH = 16

    i2s_ctrl_width = Signal(intbv(WIDTH))

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    input_l_tdata = Signal(intbv(0)[WIDTH:])
    input_r_tdata = Signal(intbv(0)[WIDTH:])
    input_tvalid = Signal(bool(0))
    sck = Signal(bool(0))
    ws = Signal(bool(0))

    # Outputs
    input_tready = Signal(bool(0))
    sd = Signal(bool(0))

    # Sources and sinks
    input_source_queue = Queue()
    input_source_pause = Signal(bool(0))
    output_sink_queue = Queue()

    input_source = axis_ep.AXIStreamSource(clk,
                                           rst,
                                           tdata=(input_l_tdata, input_r_tdata),
                                           tvalid=input_tvalid,
                                           tready=input_tready,
                                           fifo=input_source_queue,
                                           pause=input_source_pause,
                                           name='input_source')

    i2s_ctrl = i2s_ep.I2SControl(clk,
                                 rst,
                                 sck=sck,
                                 ws=ws,
                                 width=i2s_ctrl_width,
                                 prescale=2)

    i2s_sink = i2s_ep.I2SSink(clk,
                              rst,
                              sck=sck,
                              ws=ws,
                              sd=sd,
                              width=WIDTH,
                              fifo=output_sink_queue,
                              name='sink')

    # DUT
    dut = dut_i2s_tx(clk,
                     rst,
                     current_test,
                     input_l_tdata,
                     input_r_tdata,
                     input_tvalid,
                     input_tready,
                     sck,
                     ws,
                     sd)

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
        print("test 1: test ramp")
        current_test.next = 1

        y_l = list(range(0,4096,128))
        y_r = list(range(4096-128,-128,-128))
        y = list(zip(y_l, y_r))

        input_source_queue.put(y)

        yield clk.posedge
        yield clk.posedge

        while input_tvalid:
            yield clk.posedge

        yield clk.posedge

        yield delay(3000)

        lst = []

        while not output_sink_queue.empty():
            lst.append(output_sink_queue.get(False))

        assert contains(y, lst)

        yield delay(100)

        yield clk.posedge
        print("test 2: trailing zeros")
        current_test.next = 2

        i2s_ctrl_width.next = 24

        yield delay(100)
        yield clk.posedge
        rst.next = 1
        yield clk.posedge
        rst.next = 0
        yield clk.posedge
        yield delay(100)
        yield clk.posedge

        y_l = list(range(0,4096,128))
        y_r = list(range(4096-128,-128,-128))
        y = list(zip(y_l, y_r))

        input_source_queue.put(y)

        yield clk.posedge
        yield clk.posedge

        while input_tvalid:
            yield clk.posedge

        yield clk.posedge

        yield delay(5000)

        lst = []

        while not output_sink_queue.empty():
            lst.append(output_sink_queue.get(False))

        assert contains(y, lst)

        yield delay(100)

        raise StopSimulation

    return dut, input_source, i2s_ctrl, i2s_sink, clkgen, check

def contains(small, big):
    for i in range(len(big)-len(small)+1):
        for j in range(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return i, i+len(small)
    return False

def test_bench():
    sim = Simulation(bench())
    sim.run()

if __name__ == '__main__':
    print("Running test...")
    test_bench()
