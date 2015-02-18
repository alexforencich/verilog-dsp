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
 * Sine DDS
 */
module sine_dds #
(
    parameter PHASE_WIDTH = 32,
    parameter OUTPUT_WIDTH = 16
)
(
    input  wire                    clk,
    input  wire                    rst,

    input  wire [PHASE_WIDTH-1:0]  input_phase_tdata,
    input  wire                    input_phase_tvalid,
    output wire                    input_phase_tready,

    input  wire [PHASE_WIDTH-1:0]  input_phase_step_tdata,
    input  wire                    input_phase_step_tvalid,
    output wire                    input_phase_step_tready,

    output wire [OUTPUT_WIDTH-1:0] output_sample_i_tdata,
    output wire [OUTPUT_WIDTH-1:0] output_sample_q_tdata,
    output wire                    output_sample_tvalid,
    input  wire                    output_sample_tready
);

wire [PHASE_WIDTH-1:0] phase_tdata;
wire phase_tvalid;
wire phase_tready;

phase_accumulator #(
    .WIDTH(PHASE_WIDTH)
)
phase_accumulator_inst (
    .clk(clk),
    .rst(rst),
    
    .input_phase_tdata(input_phase_tdata),
    .input_phase_tvalid(input_phase_tvalid),
    .input_phase_tready(input_phase_tready),

    .input_phase_step_tdata(input_phase_step_tdata),
    .input_phase_step_tvalid(input_phase_step_tvalid),
    .input_phase_step_tready(input_phase_step_tready),

    .output_phase_tdata(phase_tdata),
    .output_phase_tvalid(phase_tvalid),
    .output_phase_tready(phase_tready)
);

sine_dds_lut #(
    .INPUT_WIDTH(OUTPUT_WIDTH+2),
    .OUTPUT_WIDTH(OUTPUT_WIDTH)
)
sine_dds_inst (
    .clk(clk),
    .rst(rst),

    .input_phase_tdata(phase_tdata[PHASE_WIDTH-1:PHASE_WIDTH-OUTPUT_WIDTH-2]),
    .input_phase_tvalid(phase_tvalid),
    .input_phase_tready(phase_tready),

    .output_sample_i_tdata(output_sample_i_tdata),
    .output_sample_q_tdata(output_sample_q_tdata),
    .output_sample_tvalid(output_sample_tvalid),
    .output_sample_tready(output_sample_tready)
);

endmodule
