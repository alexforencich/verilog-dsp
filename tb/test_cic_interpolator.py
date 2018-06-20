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
import math

import axis_ep

module = 'cic_interpolator'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_cic_interpolator(clk,
                         rst,
                         current_test,
                         input_tdata,
                         input_tvalid,
                         input_tready,
                         output_tdata,
                         output_tvalid,
                         output_tready,
                         rate):

    if os.system(build_cmd):
        raise Exception("Error running build command")
    return Cosimulation("vvp -m myhdl test_%s.vvp -lxt2" % module,
                clk=clk,
                rst=rst,
                current_test=current_test,
                input_tdata=input_tdata,
                input_tvalid=input_tvalid,
                input_tready=input_tready,
                output_tdata=output_tdata,
                output_tvalid=output_tvalid,
                output_tready=output_tready,
                rate=rate)

def bench():

    # Parameters
    WIDTH = 16
    RMAX = 4
    M = 1
    N = 2
    REG_WIDTH = WIDTH+max(N, math.ceil(math.log10(((RMAX*M)**N)/RMAX)/math.log10(2)))

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    input_tdata = Signal(intbv(0)[WIDTH:])
    input_tvalid = Signal(bool(0))
    output_tready = Signal(bool(0))
    rate = Signal(intbv(0)[math.ceil(math.log10(RMAX+1)/math.log10(2)):])

    # Outputs
    input_tready = Signal(bool(0))
    output_tdata = Signal(intbv(0)[REG_WIDTH:])
    output_tvalid = Signal(bool(0))

    # sources and sinks
    input_source_queue = Queue()
    input_source_pause = Signal(bool(0))
    output_sink_queue = Queue()
    output_sink_pause = Signal(bool(0))
    
    input_source = axis_ep.AXIStreamSource(clk,
                                           rst,
                                           tdata=input_tdata,
                                           tvalid=input_tvalid,
                                           tready=input_tready,
                                           fifo=input_source_queue,
                                           pause=input_source_pause,
                                           name='input_source')

    output_sink = axis_ep.AXIStreamSink(clk,
                                        rst,
                                        tdata=output_tdata,
                                        tvalid=output_tvalid,
                                        tready=output_tready,
                                        fifo=output_sink_queue,
                                        pause=output_sink_pause,
                                        name='output_sink')

    # DUT
    dut = dut_cic_interpolator(clk,
                               rst,
                               current_test,
                               input_tdata,
                               input_tvalid,
                               input_tready,
                               output_tdata,
                               output_tvalid,
                               output_tready,
                               rate)

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

        rate.next = 2

        yield clk.posedge
        print("test 1: impulse response")
        current_test.next = 1

        y = [1, 0, 0, 0, 0]
        ref = cic_interpolate(y, N, M, rate)

        test_frame = axis_ep.AXIStreamFrame()
        test_frame.data = y + [0]*5

        input_source_queue.put(test_frame)
        
        yield clk.posedge
        yield clk.posedge

        while input_tvalid:
            yield clk.posedge

        yield clk.posedge

        lst = []

        while not output_sink_queue.empty():
            lst += output_sink_queue.get(False).data

        print(lst)
        print(ref)
        assert contains(ref, lst)

        yield delay(100)

        yield clk.posedge
        print("test 2: ramp")
        current_test.next = 2

        y = list(range(100)) + [0,0]
        ref = cic_interpolate(y, N, M, rate)

        test_frame = axis_ep.AXIStreamFrame()
        test_frame.data = y + [0]*5
        
        input_source_queue.put(test_frame)
        
        yield clk.posedge
        yield clk.posedge

        while input_tvalid:
            yield clk.posedge

        yield clk.posedge

        lst = []

        while not output_sink_queue.empty():
            lst += output_sink_queue.get(False).data

        print(lst)
        print(ref)
        assert contains(ref, lst)

        yield delay(100)

        yield clk.posedge
        print("test 3: source pause")
        current_test.next = 3

        y = list(range(100)) + [0,0]
        ref = cic_interpolate(y, N, M, rate)

        test_frame = axis_ep.AXIStreamFrame()
        test_frame.data = y + [0]*5
        
        input_source_queue.put(test_frame)
        
        yield clk.posedge
        yield clk.posedge

        while input_tvalid:
            input_source_pause.next = True
            yield clk.posedge
            yield clk.posedge
            yield clk.posedge
            input_source_pause.next = False
            yield clk.posedge

        yield clk.posedge

        lst = []

        while not output_sink_queue.empty():
            lst += output_sink_queue.get(False).data

        print(lst)
        print(ref)
        assert contains(ref, lst)

        yield delay(100)

        yield clk.posedge
        print("test 4: sink pause")
        current_test.next = 4

        y = list(range(100)) + [0,0]
        ref = cic_interpolate(y, N, M, rate)

        test_frame = axis_ep.AXIStreamFrame()
        test_frame.data = y + [0]*5
        
        input_source_queue.put(test_frame)
        
        yield clk.posedge
        yield clk.posedge

        while input_tvalid:
            output_sink_pause.next = True
            yield clk.posedge
            yield clk.posedge
            yield clk.posedge
            output_sink_pause.next = False
            yield clk.posedge

        yield clk.posedge

        lst = []

        while not output_sink_queue.empty():
            lst += output_sink_queue.get(False).data

        print(lst)
        print(ref)
        assert contains(ref, lst)

        yield delay(100)

        yield clk.posedge
        print("test 5: sinewave")
        current_test.next = 5

        x = np.arange(0,100)
        y = np.r_[(np.sin(2*np.pi*x/50)*1024).astype(int), [0,0]]
        ref = cic_interpolate(y, N, M, rate)

        ys = y
        ys[y < 0] += 2**WIDTH

        refs = ref
        refs[ref < 0] += 2**REG_WIDTH

        test_frame = axis_ep.AXIStreamFrame()
        test_frame.data = list(map(int, ys)) + [0]*5
        
        input_source_queue.put(test_frame)
        
        yield clk.posedge
        yield clk.posedge

        while input_tvalid:
            yield clk.posedge

        yield clk.posedge

        lst = []

        while not output_sink_queue.empty():
            lst += output_sink_queue.get(False).data

        print(lst)
        print(ref)
        assert contains(ref, lst)

        yield delay(100)

        yield clk.posedge
        print("test 6: rate of 4")
        current_test.next = 6

        rate.next = 4

        yield clk.posedge

        x = np.arange(0,100)
        y = np.r_[(np.sin(2*np.pi*x/50)*1024).astype(int), [0,0]]
        ref = cic_interpolate(y, N, M, rate)

        ys = y
        ys[y < 0] += 2**WIDTH

        refs = ref
        refs[ref < 0] += 2**REG_WIDTH

        test_frame = axis_ep.AXIStreamFrame()
        test_frame.data = list(map(int, ys)) + [0]*5
        
        input_source_queue.put(test_frame)
        
        yield clk.posedge
        yield clk.posedge

        while input_tvalid:
            yield clk.posedge

        yield clk.posedge

        lst = []

        while not output_sink_queue.empty():
            lst += output_sink_queue.get(False).data

        print(lst)
        print(ref)
        assert contains(ref, lst)

        yield delay(100)

        raise StopSimulation

    return instances()

def cic_interpolate(y, N=2, M=1, R=2):
    y = np.array(y)

    # comb stage
    for i in range(N):
        for j in range(len(y)-1, M-1, -1):
            y[j] = y[j] - y[j-M]

    # upconvert
    y2 = np.zeros(y.shape[0]*R, dtype=y.dtype)
    y2[0::R] = y
    y = y2

    # integrate
    for i in range(N):
        s = 0
        for j in range(len(y)):
            s += y[j]
            y[j] = s

    return y

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
