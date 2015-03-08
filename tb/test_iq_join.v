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
 * Testbench for iq_join
 */
module test_iq_join;

// Parameters
parameter WIDTH = 16;

// Inputs
reg clk = 0;
reg rst = 0;
reg [7:0] current_test = 0;

reg [WIDTH-1:0] input_i_tdata = 0;
reg input_i_tvalid = 0;
reg [WIDTH-1:0] input_q_tdata = 0;
reg input_q_tvalid = 0;
reg output_tready = 0;

// Outputs
wire input_i_tready;
wire input_q_tready;
wire [WIDTH-1:0] output_i_tdata;
wire [WIDTH-1:0] output_q_tdata;
wire output_tvalid;

initial begin
    // myhdl integration
    $from_myhdl(clk,
                rst,
                current_test,
                input_i_tdata,
                input_i_tvalid,
                input_q_tdata,
                input_q_tvalid,
                output_tready);
    $to_myhdl(input_i_tready,
              input_q_tready,
              output_i_tdata,
              output_q_tdata,
              output_tvalid);

    // dump file
    $dumpfile("test_iq_join.lxt");
    $dumpvars(0, test_iq_join);
end

iq_join #(
    .WIDTH(WIDTH)
)
UUT (
    .clk(clk),
    .rst(rst),
    .input_i_tdata(input_i_tdata),
    .input_i_tvalid(input_i_tvalid),
    .input_i_tready(input_i_tready),
    .input_q_tdata(input_q_tdata),
    .input_q_tvalid(input_q_tvalid),
    .input_q_tready(input_q_tready),
    .output_i_tdata(output_i_tdata),
    .output_q_tdata(output_q_tdata),
    .output_tvalid(output_tvalid),
    .output_tready(output_tready)
);

endmodule
