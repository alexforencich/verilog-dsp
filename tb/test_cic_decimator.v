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
 * Testbench for cic_decimator
 */
module test_cic_decimator;

// Parameters
parameter WIDTH = 16;
parameter RMAX = 4;
parameter M = 1;
parameter N = 2;
parameter REG_WIDTH = WIDTH+$clog2((RMAX*M)**N);

// Inputs
reg clk = 0;
reg rst = 0;
reg [7:0] current_test = 0;

reg [WIDTH-1:0] input_tdata = 0;
reg input_tvalid = 0;
reg output_tready = 0;
reg [$clog2(RMAX+1)-1:0] rate = 0;

// Outputs
wire input_tready;
wire [REG_WIDTH-1:0] output_tdata;
wire output_tvalid;

initial begin
    // myhdl integration
    $from_myhdl(clk,
                rst,
                current_test,
                input_tdata,
                input_tvalid,
                output_tready,
                rate);
    $to_myhdl(input_tready,
              output_tdata,
              output_tvalid);

    // dump file
    $dumpfile("test_cic_decimator.lxt");
    $dumpvars(0, test_cic_decimator);
end

cic_decimator #(
    .WIDTH(WIDTH),
    .RMAX(RMAX),
    .M(M),
    .N(N)
)
UUT (
    .clk(clk),
    .rst(rst),
    .input_tdata(input_tdata),
    .input_tvalid(input_tvalid),
    .input_tready(input_tready),
    .output_tdata(output_tdata),
    .output_tvalid(output_tvalid),
    .output_tready(output_tready),
    .rate(rate)
);

endmodule
