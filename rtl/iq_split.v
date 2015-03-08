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
 * IQ splitter
 */
module iq_split #
(
    parameter WIDTH = 16
)
(
    input  wire              clk,
    input  wire              rst,

    /*
     * AXI stream input
     */
    input  wire [WIDTH-1:0]  input_i_tdata,
    input  wire [WIDTH-1:0]  input_q_tdata,
    input  wire              input_tvalid,
    output wire              input_tready,

    /*
     * AXI stream outputs
     */
    output wire [WIDTH-1:0]  output_i_tdata,
    output wire              output_i_tvalid,
    input  wire              output_i_tready,

    output wire [WIDTH-1:0]  output_q_tdata,
    output wire              output_q_tvalid,
    input  wire              output_q_tready
);

reg [WIDTH-1:0] i_data_reg = 0;
reg [WIDTH-1:0] q_data_reg = 0;

reg i_valid_reg = 0;
reg q_valid_reg = 0;

assign input_tready = (~i_valid_reg | (output_i_tready & output_i_tvalid)) & (~q_valid_reg | (output_q_tready & output_q_tvalid));

assign output_i_tdata = i_data_reg;
assign output_i_tvalid = i_valid_reg;

assign output_q_tdata = q_data_reg;
assign output_q_tvalid = q_valid_reg;

always @(posedge clk) begin
    if (rst) begin
        i_data_reg <= 0;
        q_data_reg <= 0;
        i_valid_reg <= 0;
        q_valid_reg <= 0;
    end else begin
        if (input_tready & input_tvalid) begin
            i_data_reg <= input_i_tdata;
            q_data_reg <= input_q_tdata;
            i_valid_reg <= 1;
            q_valid_reg <= 1;
        end else begin
            if (output_i_tready) begin
                i_valid_reg <= 0;
            end
            if (output_q_tready) begin
                q_valid_reg <= 0;
            end
        end
    end
end

endmodule
