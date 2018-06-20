"""

Copyright (c) 2014 Alex Forencich

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

def I2SControl(clk, rst,
               sck=None,
               ws=None,
               width=16,
               prescale=2):
    
    @instance
    def logic():
        prescale_cnt = 0
        ws_cnt = 0

        while True:
            yield clk.posedge

            if rst:
                sck.next = 0
                ws.next = 0
                prescale_cnt = 0
                ws_cnt = 0
            else:
                if prescale_cnt > 0:
                    prescale_cnt = prescale_cnt - 1;
                else:
                    prescale_cnt = prescale;
                    if sck:
                        sck.next = False
                        if ws_cnt > 0:
                            ws_cnt = ws_cnt - 1
                        else:
                            ws_cnt = width-1
                            ws.next = not ws
                    else:
                        sck.next = True

    return instances()


def I2SSource(clk, rst,
              sck=None,
              ws=None,
              sd=None,
              width=16,
              fifo=None,
              name=None):
    
    @instance
    def logic():
        lst = None
        r_data = 0
        bit_cnt = 0
        last_sck = 0
        last_ws = 0
        sreg = 0

        while True:
            yield clk.posedge

            if rst:
                sd.next = 0
                r_data = 0
                bit_cnt = 0
                last_sck = 0
                last_ws = 0
                sreg = 0
            else:
                if not last_sck and sck:
                    if last_ws != ws:
                        bit_cnt = width

                        if ws:
                            sreg = r_data
                        else:
                            d = (0,0)
                            if lst is None or len(lst) == 0:
                                if not fifo.empty():
                                    d = fifo.get(False)
                                if type(d) is list:
                                    lst = d
                                    d = lst.pop(0)
                            else:
                                d = lst.pop(0)
                            sreg, r_data = d
                            if name is not None:
                                print("[%s] Sending I2S data (%d, %d)" % (name, sreg, r_data))

                    last_ws = int(ws)

                if last_sck and not sck:
                    if bit_cnt > 0:
                        bit_cnt = bit_cnt - 1
                        sd.next = sreg & (1 << bit_cnt) != 0

                last_sck = int(sck)


    return logic


def I2SSink(clk, rst,
            sck=None,
            ws=None,
            sd=None,
            width=16,
            fifo=None,
            name=None):
    
    @instance
    def logic():
        l_data = 0
        bit_cnt = 0
        last_sck = 0
        last_ws = 0
        last_ws2 = 0
        sreg = 0

        while True:
            yield clk.posedge

            if rst:
                l_data = 0
                bit_cnt = 0
                last_sck = 0
                last_ws = 0
                last_ws2 = 0
                sreg = 0
            else:
                if not last_sck and sck:
                    if last_ws2 != last_ws:
                        bit_cnt = width-1
                        sreg = int(sd)
                    elif bit_cnt > 0:
                        if bit_cnt > 1:
                            sreg = (sreg << 1) | int(sd)
                        elif last_ws2:
                            d = (sreg << 1) | int(sd)
                            fifo.put((l_data, d))
                            if name is not None:
                                print("[%s] Got I2S data (%d, %d)" % (name, l_data, d))
                        else:
                            l_data = (sreg << 1) | int(sd)

                        bit_cnt = bit_cnt - 1

                    last_ws2 = last_ws
                    last_ws = int(ws)

                last_sck = int(sck)

    return instances()

