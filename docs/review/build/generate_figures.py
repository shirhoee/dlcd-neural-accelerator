#!/usr/bin/env python3
"""Generates all architectural, datapath, and FSM figures for the DLCD project report.
Uses matplotlib.patches to render 300 DPI publication-quality diagrams with zero external dependencies.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

def draw_v2_top_block_diagram():
    fig, ax = plt.subplots(figsize=(12.0, 6.2), dpi=300)
    ax.set_xlim(0, 125)
    ax.set_ylim(0, 62)
    ax.axis("off")

    # Title
    ax.text(62.5, 59, "Figure 2.1: V2 CNN Neural Accelerator Top-Level Architecture (v2_top)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#0F172A")
    ax.text(62.5, 56.5, "Fully Pipelined Streaming Datapath with Time-Multiplexed 16x16 Systolic Matrix Engine",
            ha="center", va="center", fontsize=9.5, color="#475569")

    # Colors
    c_rom = "#E0F2FE"     # Light sky blue
    c_conv = "#EFF6FF"    # Light blue
    c_pool = "#F0FDF4"    # Light emerald
    c_mlp = "#FEF3C7"     # Light amber
    c_am = "#F3E8FF"      # Light purple
    c_border = "#334155"  # Slate dark

    # Global Control Inputs (Left box)
    box_ctrl = patches.FancyBboxPatch((2, 38), 11, 14, boxstyle="round,pad=0.5", fc="#F8FAFC", ec=c_border, lw=1.5)
    ax.add_patch(box_ctrl)
    ax.text(7.5, 49, "Control / Clock", ha="center", va="center", fontsize=9, fontweight="bold", color="#0F172A")
    ax.text(7.5, 45, "clk (100 MHz)", ha="center", va="center", fontsize=8, color="#334155")
    ax.text(7.5, 42, "reset (act-high)", ha="center", va="center", fontsize=8, color="#DC2626")
    ax.text(7.5, 39.5, "start (pulse)", ha="center", va="center", fontsize=8, color="#2563EB")

    # External Image ROM
    box_irom = patches.FancyBboxPatch((2, 16), 11, 16, boxstyle="round,pad=0.5", fc=c_rom, ec="#0284C7", lw=1.5)
    ax.add_patch(box_irom)
    ax.text(7.5, 28, "External\nImage ROM", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0369A1")
    ax.text(7.5, 23, "400 x 16-bit\n(20x20 Image)", ha="center", va="center", fontsize=8, color="#0F172A")
    ax.text(7.5, 18.5, "Q7.8 Pixels", ha="center", va="center", fontsize=8, color="#475569")

    # Stage 1: Conv1 Array
    box_c1 = patches.FancyBboxPatch((18, 14), 13, 30, boxstyle="round,pad=0.5", fc=c_conv, ec="#2563EB", lw=1.5)
    ax.add_patch(box_c1)
    ax.text(24.5, 41, "conv1_array", ha="center", va="center", fontsize=10, fontweight="bold", color="#1D4ED8")
    ax.text(24.5, 37.5, "[4 Channels]", ha="center", va="center", fontsize=8.5, color="#1E40AF")
    ax.text(24.5, 33, "- window_gen (47-sr)\n- 4x conv_pe (4 MACs)\n- 6-state FSM controller", ha="center", va="center", fontsize=7.2, color="#334155")
    ax.text(24.5, 23, "ROM Source:\nconv1_rom (36x16)\n[4 kernels x 3x3]", ha="center", va="center", fontsize=7.2, style="italic", color="#0284C7")
    ax.text(24.5, 16, "Latency: 4,892 cyc", ha="center", va="center", fontsize=8, fontweight="bold", color="#B45309")

    # Stage 2: MaxPool1 Array
    box_mp1 = patches.FancyBboxPatch((41, 14), 13, 30, boxstyle="round,pad=0.5", fc=c_pool, ec="#16A34A", lw=1.5)
    ax.add_patch(box_mp1)
    ax.text(47.5, 41, "maxpool_array", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#15803D")
    ax.text(47.5, 37.5, "[4 Channels]", ha="center", va="center", fontsize=8.5, color="#166534")
    ax.text(47.5, 33, "- 4x pool_window_gen\n- 4x maxpool_pe (2x2)\n- 4x relu_q7_8 (fused)", ha="center", va="center", fontsize=7.2, color="#334155")
    ax.text(47.5, 23, "Spatial Reduction:\n20x20 -> 10x10\nStreaming Stride-2", ha="center", va="center", fontsize=7.2, style="italic", color="#15803D")
    ax.text(47.5, 16, "Outputs: 4x100 = 400", ha="center", va="center", fontsize=8, color="#334155")

    # Stage 3: Conv2 Array
    box_c2 = patches.FancyBboxPatch((64, 14), 13, 30, boxstyle="round,pad=0.5", fc=c_conv, ec="#2563EB", lw=1.5)
    ax.add_patch(box_c2)
    ax.text(70.5, 41, "conv2_array", ha="center", va="center", fontsize=10, fontweight="bold", color="#1D4ED8")
    ax.text(70.5, 37.5, "[8 Channels]", ha="center", va="center", fontsize=8.5, color="#1E40AF")
    ax.text(70.5, 33, "- 4x 100-word buffers\n- 4x conv2_window_gen\n- 8x conv2_pe (32 MACs)\n- 6-state FSM", ha="center", va="center", fontsize=7.2, color="#334155")
    ax.text(70.5, 22, "ROM Source:\nconv2_rom (288x16)\n[8x4 kernels x 3x3]", ha="center", va="center", fontsize=7.2, style="italic", color="#0284C7")
    ax.text(70.5, 16, "Latency: 1,244 cyc", ha="center", va="center", fontsize=8, fontweight="bold", color="#B45309")

    # Stage 4: MaxPool2 Array
    box_mp2 = patches.FancyBboxPatch((87, 14), 13, 30, boxstyle="round,pad=0.5", fc=c_pool, ec="#16A34A", lw=1.5)
    ax.add_patch(box_mp2)
    ax.text(93.5, 41, "maxpool2_array", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#15803D")
    ax.text(93.5, 37.5, "[8 Channels]", ha="center", va="center", fontsize=8.5, color="#166534")
    ax.text(93.5, 33, "- 8x pool2_window_gen\n- 8x maxpool_pe (2x2)\n- 8x relu_q7_8 (fused)", ha="center", va="center", fontsize=7.2, color="#334155")
    ax.text(93.5, 23, "Spatial Reduction:\n10x10 -> 5x5\nStreaming Stride-2", ha="center", va="center", fontsize=7.2, style="italic", color="#15803D")
    ax.text(93.5, 16, "Features: 8x25 = 200", ha="center", va="center", fontsize=8, color="#334155")

    # Stage 5: MLP Head
    box_mlp = patches.FancyBboxPatch((109, 14), 14.5, 30, boxstyle="round,pad=0.5", fc=c_mlp, ec="#D97706", lw=1.5)
    ax.add_patch(box_mlp)
    ax.text(116.25, 41, "mlp_head (Dense)", ha="center", va="center", fontsize=10, fontweight="bold", color="#B45309")
    ax.text(116.25, 37.5, "200 -> 64 -> 32 -> 10", ha="center", va="center", fontsize=8.5, color="#92400E")
    ax.text(116.25, 33, "- 16x16 systolic_array\n  (256 weight-stat PEs)\n- ram_A [208x16]\n- ram_B [64x16]\n- 4-state nested FSM", ha="center", va="center", fontsize=7.2, color="#334155")
    ax.text(116.25, 22, "ROM Source:\nweight_rom (992x256)\n[62 tiles x 16 words]", ha="center", va="center", fontsize=7.2, style="italic", color="#B45309")
    ax.text(116.25, 16, "Latency: 2,977 cyc", ha="center", va="center", fontsize=8, fontweight="bold", color="#B45309")

    # Output: Argmax (Bottom right)
    box_am = patches.FancyBboxPatch((108.5, 2), 15, 9, boxstyle="round,pad=0.5", fc=c_am, ec="#9333EA", lw=1.5)
    ax.add_patch(box_am)
    ax.text(116, 8.5, "argmax", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#7E22CE")
    ax.text(116, 5.5, "10-Input Comparator Tree\nprediction[3:0], done (1 cyc)", ha="center", va="center", fontsize=7.2, color="#334155")

    # Arrows between blocks
    kw_arr = dict(arrowstyle="->", lw=1.5, color="#0F172A")
    # Image ROM <-> Conv1
    ax.annotate("", xy=(18, 25), xytext=(13, 25), arrowprops=kw_arr)
    ax.text(15.5, 26.5, "pixel_in", fontsize=7, ha="center")
    ax.annotate("", xy=(13, 21), xytext=(18, 21), arrowprops=kw_arr)
    ax.text(15.5, 19, "pixel_addr", fontsize=7, ha="center")

    # Conv1 -> MaxPool1
    ax.annotate("", xy=(41, 28), xytext=(31, 28), arrowprops=kw_arr)
    ax.text(36, 29.8, "c1_valid\n4 ch", fontsize=7, ha="center", va="bottom")

    # MaxPool1 -> Conv2
    ax.annotate("", xy=(64, 28), xytext=(54, 28), arrowprops=kw_arr)
    ax.text(59, 29.8, "mp1_valid\n4 ch", fontsize=7, ha="center", va="bottom")

    # Conv2 -> MaxPool2
    ax.annotate("", xy=(87, 28), xytext=(77, 28), arrowprops=kw_arr)
    ax.text(82, 29.8, "c2_valid\n8 ch", fontsize=7, ha="center", va="bottom")

    # MaxPool2 -> MLP Head
    ax.annotate("", xy=(109, 28), xytext=(100, 28), arrowprops=kw_arr)
    ax.text(104.5, 29.8, "mp2_valid\n8 ch", fontsize=7, ha="center", va="bottom")

    # MLP Head -> Argmax
    ax.annotate("", xy=(116, 11), xytext=(116, 14), arrowprops=kw_arr)
    ax.text(118, 12.5, "d_valid (10 logits)", fontsize=7, ha="left", va="center")

    # Final Output arrow
    ax.annotate("", xy=(99, 6.5), xytext=(108.5, 6.5), arrowprops=dict(arrowstyle="<-", lw=1.8, color="#15803D"))
    ax.text(94, 7.5, "prediction[3:0]\ndone", fontsize=8, fontweight="bold", ha="center", color="#15803D")

    # Footer metrics bar
    ax.text(62.5, 1, "Total Latency: 9,116 cycles (91.16 us @ 100 MHz) | Multipliers: 292 (4 + 32 + 256) | Accuracy: 98.83% Float32 / 98.70% Q7.8 Hardware",
            ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0F172A")

    plt.tight_layout()
    p = FIG_DIR / "fig2_1_v2_top_block_diagram.png"
    plt.savefig(p, dpi=300)
    plt.close(fig)
    print(f"Generated {p}")

def draw_mac_conv_pe_datapath():
    fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=300)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 55)
    ax.axis("off")

    ax.text(52.5, 52, "Figure 2.2: Detailed RTL Datapath of conv_pe and mac_q7_8 Execution Unit",
            ha="center", va="center", fontsize=11.5, fontweight="bold", color="#0F172A")
    ax.text(52.5, 49.5, "Bit-Exact Sequential 9-Tap Multiply-Accumulate with product[23:8] Truncation",
            ha="center", va="center", fontsize=9, color="#475569")

    # Left: conv_pe boundary
    b_pe = patches.FancyBboxPatch((2, 4), 98, 43, boxstyle="round,pad=0.8", fc="#F8FAFC", ec="#64748B", lw=1.5, ls="--")
    ax.add_patch(b_pe)
    ax.text(6, 44.5, "conv_pe.v Module Boundary", fontsize=9, fontweight="bold", color="#475569")

    # Weight Shift Register
    b_sr = patches.FancyBboxPatch((5, 22), 18, 18, boxstyle="round,pad=0.5", fc="#E0F2FE", ec="#0284C7", lw=1.5)
    ax.add_patch(b_sr)
    ax.text(14, 36.5, "weights[0:8] Shift Reg", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0369A1")
    ax.text(14, 32.5, "9 x 16-bit Q7.8 Weights\n(Weight-Stationary)", ha="center", va="center", fontsize=7.5, color="#0F172A")
    ax.text(14, 27, "Enabled by load_weight\nweight_in[15:0] serial shift", ha="center", va="center", fontsize=7, color="#475569")

    # Tap counter
    b_tap = patches.FancyBboxPatch((5, 7), 18, 12, boxstyle="round,pad=0.5", fc="#FEF3C7", ec="#D97706", lw=1.5)
    ax.add_patch(b_tap)
    ax.text(14, 15, "tap_idx Counter [3:0]", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#B45309")
    ax.text(14, 11, "Counts 0 to 8 on mac_en\nAsserts valid_out when tap_idx==8", ha="center", va="center", fontsize=7, color="#78350F")

    # Mux
    b_mux = patches.Polygon([[29, 22], [33, 25], [33, 37], [29, 40]], closed=True, fc="#F1F5F9", ec="#334155", lw=1.5)
    ax.add_patch(b_mux)
    ax.text(31, 31, "MUX\n9:1", ha="center", va="center", fontsize=7.5, fontweight="bold")

    # mac_q7_8 boundary
    b_mac = patches.FancyBboxPatch((40, 10), 38, 32, boxstyle="round,pad=0.6", fc="#EFF6FF", ec="#2563EB", lw=1.5)
    ax.add_patch(b_mac)
    ax.text(59, 39, "mac_q7_8.v (Purely Combinational)", ha="center", va="center", fontsize=9, fontweight="bold", color="#1D4ED8")

    # Multiplier
    b_mult = patches.FancyBboxPatch((43, 24), 14, 12, boxstyle="round,pad=0.4", fc="#DBEAFE", ec="#1D4ED8", lw=1.2)
    ax.add_patch(b_mult)
    ax.text(50, 31, "16x16 Signed\nMultiplier (*)", ha="center", va="center", fontsize=8, fontweight="bold", color="#1E40AF")
    ax.text(50, 26.5, "product[31:0]", ha="center", va="center", fontsize=7.5, color="#1D4ED8")

    # Slicer
    b_slice = patches.FancyBboxPatch((60, 26), 7, 8, boxstyle="round,pad=0.3", fc="#FEF08A", ec="#CA8A04", lw=1.2)
    ax.add_patch(b_slice)
    ax.text(63.5, 30, "product\n[23:8]", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#854D0E")

    # Adder
    b_add = patches.FancyBboxPatch((70, 16), 6, 14, boxstyle="round,pad=0.3", fc="#DCFCE7", ec="#16A34A", lw=1.2)
    ax.add_patch(b_add)
    ax.text(73, 23, "16-bit\nAdder\n(+)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#15803D")

    # Accumulator MUX (clr_acc ? 0 : out_acc)
    b_accmux = patches.Polygon([[43, 13], [47, 15], [47, 21], [43, 23]], closed=True, fc="#F1F5F9", ec="#334155", lw=1.2)
    ax.add_patch(b_accmux)
    ax.text(45, 18, "CLR\nMUX", ha="center", va="center", fontsize=6.5, fontweight="bold")

    # Accumulator Register (out_acc)
    b_reg = patches.FancyBboxPatch((83, 18), 14, 14, boxstyle="round,pad=0.5", fc="#FCE7F3", ec="#DB2777", lw=1.5)
    ax.add_patch(b_reg)
    ax.text(90, 27, "out_acc [15:0]", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#BE185D")
    ax.text(90, 23, "Q7.8 Accumulator DFF", ha="center", va="center", fontsize=7.5, color="#0F172A")
    ax.text(90, 20, "Enabled by mac_en", ha="center", va="center", fontsize=7, color="#475569")

    # Arrows
    kw = dict(arrowstyle="->", lw=1.2, color="#0F172A")
    # Shift reg to Mux
    ax.annotate("", xy=(29, 31), xytext=(23, 31), arrowprops=kw)
    ax.text(26, 32.5, "weights[8:0]", fontsize=6.5, ha="center")
    # Tap idx to Mux
    ax.annotate("", xy=(31, 22), xytext=(23, 13), arrowprops=kw)
    ax.text(28, 16, "tap_idx[3:0]", fontsize=6.5, ha="center")

    # Mux to Multiplier
    ax.annotate("", xy=(43, 32), xytext=(33, 32), arrowprops=kw)
    ax.text(38, 33.5, "current_weight", fontsize=6.5, ha="center")

    # Pixel in to Multiplier
    ax.annotate("", xy=(43, 26), xytext=(35, 26), arrowprops=kw)
    ax.text(38, 24.5, "pixel_in[15:0]", fontsize=6.5, ha="center")

    # Multiplier to Slicer
    ax.annotate("", xy=(60, 30), xytext=(57, 30), arrowprops=kw)

    # Slicer to Adder
    ax.annotate("", xy=(70, 26), xytext=(67, 26), arrowprops=kw)
    ax.text(68.5, 28, "scaled", fontsize=6.5, ha="center")

    # Acc in to Adder
    ax.annotate("", xy=(70, 18), xytext=(47, 18), arrowprops=kw)
    ax.text(58, 16.5, "acc_in[15:0]", fontsize=6.5, ha="center")

    # Adder to out_acc register
    ax.annotate("", xy=(83, 25), xytext=(76, 25), arrowprops=kw)
    ax.text(79.5, 26.5, "mac_result", fontsize=6.5, ha="center")

    # Feedback from out_acc to acc_in mux
    ax.plot([90, 90, 41, 41, 43], [18, 5, 5, 16, 16], color="#475569", lw=1.2)
    ax.text(65, 3.5, "Accumulator Feedback (out_acc)", fontsize=7, color="#475569", ha="center")

    # Output valid_out
    ax.annotate("", xy=(100, 10), xytext=(23, 10), arrowprops=dict(arrowstyle="->", lw=1.2, color="#15803D"))
    ax.text(93, 11.5, "valid_out (strobe)", fontsize=7.5, fontweight="bold", color="#15803D", ha="center")

    plt.tight_layout()
    p = FIG_DIR / "fig2_2_mac_conv_pe_datapath.png"
    plt.savefig(p, dpi=300)
    plt.close(fig)
    print(f"Generated {p}")

def draw_conv2_and_systolic_pe():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 5.0), dpi=300)
    for ax in (ax1, ax2):
        ax.set_xlim(0, 50)
        ax.set_ylim(0, 50)
        ax.axis("off")

    # Left: conv2_pe
    ax1.text(25, 48, "conv2_pe: 4-Input Dot Product MAC", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#1D4ED8")
    b_c2 = patches.FancyBboxPatch((2, 2), 46, 43, boxstyle="round,pad=0.5", fc="#EFF6FF", ec="#2563EB", lw=1.2)
    ax1.add_patch(b_c2)

    # 4 MAC instances
    y_pos = [37, 28, 19, 10]
    for idx, y in enumerate(y_pos):
        bm = patches.FancyBboxPatch((4, y), 12, 6.5, boxstyle="round,pad=0.3", fc="#DBEAFE", ec="#1D4ED8", lw=1)
        ax1.add_patch(bm)
        ax1.text(10, y+3.2, f"mac{idx}\n(weight*pixel)", ha="center", va="center", fontsize=6.5, fontweight="bold")

    # Adder tree
    b_s01 = patches.FancyBboxPatch((20, 31), 7, 8, boxstyle="round,pad=0.2", fc="#DCFCE7", ec="#16A34A", lw=1)
    ax1.add_patch(b_s01)
    ax1.text(23.5, 35, "sum_01\n(+)", ha="center", va="center", fontsize=6.5, fontweight="bold")

    b_s23 = patches.FancyBboxPatch((20, 13), 7, 8, boxstyle="round,pad=0.2", fc="#DCFCE7", ec="#16A34A", lw=1)
    ax1.add_patch(b_s23)
    ax1.text(23.5, 17, "sum_23\n(+)", ha="center", va="center", fontsize=6.5, fontweight="bold")

    b_tree = patches.FancyBboxPatch((30, 22), 7, 8, boxstyle="round,pad=0.2", fc="#DCFCE7", ec="#16A34A", lw=1)
    ax1.add_patch(b_tree)
    ax1.text(33.5, 26, "tree_sum\n(+)", ha="center", va="center", fontsize=6.5, fontweight="bold")

    b_acc2 = patches.FancyBboxPatch((40, 20), 7, 12, boxstyle="round,pad=0.3", fc="#FCE7F3", ec="#DB2777", lw=1)
    ax1.add_patch(b_acc2)
    ax1.text(43.5, 26, "out_acc\nReg", ha="center", va="center", fontsize=7, fontweight="bold")

    # Connections left
    kw = dict(arrowstyle="->", lw=1, color="#334155")
    ax1.annotate("", xy=(20, 36), xytext=(16, 40), arrowprops=kw)
    ax1.annotate("", xy=(20, 33), xytext=(16, 31), arrowprops=kw)
    ax1.annotate("", xy=(20, 18), xytext=(16, 22), arrowprops=kw)
    ax1.annotate("", xy=(20, 15), xytext=(16, 13), arrowprops=kw)
    ax1.annotate("", xy=(30, 27), xytext=(27, 35), arrowprops=kw)
    ax1.annotate("", xy=(30, 25), xytext=(27, 17), arrowprops=kw)
    ax1.annotate("", xy=(40, 26), xytext=(37, 26), arrowprops=kw)
    ax1.annotate("", xy=(48, 26), xytext=(47, 26), arrowprops=kw)

    # Right: systolic_pe
    ax2.text(25, 48.5, "systolic_pe: Weight-Stationary Matrix PE", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#B45309")
    b_sys = patches.FancyBboxPatch((2, 2), 46, 44, boxstyle="round,pad=0.5", fc="#FEF3C7", ec="#D97706", lw=1.2)
    ax2.add_patch(b_sys)

    # Stationary weight register
    b_sw = patches.FancyBboxPatch((15, 31), 20, 7.5, boxstyle="round,pad=0.3", fc="#FEF08A", ec="#CA8A04", lw=1.2)
    ax2.add_patch(b_sw)
    ax2.text(25, 35.5, "stationary_weight [15:0]", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#854D0E")
    ax2.text(25, 33, "Loaded on load_weight", ha="center", va="center", fontsize=6.5, color="#713F12")

    # core_mac
    b_cmac = patches.FancyBboxPatch((15, 17), 20, 10, boxstyle="round,pad=0.3", fc="#EFF6FF", ec="#2563EB", lw=1.2)
    ax2.add_patch(b_cmac)
    ax2.text(25, 23, "core_mac (mac_q7_8)", ha="center", va="center", fontsize=8, fontweight="bold", color="#1D4ED8")
    ax2.text(25, 19.5, "acc_in + (wt * in_val_in)[23:8]", ha="center", va="center", fontsize=6.5, color="#1E40AF")

    # Output registers
    b_rout = patches.FancyBboxPatch((15, 6), 20, 7.5, boxstyle="round,pad=0.3", fc="#FCE7F3", ec="#DB2777", lw=1.2)
    ax2.add_patch(b_rout)
    ax2.text(25, 10.5, "in_val_out & acc_out DFFs", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#BE185D")
    ax2.text(25, 8, "Synchronous 1-cycle pipeline step", ha="center", va="center", fontsize=6.5, color="#475569")

    # Systolic data flow arrows
    ax2.annotate("", xy=(15, 22), xytext=(5, 22), arrowprops=dict(arrowstyle="->", lw=1.5, color="#2563EB"))
    ax2.text(10, 24, "in_val_in\n(From Left)", fontsize=6.5, ha="center", color="#2563EB")

    ax2.annotate("", xy=(45, 9.75), xytext=(35, 9.75), arrowprops=dict(arrowstyle="->", lw=1.5, color="#2563EB"))
    ax2.text(40, 12, "in_val_out\n(To Right)", fontsize=6.5, ha="center", color="#2563EB")

    # weight from stationary_weight to core_mac
    ax2.annotate("", xy=(21, 27), xytext=(21, 31), arrowprops=kw)
    ax2.text(19, 29, "weight", fontsize=6.5, ha="right", va="center")

    # acc_in routed around stationary_weight (entering on the right)
    ax2.text(38, 43.5, "acc_in (From Top)", fontsize=6.5, ha="center", va="center", color="#15803D")
    ax2.plot([38, 38, 31], [41.5, 29, 29], color="#15803D", lw=1.5)
    ax2.annotate("", xy=(31, 27), xytext=(31, 29), arrowprops=dict(arrowstyle="->", lw=1.5, color="#15803D"))

    # acc_out out the bottom
    ax2.annotate("", xy=(31, 1.5), xytext=(31, 6), arrowprops=dict(arrowstyle="->", lw=1.5, color="#15803D"))
    ax2.text(33, 3.8, "acc_out (To Bottom)", fontsize=6.5, ha="left", va="center", color="#15803D")

    plt.tight_layout()
    p = FIG_DIR / "fig2_3_conv2_systolic_pe.png"
    plt.savefig(p, dpi=300)
    plt.close(fig)
    print(f"Generated {p}")

def draw_fsm_conv1():
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis("off")

    ax.text(50, 47, "Figure 3.1: conv1_array Finite State Machine (6 Real States)",
            ha="center", va="center", fontsize=11.5, fontweight="bold", color="#0F172A")
    ax.text(50, 44, "Controls Weight Preload, Sliding Window Stride, Serial 9-Tap MAC, and Valid Strobe",
            ha="center", va="center", fontsize=8.5, color="#475569")

    # State positions: horizontal sequence
    states = [
        ("ST_INIT\n(3'd0)", 10, 25, "#E0F2FE", "#0284C7", "Load 9 weights\ninto 4 PEs (init_cnt)"),
        ("ST_ADVANCE\n(3'd1)", 28, 25, "#FEF3C7", "#D97706", "Advance window_gen\nby 1 cycle"),
        ("ST_FETCH\n(3'd2)", 46, 25, "#FEF9C3", "#CA8A04", "Wait for window_valid\nfrom window_gen"),
        ("ST_MAC\n(3'd3)", 64, 25, "#EFF6FF", "#2563EB", "Accumulate 9 taps\n(mac_cnt == 0..8)"),
        ("ST_WAIT_VALID\n(3'd4)", 82, 25, "#DCFCE7", "#16A34A", "1-cycle register delay\nfor PE valid_out"),
        ("ST_DONE\n(3'd5)", 93, 10, "#F3E8FF", "#9333EA", "Assert done strobe\nInference complete")
    ]

    for name, x, y, fc, ec, desc in states:
        w, h = 13, 10
        if "DONE" in name: w, h = 11, 8
        b = patches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.4", fc=fc, ec=ec, lw=1.5)
        ax.add_patch(b)
        ax.text(x, y+1.2, name, ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0F172A")
        ax.text(x, y-2.5, desc, ha="center", va="center", fontsize=6, color="#334155")

    # Transitions
    kw = dict(arrowstyle="->", lw=1.3, color="#0F172A")
    # Reset -> INIT
    ax.annotate("", xy=(3.5, 25), xytext=(0, 25), arrowprops=kw)
    ax.text(1.5, 27, "reset", fontsize=6.5)

    # INIT -> INIT (self loop)
    ax.annotate("", xy=(10, 30.5), xytext=(7, 30.5), arrowprops=dict(arrowstyle="->", lw=1, color="#64748B", connectionstyle="arc3,rad=1.2"))
    ax.text(8.5, 35, "init_cnt < 8", fontsize=6, ha="center", color="#64748B")

    # INIT -> FETCH
    ax.annotate("", xy=(39.5, 25), xytext=(16.5, 25), arrowprops=kw)
    ax.text(28, 28, "init_cnt == 8", fontsize=6.5, ha="center")

    # FETCH -> FETCH (wait for valid)
    ax.annotate("", xy=(46, 30.5), xytext=(43, 30.5), arrowprops=dict(arrowstyle="->", lw=1, color="#64748B", connectionstyle="arc3,rad=1.2"))
    ax.text(44.5, 35, "!win_valid && !win_done", fontsize=6, ha="center", color="#64748B")

    # FETCH -> MAC
    ax.annotate("", xy=(57.5, 25), xytext=(52.5, 25), arrowprops=kw)
    ax.text(55, 27, "win_valid", fontsize=6.5, ha="center")

    # MAC -> MAC (accumulate 9 taps)
    ax.annotate("", xy=(64, 30.5), xytext=(61, 30.5), arrowprops=dict(arrowstyle="->", lw=1, color="#64748B", connectionstyle="arc3,rad=1.2"))
    ax.text(62.5, 35, "mac_cnt < 8", fontsize=6, ha="center", color="#64748B")

    # MAC -> WAIT_VALID
    ax.annotate("", xy=(75.5, 25), xytext=(70.5, 25), arrowprops=kw)
    ax.text(73, 27, "mac_cnt == 8", fontsize=6.5, ha="center")

    # WAIT_VALID -> ADVANCE (loop back for next window)
    ax.plot([82, 82, 28, 28], [20, 8, 8, 20], color="#2563EB", lw=1.2)
    ax.annotate("", xy=(28, 20), xytext=(28, 10), arrowprops=dict(arrowstyle="->", lw=1.2, color="#2563EB"))
    ax.text(55, 10, "!win_done: Advance pipeline to next pixel window", fontsize=6.5, ha="center", color="#2563EB")

    # ADVANCE -> FETCH
    ax.annotate("", xy=(42, 22), xytext=(34.5, 22), arrowprops=kw)
    ax.text(38, 20, "unconditional", fontsize=5.5, ha="center")

    # FETCH -> DONE
    ax.plot([46, 46, 88], [20, 10, 10], color="#9333EA", lw=1.2)
    ax.annotate("", xy=(88, 10), xytext=(80, 10), arrowprops=dict(arrowstyle="->", lw=1.2, color="#9333EA"))
    ax.text(62, 11.5, "win_done == 1 (all 400 windows processed)", fontsize=6.5, ha="center", color="#9333EA")

    plt.tight_layout()
    p = FIG_DIR / "fig3_1_conv1_fsm.png"
    plt.savefig(p, dpi=300)
    plt.close(fig)
    print(f"Generated {p}")

def draw_fsm_conv2():
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 50)
    ax.axis("off")

    ax.text(55, 47, "Figure 3.2: conv2_array Finite State Machine (6 Real States)",
            ha="center", va="center", fontsize=11.5, fontweight="bold", color="#0F172A")
    ax.text(55, 44, "Controls Feature Ingestion into 100-Word RAMs, Multi-Channel Dot-Products, and Drain",
            ha="center", va="center", fontsize=8.5, color="#475569")

    states = [
        ("ST_LOAD\n(3'd0)", 11, 25, "#E0F2FE", "#0284C7", "Buffer 100 features/ch\nfrom MaxPool1 (write_addr)"),
        ("ST_FETCH\n(3'd1)", 34, 25, "#FEF9C3", "#CA8A04", "Slide conv2_window_gen\nWait for w_valid"),
        ("ST_MAC\n(3'd2)", 56, 25, "#EFF6FF", "#2563EB", "8x conv2_pe dot-products\n(mac_cnt == 0..8)"),
        ("ST_WAIT_VALID\n(3'd3)", 78, 25, "#DCFCE7", "#16A34A", "1-cycle strobe\nfor valid_out"),
        ("ST_ADVANCE\n(3'd4)", 56, 9, "#FEF3C7", "#D97706", "Advance window_gen\nby 1 cycle"),
        ("ST_DONE\n(3'd5)", 99, 25, "#F3E8FF", "#9333EA", "All 64 outputs\ngenerated (w_done)")
    ]

    for name, x, y, fc, ec, desc in states:
        w, h = 12, 9.5
        if "DONE" in name: w, h = 10, 8
        b = patches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.4", fc=fc, ec=ec, lw=1.5)
        ax.add_patch(b)
        ax.text(x, y+1.2, name, ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0F172A")
        ax.text(x, y-2.5, desc, ha="center", va="center", fontsize=6, color="#334155")

    kw = dict(arrowstyle="->", lw=1.3, color="#0F172A")
    # Reset -> LOAD
    ax.annotate("", xy=(5, 25), xytext=(1, 25), arrowprops=kw)
    ax.text(3, 27, "reset", fontsize=6.5)

    # LOAD -> LOAD (self loop)
    ax.annotate("", xy=(11, 30.25), xytext=(8, 30.25), arrowprops=dict(arrowstyle="->", lw=1, color="#64748B", connectionstyle="arc3,rad=1.2"))
    ax.text(9.5, 35, "write_addr < 99", fontsize=6, ha="center", color="#64748B")

    # LOAD -> FETCH
    ax.annotate("", xy=(28, 25), xytext=(17, 25), arrowprops=kw)
    ax.text(22.5, 27.5, "write_addr==99", fontsize=6.5, ha="center", va="bottom")

    # FETCH -> MAC
    ax.annotate("", xy=(50, 25), xytext=(40, 25), arrowprops=kw)
    ax.text(45, 27.5, "w_valid", fontsize=6.5, ha="center", va="bottom")

    # MAC -> MAC
    ax.annotate("", xy=(56, 30.25), xytext=(53, 30.25), arrowprops=dict(arrowstyle="->", lw=1, color="#64748B", connectionstyle="arc3,rad=1.2"))
    ax.text(54.5, 35, "mac_cnt < 8", fontsize=6, ha="center", color="#64748B")

    # MAC -> WAIT_VALID
    ax.annotate("", xy=(72, 25), xytext=(62, 25), arrowprops=kw)
    ax.text(67, 27.5, "mac_cnt == 8", fontsize=6.5, ha="center", va="bottom")

    # WAIT_VALID -> ADVANCE
    ax.plot([78, 78, 62], [20.25, 9, 9], color="#2563EB", lw=1.2)
    ax.annotate("", xy=(62, 9), xytext=(66, 9), arrowprops=dict(arrowstyle="->", lw=1.2, color="#2563EB"))
    ax.text(73, 11, "!w_done", fontsize=6.5, color="#2563EB")

    # ADVANCE -> FETCH
    ax.plot([50, 34, 34], [9, 9, 20.25], color="#2563EB", lw=1.2)
    ax.annotate("", xy=(34, 20.25), xytext=(34, 15), arrowprops=dict(arrowstyle="->", lw=1.2, color="#2563EB"))

    # WAIT_VALID -> DONE
    ax.annotate("", xy=(94, 25), xytext=(84, 25), arrowprops=dict(arrowstyle="->", lw=1.2, color="#9333EA"))
    ax.text(89, 27.5, "w_done", fontsize=6.5, ha="center", va="bottom", color="#9333EA")

    plt.tight_layout()
    p = FIG_DIR / "fig3_2_conv2_fsm.png"
    plt.savefig(p, dpi=300)
    plt.close(fig)
    print(f"Generated {p}")

def draw_fsm_mlp_head():
    fig, ax = plt.subplots(figsize=(9.5, 5.0), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis("off")

    ax.text(50, 47, "Figure 3.3: mlp_head 4-State Controller and 3-Layer Tiling Loop",
            ha="center", va="center", fontsize=11.5, fontweight="bold", color="#0F172A")
    ax.text(50, 44, "Time-Multiplexed Execution of 200->64->32->10 Architecture Across 62 Tiles",
            ha="center", va="center", fontsize=8.5, color="#475569")

    # 4 Main states
    b_idle = patches.FancyBboxPatch((4, 20), 15, 12, boxstyle="round,pad=0.5", fc="#F8FAFC", ec="#64748B", lw=1.5)
    ax.add_patch(b_idle)
    ax.text(11.5, 28, "IDLE (3'd0)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0F172A")
    ax.text(11.5, 23.5, "Buffers 200 MaxPool2\nfeatures into ram_A\n(write_ptr < 200)", ha="center", va="center", fontsize=6.5, color="#475569")

    b_load = patches.FancyBboxPatch((31, 20), 16, 12, boxstyle="round,pad=0.5", fc="#FEF3C7", ec="#D97706", lw=1.5)
    ax.add_patch(b_load)
    ax.text(39, 28, "LOAD_WEIGHT (3'd1)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#B45309")
    ax.text(39, 23.5, "Preloads 16x16 weights\nfrom ROM into systolic PEs\nDuration: 16 cycles (timer)", ha="center", va="center", fontsize=6.5, color="#78350F")

    b_comp = patches.FancyBboxPatch((57, 20), 16, 12, boxstyle="round,pad=0.5", fc="#EFF6FF", ec="#2563EB", lw=1.5)
    ax.add_patch(b_comp)
    ax.text(65, 28, "COMPUTE (3'd2)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1D4ED8")
    ax.text(65, 23.5, "Streams 16 features\nSystolic matrix multiply\nDuration: 32 cycles (timer)", ha="center", va="center", fontsize=6.5, color="#1E40AF")

    b_done = patches.FancyBboxPatch((86, 20), 10, 12, boxstyle="round,pad=0.5", fc="#F3E8FF", ec="#9333EA", lw=1.5)
    ax.add_patch(b_done)
    ax.text(91, 28, "DONE (3'd3)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#7E22CE")
    ax.text(91, 23.5, "valid_out <= 1\n10 output logits\nready for argmax", ha="center", va="center", fontsize=6.5, color="#475569")

    # Transitions
    kw = dict(arrowstyle="->", lw=1.3, color="#0F172A")
    ax.annotate("", xy=(4, 26), xytext=(0, 26), arrowprops=kw)
    ax.text(1.5, 28, "reset", fontsize=6.5)

    # IDLE -> LOAD_WEIGHT
    ax.annotate("", xy=(31, 26), xytext=(19, 26), arrowprops=kw)
    ax.text(25, 28.5, "write_ptr == 200\n(Start L1)", fontsize=6.5, ha="center", va="bottom")

    # LOAD_WEIGHT -> COMPUTE
    ax.annotate("", xy=(57, 26), xytext=(47, 26), arrowprops=kw)
    ax.text(52, 28.5, "timer == 15\n(16 cycles)", fontsize=6.5, ha="center", va="bottom")

    # COMPUTE -> LOAD_WEIGHT (Next Tile)
    ax.plot([65, 65, 39, 39], [20, 8, 8, 20], color="#2563EB", lw=1.2)
    ax.annotate("", xy=(39, 20), xytext=(39, 10), arrowprops=dict(arrowstyle="->", lw=1.2, color="#2563EB"))
    ax.text(52, 10, "timer == 31 && !last_tile: Advance (c_idx, r_idx, layer)", fontsize=7, ha="center", color="#2563EB")

    # COMPUTE -> DONE
    ax.annotate("", xy=(86, 26), xytext=(73, 26), arrowprops=dict(arrowstyle="->", lw=1.2, color="#9333EA"))
    ax.text(79.5, 28.5, "layer==3 &&\nlast_tile", fontsize=6.5, ha="center", va="bottom", color="#9333EA")

    # Bottom summary box for tiles
    box_t = patches.FancyBboxPatch((8, 1), 84, 5.5, boxstyle="round,pad=0.3", fc="#F8FAFC", ec="#94A3B8", lw=1)
    ax.add_patch(box_t)
    ax.text(50, 3.8, "Tiling Hierarchy: Layer 1 (200->64): 4 row x 13 col = 52 tiles | Layer 2 (64->32): 2 row x 4 col = 8 tiles | Layer 3 (32->10): 1 row x 2 col = 2 tiles", fontsize=6.5, fontweight="bold", ha="center", color="#0F172A")
    ax.text(50, 1.8, "Total Tile Cycles: (52 + 8 + 2) x 48 = 2,976 cycles + 2 overhead (1 state transition + 1 done) = 2,978 cycles measured", fontsize=6.5, ha="center", color="#475569")

    plt.tight_layout()
    p = FIG_DIR / "fig3_3_mlp_head_fsm.png"
    plt.savefig(p, dpi=300)
    plt.close(fig)
    print(f"Generated {p}")

if __name__ == "__main__":
    draw_v2_top_block_diagram()
    draw_mac_conv_pe_datapath()
    draw_conv2_and_systolic_pe()
    draw_fsm_conv1()
    draw_fsm_conv2()
    draw_fsm_mlp_head()
    print("All architectural figures generated successfully!")
