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

import i2s_ep

module = 'i2s_ctrl'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_i2s_ctrl(clk,
                 rst,
                 current_test,
                 sck,
                 ws,
                 prescale):

    if os.system(build_cmd):
        raise Exception("Error running build command")
    return Cosimulation("vvp -m myhdl test_%s.vvp -lxt2" % module,
                clk=clk,
                rst=rst,
                current_test=current_test,
                sck=sck,
                ws=ws,
                prescale=prescale)

def bench():

    # Parameters
    WIDTH = 16

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    prescale = Signal(intbv(0)[16:])

    # Outputs
    sck = Signal(bool(0))
    ws = Signal(bool(0))

    sck_check = Signal(bool(0))
    ws_check = Signal(bool(0))

    i2s_ctrl = i2s_ep.I2SControl(clk,
                                 rst,
                                 sck=sck_check,
                                 ws=ws_check,
                                 width=WIDTH,
                                 prescale=prescale)

    # DUT
    dut = dut_i2s_ctrl(clk,
                       rst,
                       current_test,
                       sck,
                       ws,
                       prescale)

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
        print("test 1: no prescaler")
        current_test.next = 1

        for i in range(100):
            print(sck, ws, sck_check, ws_check)
            assert sck == sck_check
            assert ws == ws_check
            yield clk.posedge

        yield delay(100)

        yield clk.posedge
        print("test 2: prescaler of 4")
        current_test.next = 2

        prescale.next = 4

        yield clk.posedge
        rst.next = 1
        yield clk.posedge
        rst.next = 0
        yield clk.posedge
        yield delay(100)
        yield clk.posedge

        for i in range(100):
            print(sck, ws, sck_check, ws_check)
            assert sck == sck_check
            assert ws == ws_check
            yield clk.posedge

        yield delay(100)

        raise StopSimulation

    return dut, i2s_ctrl, clkgen, check

def test_bench():
    sim = Simulation(bench())
    sim.run()

if __name__ == '__main__':
    print("Running test...")
    test_bench()
