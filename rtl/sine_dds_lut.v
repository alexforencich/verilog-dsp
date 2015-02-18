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
 * Sine DDS look up table
 */
module sine_dds_lut #
(
    parameter OUTPUT_WIDTH = 16,
    parameter INPUT_WIDTH = OUTPUT_WIDTH+2
)
(
    input  wire                    clk,
    input  wire                    rst,

    /*
     * AXI stream phase input
     */
    input  wire [INPUT_WIDTH-1:0]  input_phase_tdata,
    input  wire                    input_phase_tvalid,
    output wire                    input_phase_tready,

    /*
     * AXI stream sample output
     */
    output wire [OUTPUT_WIDTH-1:0] output_sample_i_tdata,
    output wire [OUTPUT_WIDTH-1:0] output_sample_q_tdata,
    output wire                    output_sample_tvalid,
    input  wire                    output_sample_tready
);

localparam W = (INPUT_WIDTH-2)/2;

reg [INPUT_WIDTH-1:0] phase_reg = 0;

integer i;

// coarse sine and cosine LUTs
reg [OUTPUT_WIDTH-1:0] coarse_c_lut[2**(W+1)-1:0];
reg [OUTPUT_WIDTH-1:0] coarse_s_lut[2**(W+1)-1:0];

initial begin
    for (i = 0; i < 2**(W+1); i = i + 1) begin
        coarse_c_lut[i] = $cos(2*3.1415926535*i/2**(W+2))*(2**(OUTPUT_WIDTH-1)-1);
        coarse_s_lut[i] = $sin(2*3.1415926535*i/2**(W+2))*(2**(OUTPUT_WIDTH-1)-1);
    end
end

// fine sine LUT
reg [(OUTPUT_WIDTH/2)-1:0] fine_s_lut[2**W-1:0];

initial begin
    for (i = 0; i < 2**W; i = i + 1) begin
        fine_s_lut[i] = $sin(2*3.1415926535*(i-2**(W-1))/2**INPUT_WIDTH)*(2**(OUTPUT_WIDTH-1)-1);
    end
end

reg [OUTPUT_WIDTH-1:0] sample_i_reg = 0;
reg [OUTPUT_WIDTH-1:0] sample_q_reg = 0;

wire SIGN = phase_reg[INPUT_WIDTH-1];
wire SLOPE = phase_reg[INPUT_WIDTH-2];
wire [W:0] A = phase_reg[INPUT_WIDTH-2:W];
wire [W-1:0] B = phase_reg[W-1:0];

reg sign_reg_1 = 0;
reg sign_reg_2 = 0;
reg sign_reg_3 = 0;
reg sign_reg_4 = 0;

reg [OUTPUT_WIDTH-1:0] ccs_reg_1 = 0, ccs_reg_2 = 0, ccs_reg_3 = 0;
reg [OUTPUT_WIDTH-1:0] css_reg_1 = 0, css_reg_2 = 0, css_reg_3 = 0;
reg [(OUTPUT_WIDTH/2)-1:0] fss_reg_1 = 0, fss_reg_2 = 0;

reg [(OUTPUT_WIDTH*2)-1:0] cp_reg_1 = 0;
reg [(OUTPUT_WIDTH*2)-1:0] sp_reg_1 = 0;

reg [OUTPUT_WIDTH-1:0] cs_reg_1 = 0;
reg [OUTPUT_WIDTH-1:0] ss_reg_1 = 0;

assign input_phase_tready = output_sample_tready;
assign output_sample_i_tdata = sample_i_reg;
assign output_sample_q_tdata = sample_q_reg;
assign output_sample_tvalid = input_phase_tvalid;

always @(posedge clk) begin
    if (rst) begin
        phase_reg <= 0;
    end else begin
        if (input_phase_tready & input_phase_tvalid) begin
            phase_reg <= input_phase_tdata;
        end
    end

    if (input_phase_tready & input_phase_tvalid) begin
        // pipeline sits primarily in DSP slice
        // sin(A+B) = sin(A) + cos(A)*sin(B)
        // cos(A+B) = cos(A) - sin(A)*sin(B)
        
        // read samples
        sign_reg_1 <= SIGN;
        ccs_reg_1 <= coarse_c_lut[A];
        css_reg_1 <= coarse_s_lut[A];
        fss_reg_1 <= fine_s_lut[B];

        // pipeline
        sign_reg_2 <= sign_reg_1;
        ccs_reg_2 <= ccs_reg_1;
        css_reg_2 <= css_reg_1;
        fss_reg_2 <= fss_reg_1;

        // multiply
        sign_reg_3 <= sign_reg_2;
        ccs_reg_3 <= ccs_reg_2;
        css_reg_3 <= css_reg_2;
        cp_reg_1 <= $signed(css_reg_2) * $signed(fss_reg_2);
        sp_reg_1 <= $signed(ccs_reg_2) * $signed(fss_reg_2);

        // add
        sign_reg_4 <= sign_reg_3;
        cs_reg_1 <= ccs_reg_3 - (cp_reg_1 >> (OUTPUT_WIDTH-1));
        ss_reg_1 <= css_reg_3 + (sp_reg_1 >> (OUTPUT_WIDTH-1));

        // negate output samples
        sample_i_reg <= sign_reg_4 ? -cs_reg_1 : cs_reg_1;
        sample_q_reg <= sign_reg_4 ? -ss_reg_1 : ss_reg_1;
    end
end

endmodule
