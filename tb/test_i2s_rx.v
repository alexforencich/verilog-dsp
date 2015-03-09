/*

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

*/

// Language: Verilog 2001

`timescale 1ns / 1ps

/*
 * Testbench for i2s_rx
 */
module test_i2s_rx;

// Parameters
parameter WIDTH = 16;

// Inputs
reg clk = 0;
reg rst = 0;
reg [7:0] current_test = 0;

reg sck = 0;
reg ws = 0;
reg sd = 0;
reg output_tready = 0;

// Outputs
wire [WIDTH-1:0] output_l_tdata;
wire [WIDTH-1:0] output_r_tdata;
wire output_tvalid;

initial begin
    // myhdl integration
    $from_myhdl(clk,
                rst,
                current_test,
                sck,
                ws,
                sd,
                output_tready);
    $to_myhdl(output_l_tdata,
              output_r_tdata,
              output_tvalid);

    // dump file
    $dumpfile("test_i2s_rx.lxt");
    $dumpvars(0, test_i2s_rx);
end

i2s_rx #(
    .WIDTH(WIDTH)
)
UUT (
    .clk(clk),
    .rst(rst),
    .sck(sck),
    .ws(ws),
    .sd(sd),
    .output_l_tdata(output_l_tdata),
    .output_r_tdata(output_r_tdata),
    .output_tvalid(output_tvalid),
    .output_tready(output_tready)
);

endmodule
