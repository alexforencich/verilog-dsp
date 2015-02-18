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
 * Testbench for phase_accumulator
 */
module test_phase_accumulator;

// Parameters
parameter WIDTH = 32;

// Inputs
reg clk = 0;
reg rst = 0;
reg [7:0] current_test = 0;

reg [WIDTH-1:0] input_phase_tdata = 0;
reg input_phase_tvalid = 0;
reg [WIDTH-1:0] input_phase_step_tdata = 0;
reg input_phase_step_tvalid = 0;
reg output_phase_tready = 0;

// Outputs
wire input_phase_tready;
wire input_phase_step_tready;
wire [WIDTH-1:0] output_phase_tdata;
wire output_phase_tvalid;

initial begin
    // myhdl integration
    $from_myhdl(clk,
                rst,
                current_test,
                input_phase_tdata,
                input_phase_tvalid,
                input_phase_step_tdata,
                input_phase_step_tvalid,
                output_phase_tready);
    $to_myhdl(input_phase_tready,
              input_phase_step_tready,
              output_phase_tdata,
              output_phase_tvalid);

    // dump file
    $dumpfile("test_phase_accumulator.lxt");
    $dumpvars(0, test_phase_accumulator);
end

phase_accumulator #(
    .WIDTH(WIDTH)
)
UUT (
    .clk(clk),
    .rst(rst),
    .input_phase_tdata(input_phase_tdata),
    .input_phase_tvalid(input_phase_tvalid),
    .input_phase_tready(input_phase_tready),
    .input_phase_step_tdata(input_phase_step_tdata),
    .input_phase_step_tvalid(input_phase_step_tvalid),
    .input_phase_step_tready(input_phase_step_tready),
    .output_phase_tdata(output_phase_tdata),
    .output_phase_tvalid(output_phase_tvalid),
    .output_phase_tready(output_phase_tready)
);

endmodule
