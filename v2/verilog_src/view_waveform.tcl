# GTKWave startup script for tb_conv_pe.vcd
set sigs [list \
    tb_conv_pe.clk \
    tb_conv_pe.reset \
    tb_conv_pe.load_weight \
    tb_conv_pe.mac_en \
    tb_conv_pe.clr_acc \
    tb_conv_pe.pixel_in[15:0] \
    tb_conv_pe.uut.tap_idx[3:0] \
    tb_conv_pe.uut.current_weight[15:0] \
    tb_conv_pe.out_acc[15:0] \
    tb_conv_pe.valid_out \
]

gtkwave::addSignalsFromList $sigs
gtkwave::/Time/Zoom/Zoom_Full
