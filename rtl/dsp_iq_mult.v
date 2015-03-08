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
 * IQ Multiplier - computes a*b
 */
module dsp_iq_mult #
(
    parameter WIDTH = 16
)
(
    input  wire                  clk,
    input  wire                  rst,

    /*
     * AXI stream inputs
     */
    input  wire [WIDTH-1:0]      input_a_i_tdata,
    input  wire [WIDTH-1:0]      input_a_q_tdata,
    input  wire                  input_a_tvalid,
    output wire                  input_a_tready,

    input  wire [WIDTH-1:0]      input_b_i_tdata,
    input  wire [WIDTH-1:0]      input_b_q_tdata,
    input  wire                  input_b_tvalid,
    output wire                  input_b_tready,

    /*
     * AXI stream output
     */
    output wire [(WIDTH*2)-1:0]  output_i_tdata,
    output wire [(WIDTH*2)-1:0]  output_q_tdata,
    output wire                  output_tvalid,
    input  wire                  output_tready
);

reg [WIDTH-1:0] input_a_i_reg_0 = 0;
reg [WIDTH-1:0] input_a_q_reg_0 = 0;
reg [WIDTH-1:0] input_a_i_reg_1 = 0;
reg [WIDTH-1:0] input_a_q_reg_1 = 0;

reg [WIDTH-1:0] input_b_i_reg_0 = 0;
reg [WIDTH-1:0] input_b_q_reg_0 = 0;
reg [WIDTH-1:0] input_b_i_reg_1 = 0;
reg [WIDTH-1:0] input_b_q_reg_1 = 0;

reg [(WIDTH*2)-1:0] output_i_reg_0 = 0;
reg [(WIDTH*2)-1:0] output_q_reg_0 = 0;
reg [(WIDTH*2)-1:0] output_i_reg_1 = 0;
reg [(WIDTH*2)-1:0] output_q_reg_1 = 0;

wire transfer = input_a_tvalid & input_b_tvalid & output_tready;

assign input_a_tready = input_b_tvalid & output_tready;
assign input_b_tready = input_a_tvalid & output_tready;

assign output_i_tdata = output_i_reg_1;
assign output_q_tdata = output_q_reg_1;
assign output_tvalid = input_a_tvalid & input_b_tvalid;

always @(posedge clk) begin
    if (rst) begin
        input_a_i_reg_0 <= 0;
        input_a_q_reg_0 <= 0;
        input_a_i_reg_1 <= 0;
        input_a_q_reg_1 <= 0;

        input_b_i_reg_0 <= 0;
        input_b_q_reg_0 <= 0;
        input_b_i_reg_1 <= 0;
        input_b_q_reg_1 <= 0;

        output_i_reg_0 <= 0;
        output_q_reg_0 <= 0;
        output_i_reg_1 <= 0;
        output_q_reg_1 <= 0;
    end else begin
        if (transfer) begin
            // pipeline for Xilinx DSP slice

            // register
            input_a_i_reg_0 <= input_a_i_tdata;
            input_a_q_reg_0 <= input_a_q_tdata;
            input_b_i_reg_0 <= input_b_i_tdata;
            input_b_q_reg_0 <= input_b_q_tdata;

            // pipeline
            input_a_i_reg_1 <= input_a_i_reg_0;
            input_a_q_reg_1 <= input_a_q_reg_0;
            input_b_i_reg_1 <= input_b_i_reg_0;
            input_b_q_reg_1 <= input_b_q_reg_0;

            // multiply
            output_i_reg_0 <= $signed(input_a_i_reg_1) * $signed(input_b_i_reg_1);
            output_q_reg_0 <= $signed(input_a_q_reg_1) * $signed(input_b_q_reg_1);

            // pipeline
            output_i_reg_1 <= output_i_reg_0;
            output_q_reg_1 <= output_q_reg_0;
        end
    end
end

endmodule
