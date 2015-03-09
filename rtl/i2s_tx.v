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
 * I2S TX
 */
module i2s_tx #
(
    parameter WIDTH = 16
)
(
    input  wire              clk,
    input  wire              rst,

    /*
     * AXI stream input
     */
    input  wire [WIDTH-1:0]  input_l_tdata,
    input  wire [WIDTH-1:0]  input_r_tdata,
    input  wire              input_tvalid,
    output wire              input_tready,

    /*
     * I2S interface
     */
    input  wire              sck,
    input  wire              ws,
    output wire              sd
);

reg [WIDTH-1:0] l_data_reg = 0;
reg [WIDTH-1:0] r_data_reg = 0;

reg l_data_valid_reg = 0;
reg r_data_valid_reg = 0;

reg [WIDTH-1:0] sreg = 0;

reg [$clog2(WIDTH+1)-1:0] bit_cnt = 0;

reg last_sck = 0;
reg last_ws = 0;
reg sd_reg = 0;

assign input_tready = ~l_data_valid_reg & ~r_data_valid_reg;

assign sd = sd_reg;

always @(posedge clk) begin
    if (rst) begin
        l_data_reg <= 0;
        r_data_reg <= 0;
        l_data_valid_reg <= 0;
        r_data_valid_reg <= 0;
        sreg <= 0;
        bit_cnt <= 0;
        last_sck <= 0;
        last_ws <= 0;
        sd_reg <= 0;
    end else begin
        if (input_tready & input_tvalid) begin
            l_data_reg <= input_l_tdata;
            r_data_reg <= input_r_tdata;
            l_data_valid_reg <= 1;
            r_data_valid_reg <= 1;
        end

        last_sck <= sck;

        if (~last_sck & sck) begin
            // rising edge sck
            last_ws <= ws;

            if (last_ws != ws) begin
                bit_cnt <= WIDTH;
                if (ws) begin
                    sreg <= r_data_reg;
                    r_data_valid_reg <= 0;
                end else begin
                    sreg <= l_data_reg;
                    l_data_valid_reg <= 0;
                end
            end
        end

        if (last_sck & ~sck) begin
            // falling edge sck
            if (bit_cnt > 0) begin
                bit_cnt <= bit_cnt - 1;
                {sd_reg, sreg} <= {sreg[WIDTH-1:0], 1'b0};
            end
        end
    end
end

endmodule
