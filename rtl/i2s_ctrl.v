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
 * I2S control
 */
module i2s_ctrl #
(
    parameter WIDTH = 16
)
(
    input  wire              clk,
    input  wire              rst,

    /*
     * I2S interface
     */
    output wire              sck,
    output wire              ws,

    /*
     * Configuration
     */
    input  wire [15:0]       prescale
);

reg [15:0] prescale_cnt = 0;
reg [$clog2(WIDTH)-1:0] ws_cnt = 0;

reg sck_reg = 0;
reg ws_reg = 0;

assign sck = sck_reg;
assign ws = ws_reg;

always @(posedge clk) begin
    if (rst) begin
        prescale_cnt <= 0;
        ws_cnt <= 0;
        sck_reg <= 0;
        ws_reg <= 0;
    end else begin
        if (prescale_cnt > 0) begin
            prescale_cnt <= prescale_cnt - 1;
        end else begin
            prescale_cnt <= prescale;
            if (sck_reg) begin
                sck_reg <= 0;
                if (ws_cnt > 0) begin
                    ws_cnt <= ws_cnt - 1;
                end else begin
                    ws_cnt <= WIDTH-1;
                    ws_reg <= ~ws_reg;
                end
            end else begin
                sck_reg <= 1;
            end
        end
    end
end

endmodule
