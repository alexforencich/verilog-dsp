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
 * I2S RX
 */
module i2s_rx #
(
    parameter WIDTH = 16
)
(
    input  wire              clk,
    input  wire              rst,

    /*
     * I2S interface
     */
    input  wire              sck,
    input  wire              ws,
    input  wire              sd,

    /*
     * AXI stream output
     */
    output wire [WIDTH-1:0]  output_l_tdata,
    output wire [WIDTH-1:0]  output_r_tdata,
    output wire              output_tvalid,
    input  wire              output_tready
);

reg [WIDTH-1:0] l_data_reg = 0;
reg [WIDTH-1:0] r_data_reg = 0;

reg l_data_valid_reg = 0;
reg r_data_valid_reg = 0;

reg [WIDTH-1:0] sreg = 0;

reg [$clog2(WIDTH)-1:0] bit_cnt = 0;

reg last_sck = 0;
reg last_ws = 0;
reg last_ws2 = 0;

assign output_l_tdata = l_data_reg;
assign output_r_tdata = r_data_reg;
assign output_tvalid = l_data_valid_reg & r_data_valid_reg;

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
        last_ws2 <= 0;
    end else begin
        if (output_tready & output_tvalid) begin
            l_data_valid_reg <= 0;
            r_data_valid_reg <= 0;
        end

        last_sck <= sck;

        if (~last_sck & sck) begin
            // rising edge sck
            last_ws <= ws;
            last_ws2 <= last_ws;

            if (last_ws2 != last_ws) begin
                bit_cnt <= WIDTH-1;
                sreg <= {{WIDTH-1{1'b0}}, sd};
            end else begin
                if (bit_cnt > 0) begin
                    bit_cnt <= bit_cnt - 1;
                    if (bit_cnt > 1) begin
                        sreg <= {sreg[WIDTH-2:0], sd};
                    end else if (last_ws2) begin
                        r_data_reg <= {sreg[WIDTH-2:0], sd};
                        r_data_valid_reg <= l_data_valid_reg;
                    end else begin
                        l_data_reg <= {sreg[WIDTH-2:0], sd};
                        l_data_valid_reg <= 1;
                    end
                end
            end
        end
    end
end

endmodule
