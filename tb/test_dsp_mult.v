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
 * Testbench for dsp_mult
 */
module test_dsp_mult;

// Parameters
parameter WIDTH = 16;

// Inputs
reg clk = 0;
reg rst = 0;
reg [7:0] current_test = 0;

reg [WIDTH-1:0] input_a_tdata = 0;
reg input_a_tvalid = 0;
reg [WIDTH-1:0] input_b_tdata = 0;
reg input_b_tvalid = 0;
reg output_tready = 0;

// Outputs
wire input_a_tready;
wire input_b_tready;
wire [(WIDTH*2)-1:0] output_tdata;
wire output_tvalid;

initial begin
    // myhdl integration
    $from_myhdl(clk,
                rst,
                current_test,
                input_a_tdata,
                input_a_tvalid,
                input_b_tdata,
                input_b_tvalid,
                output_tready);
    $to_myhdl(input_a_tready,
              input_b_tready,
              output_tdata,
              output_tvalid);

    // dump file
    $dumpfile("test_dsp_mult.lxt");
    $dumpvars(0, test_dsp_mult);
end

dsp_mult #(
    .WIDTH(WIDTH)
)
UUT (
    .clk(clk),
    .rst(rst),
    .input_a_tdata(input_a_tdata),
    .input_a_tvalid(input_a_tvalid),
    .input_a_tready(input_a_tready),
    .input_b_tdata(input_b_tdata),
    .input_b_tvalid(input_b_tvalid),
    .input_b_tready(input_b_tready),
    .output_tdata(output_tdata),
    .output_tvalid(output_tvalid),
    .output_tready(output_tready)
);

endmodule
