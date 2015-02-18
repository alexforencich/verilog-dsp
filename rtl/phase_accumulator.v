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
 * Phase accumulator
 */
module phase_accumulator #
(
    parameter WIDTH = 32
)
(
    input  wire             clk,
    input  wire             rst,

    /*
     * AXI stream phase input
     */
    input  wire [WIDTH-1:0] input_phase_tdata,
    input  wire             input_phase_tvalid,
    output wire             input_phase_tready,

    /*
     * AXI stream phase step input
     */
    input  wire [WIDTH-1:0] input_phase_step_tdata,
    input  wire             input_phase_step_tvalid,
    output wire             input_phase_step_tready,

    /*
     * AXI stream phase output
     */
    output wire [WIDTH-1:0] output_phase_tdata,
    output wire             output_phase_tvalid,
    input  wire             output_phase_tready
);

reg [WIDTH-1:0] phase_reg = 0;
reg [WIDTH-1:0] phase_step_reg = 0;

assign input_phase_tready = output_phase_tready;
assign input_phase_step_tready = 1;
assign output_phase_tdata = phase_reg;
assign output_phase_tvalid = 1;

always @(posedge clk) begin
    if (rst) begin
        phase_reg <= 0;
        phase_step_reg <= 0;
    end else begin
        if (input_phase_tready & input_phase_tvalid) begin
            phase_reg <= input_phase_tdata;
        end else if (output_phase_tready) begin
            phase_reg <= phase_reg + phase_step_reg;
        end

        if (input_phase_step_tvalid) begin
            phase_step_reg <= input_phase_step_tdata;
        end
    end
end

endmodule
