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
 * IQ joiner
 */
module iq_join #
(
    parameter WIDTH = 16
)
(
    input  wire              clk,
    input  wire              rst,

    /*
     * AXI stream inputs
     */
    input  wire [WIDTH-1:0]  input_i_tdata,
    input  wire              input_i_tvalid,
    output wire              input_i_tready,

    input  wire [WIDTH-1:0]  input_q_tdata,
    input  wire              input_q_tvalid,
    output wire              input_q_tready,

    /*
     * AXI stream output
     */
    output wire [WIDTH-1:0]  output_i_tdata,
    output wire [WIDTH-1:0]  output_q_tdata,
    output wire              output_tvalid,
    input  wire              output_tready
);

reg [WIDTH-1:0] i_data_reg = 0;
reg [WIDTH-1:0] q_data_reg = 0;

reg i_valid_reg = 0;
reg q_valid_reg = 0;

assign input_i_tready = ~i_valid_reg | (output_tready & output_tvalid);
assign input_q_tready = ~q_valid_reg | (output_tready & output_tvalid);

assign output_i_tdata = i_data_reg;
assign output_q_tdata = q_data_reg;
assign output_tvalid = i_valid_reg & q_valid_reg;

always @(posedge clk) begin
    if (rst) begin
        i_data_reg <= 0;
        q_data_reg <= 0;
        i_valid_reg <= 0;
        q_valid_reg <= 0;
    end else begin
        if (input_i_tready & input_i_tvalid) begin
            i_data_reg <= input_i_tdata;
            i_valid_reg <= 1;
        end else if (output_tready & output_tvalid) begin
            i_valid_reg <= 0;
        end
        if (input_q_tready & input_q_tvalid) begin
            q_data_reg <= input_q_tdata;
            q_valid_reg <= 1;
        end else if (output_tready & output_tvalid) begin
            q_valid_reg <= 0;
        end
    end
end

endmodule
