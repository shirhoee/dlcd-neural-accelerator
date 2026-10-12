import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

fig, ax = plt.subplots(figsize=(16, 11), dpi=200)
fig.patch.set_facecolor('#f8f9fa')
ax.set_facecolor('#f8f9fa')

# Helper functions to draw IEEE standard logic gates with exact ports
def draw_and_gate(ax, x, y, w=1.2, h=1.0, label='&'):
    verts = [
        (x, y - h/2),
        (x, y + h/2),
        (x + w*0.45, y + h/2),
        (x + w, y + h*0.25),
        (x + w, y - h*0.25),
        (x + w*0.45, y - h/2),
        (x, y - h/2)
    ]
    codes = [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.5, zorder=4)
    ax.add_patch(patch)
    if label:
        ax.text(x + w*0.35, y, label, ha='center', va='center', fontsize=9, fontweight='bold', color='#1e293b', zorder=5)

def draw_xor_gate(ax, x, y, w=1.2, h=1.0, label=''):
    verts = [
        (x + 0.15, y - h/2),
        (x + 0.35, y),
        (x + 0.15, y + h/2),
        (x + w*0.5, y + h/2),
        (x + w, y),
        (x + w*0.5, y - h/2),
        (x + 0.15, y - h/2)
    ]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.5, zorder=4)
    ax.add_patch(patch)
    # Curved back line
    back_verts = [(x, y - h/2), (x + 0.2, y), (x, y + h/2)]
    back_codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    back_patch = patches.PathPatch(Path(back_verts, back_codes), facecolor='none', edgecolor='#1e293b', linewidth=1.5, zorder=4)
    ax.add_patch(back_patch)
    if label:
        ax.text(x + w*0.45, y, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1e293b', zorder=5)

def draw_or_gate(ax, x, y, w=1.2, h=1.0, label='≥1'):
    verts = [
        (x, y - h/2),
        (x + 0.25, y),
        (x, y + h/2),
        (x + w*0.45, y + h/2),
        (x + w, y),
        (x + w*0.45, y - h/2),
        (x, y - h/2)
    ]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.5, zorder=4)
    ax.add_patch(patch)
    if label:
        ax.text(x + w*0.4, y, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1e293b', zorder=5)

def draw_not_gate(ax, x, y, w=0.75, h=0.5):
    verts = [(x, y - h/2), (x, y + h/2), (x + w*0.65, y), (x, y - h/2)]
    path = Path(verts, [Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])
    patch = patches.PathPatch(path, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.4, zorder=4)
    ax.add_patch(patch)
    bubble = patches.Circle((x + w*0.65 + 0.08, y), 0.07, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.4, zorder=5)
    ax.add_patch(bubble)

def draw_dff(ax, x, y, w=1.2, h=1.5, title='D-FF', q_label='Q', d_label='D'):
    rect = patches.Rectangle((x, y - h/2), w, h, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.5, zorder=4)
    ax.add_patch(rect)
    # Clock triangle at bottom-left
    ax.plot([x, x + 0.2, x], [y - h/2 + 0.2, y - h/2 + 0.35, y - h/2 + 0.5], color='#1e293b', linewidth=1.4, zorder=5)
    ax.text(x + 0.18, y + 0.3, d_label, fontsize=8.5, fontweight='bold', color='#475569', ha='left', va='center', zorder=5)
    ax.text(x + w - 0.18, y + 0.3, q_label, fontsize=8.5, fontweight='bold', color='#475569', ha='right', va='center', zorder=5)
    ax.text(x + w/2, y - 0.4, title, fontsize=8, fontweight='bold', color='#1e3a8a', ha='center', va='center', zorder=5)

# --- HEADER BLOCK ---
ax.text(0.5, 10.45, 'conv_pe & mac_q7_8 : Gate-Level Logic Schematic', fontsize=16, fontweight='bold', color='#0f172a', family='serif')
ax.text(0.5, 10.15, 'Digital Logic & Computer Design (DLCD) | Synchronous Control & Arithmetic Microarchitecture', fontsize=10, color='#475569', style='italic')

# Metadata Box
meta_box = patches.FancyBboxPatch((10.8, 9.55), 4.7, 1.15, boxstyle="round,pad=0.08", facecolor='#f1f5f9', edgecolor='#94a3b8', linewidth=1.2, zorder=2)
ax.add_patch(meta_box)
ax.text(11.0, 10.45, 'MODULE: conv_pe.v  |  SUBMODULE: mac_q7_8.v', fontsize=7.5, fontweight='bold', color='#1e293b')
ax.text(11.0, 10.18, 'LOGIC FAMILY: CMOS Standard Cells / FPGA LUTs', fontsize=7.5, color='#334155')
ax.text(11.0, 9.90, 'Shreyansh Raj (PES2UG25CS516) | Sarthak Bhowmik (PES2UG25CS493)', fontsize=7.2, color='#1e3a8a')
ax.text(11.0, 9.68, 'Shaurya Singh (PES2UG25CS508) | Shreya Anand (PES2UG25CS515)', fontsize=7.2, color='#1e3a8a')

# =========================================================================
# SECTION A: 4-BIT MODULO-9 SYNCHRONOUS BINARY UP-COUNTER
# =========================================================================
box_a = patches.FancyBboxPatch((0.5, 4.8), 7.3, 4.5, boxstyle="round,pad=0.15", facecolor='#f8fafc', edgecolor='#3b82f6', linewidth=1.4, linestyle='--', zorder=1)
ax.add_patch(box_a)
ax.text(0.8, 9.05, 'A. 4-Bit Modulo-9 Synchronous Binary Up-Counter (tap_idx[3:0])', fontsize=10, fontweight='bold', color='#1d4ed8')

ax.text(4.15, 8.60, 'Next-State Logic: D = (Q + 1) mod 9 when mac_en=1', fontsize=8.5, ha='center', color='#334155', fontweight='bold')
ax.text(4.15, 8.25, 'D0 = ~Q0 · ~Q3  |  D1 = (Q1 ⊕ Q0) · ~Q3  |  D2 = (Q2 ⊕ (Q1·Q0)) · ~Q3  |  D3 = (Q3·~Q0) + (Q2·Q1·Q0)', fontsize=6.8, ha='center', color='#475569', family='monospace')

dff_xs = [1.2, 2.9, 4.6, 6.3]
dff_y = 6.6
for i, x in enumerate(dff_xs):
    draw_dff(ax, x, dff_y, w=1.0, h=1.4, title=f'FF{i}', q_label=f'Q{i}', d_label=f'D{i}')
    # Output stubs pointing up
    ax.plot([x + 0.82, x + 0.82], [dff_y + 0.3, dff_y + 0.9], color='#0284c7', linewidth=1.5, zorder=3)
    # Output net tag
    ax.text(x + 0.82, dff_y + 1.0, f'Q{i}', fontsize=8, fontweight='bold', color='#0284c7', ha='center', va='bottom', zorder=5)

# Clock and Enable Rails at bottom of Box A
clk_y = 5.3
en_y = 5.0
ax.plot([0.8, 7.5], [clk_y, clk_y], color='#dc2626', linewidth=1.5, zorder=3)
ax.text(0.7, clk_y, 'clk', color='#dc2626', fontsize=8, fontweight='bold', ha='right', va='center')

ax.plot([0.8, 7.5], [en_y, en_y], color='#ea580c', linewidth=1.5, zorder=3)
ax.text(0.7, en_y, 'mac_en', color='#ea580c', fontsize=8, fontweight='bold', ha='right', va='center')

for x in dff_xs:
    # Clock vertical connection to FF clock triangle
    ax.plot([x + 0.2, x + 0.2], [clk_y, dff_y - 0.7 + 0.35], color='#dc2626', linewidth=1.2, zorder=3)
    # Enable vertical connection to FF bottom
    ax.plot([x + 0.5, x + 0.5], [en_y, dff_y - 0.7], color='#ea580c', linewidth=1.2, zorder=3)

# =========================================================================
# SECTION B: == 8 COMPARATOR & VALID_OUT LOGIC
# =========================================================================
box_b = patches.FancyBboxPatch((8.1, 4.8), 7.4, 4.5, boxstyle="round,pad=0.15", facecolor='#f8fafc', edgecolor='#059669', linewidth=1.4, linestyle='--', zorder=1)
ax.add_patch(box_b)
ax.text(8.4, 9.05, 'B. Terminal Count (== 8) Comparator & valid_out Logic', fontsize=10, fontweight='bold', color='#047857')
ax.text(8.4, 8.65, 'Detects State 8 (1000b) via Q3 · ~Q2 · ~Q1 · ~Q0, gated by mac_en', fontsize=7.5, color='#475569')

# 4 Inputs from Counter: Q3, Q2, Q1, Q0
in_y = {'Q3': 8.1, 'Q2': 7.4, 'Q1': 6.7, 'Q0': 6.0}

# Inverters for Q2, Q1, Q0
draw_not_gate(ax, 9.0, in_y['Q2'], w=0.7, h=0.45)
draw_not_gate(ax, 9.0, in_y['Q1'], w=0.7, h=0.45)
draw_not_gate(ax, 9.0, in_y['Q0'], w=0.7, h=0.45)

# Input stubs with tags
for sig, y_pos in in_y.items():
    ax.text(8.3, y_pos, sig, fontsize=8, fontweight='bold', color='#0284c7', ha='right', va='center')
    if sig != 'Q3':
        ax.plot([8.35, 9.0], [y_pos, y_pos], color='#0284c7', linewidth=1.3, zorder=3)
    else:
        # Q3 straight line to AND gate
        ax.plot([8.35, 10.3], [y_pos, y_pos], color='#0284c7', linewidth=1.3, zorder=3)

# Inverter output wires to AND gate
for sig in ['Q2', 'Q1', 'Q0']:
    y_pos = in_y[sig]
    ax.plot([9.78, 10.3], [y_pos, y_pos], color='#0284c7', linewidth=1.3, zorder=3)

# 4-Input AND Gate
draw_and_gate(ax, 10.3, 7.05, w=1.3, h=2.4, label='&')

# Wire from 4-input AND to 2-input AND
# 4-input AND output is at (11.6, 7.05)
ax.plot([11.6, 12.3], [7.05, 7.05], color='#047857', linewidth=1.5, zorder=3)
ax.text(11.95, 7.25, 'eq_8', fontsize=7.5, fontweight='bold', color='#047857', ha='center', va='bottom')

# 2-Input AND Gate (eq_8 AND mac_en)
draw_and_gate(ax, 12.3, 6.8, w=1.0, h=1.0, label='&')

# mac_en routed orthogonally from below
ax.plot([12.0, 12.0], [5.0, 6.55], color='#ea580c', linewidth=1.4, zorder=3)
ax.plot([12.0, 12.3], [6.55, 6.55], color='#ea580c', linewidth=1.4, zorder=3)
ax.text(11.9, 5.4, 'mac_en', color='#ea580c', fontsize=7.5, fontweight='bold', ha='right', va='center')

# Wire from 2-input AND to D-FF
# 2-input AND output is at (13.3, 6.8)
ax.plot([13.3, 13.9], [6.8, 6.8], color='#059669', linewidth=1.5, zorder=3)
ax.plot([13.9, 13.9], [6.8, 7.1], color='#059669', linewidth=1.5, zorder=3)
ax.plot([13.9, 14.1], [7.1, 7.1], color='#059669', linewidth=1.5, zorder=3)

# D-FF for valid_out
draw_dff(ax, 14.1, 6.8, w=1.0, h=1.4, title='D-FF', q_label='Q', d_label='D')

# valid_out output wire
ax.plot([15.1, 15.4], [7.1, 7.1], color='#059669', linewidth=2.0, zorder=3)
ax.text(15.45, 7.1, 'valid_out', color='#059669', fontsize=8.5, fontweight='bold', ha='left', va='center')

# Clock connection to valid_out D-FF
ax.plot([14.3, 14.3], [5.3, 6.1 + 0.35], color='#dc2626', linewidth=1.2, zorder=3)
ax.plot([12.0, 14.3], [5.3, 5.3], color='#dc2626', linewidth=1.2, zorder=3)
ax.text(13.1, 5.15, 'clk', color='#dc2626', fontsize=7.2, fontweight='bold', ha='center', va='top')

# =========================================================================
# SECTION C: FEEDBACK CLEAR MULTIPLEXER GATE SLICE (Bit k)
# =========================================================================
box_c = patches.FancyBboxPatch((0.5, 0.4), 4.3, 4.1, boxstyle="round,pad=0.15", facecolor='#f8fafc', edgecolor='#d97706', linewidth=1.4, linestyle='--', zorder=1)
ax.add_patch(box_c)
ax.text(0.8, 4.15, 'C. Feedback MUX 1-Bit Gate Slice (k)', fontsize=9.5, fontweight='bold', color='#b45309')
ax.text(0.8, 3.82, 'acc_in[k] = ~clr_acc · out_acc[k]', fontsize=7.5, color='#475569', family='monospace')

# Inverter on clr_acc
draw_not_gate(ax, 1.5, 3.0, w=0.7, h=0.45)
ax.text(0.7, 3.0, 'clr_acc', color='#d97706', fontsize=7.8, fontweight='bold', ha='right', va='center')
ax.plot([0.75, 1.5], [3.0, 3.0], color='#d97706', linewidth=1.4, zorder=3)

# 2-Input AND Gate
draw_and_gate(ax, 2.7, 2.5, w=1.1, h=1.1, label='&')

# Wire from Inverter to top input of AND (orthogonal)
ax.plot([2.28, 2.5], [3.0, 3.0], color='#d97706', linewidth=1.3, zorder=3)
ax.plot([2.5, 2.5], [3.0, 2.75], color='#d97706', linewidth=1.3, zorder=3)
ax.plot([2.5, 2.7], [2.75, 2.75], color='#d97706', linewidth=1.3, zorder=3)

# Wire from out_acc[k] to bottom input of AND (orthogonal)
ax.text(0.7, 1.9, 'out_acc[k]', color='#1e293b', fontsize=7.8, fontweight='bold', ha='right', va='center')
ax.plot([0.75, 2.5], [1.9, 1.9], color='#1e293b', linewidth=1.4, zorder=3)
ax.plot([2.5, 2.5], [1.9, 2.25], color='#1e293b', linewidth=1.4, zorder=3)
ax.plot([2.5, 2.7], [2.25, 2.25], color='#1e293b', linewidth=1.4, zorder=3)

# Output of MUX slice
ax.plot([3.8, 4.4], [2.5, 2.5], color='#b45309', linewidth=1.6, zorder=3)
ax.text(4.45, 2.5, 'acc_in[k]', color='#b45309', fontsize=8, fontweight='bold', ha='left', va='center')

ax.text(2.65, 0.9, 'Instantiated 16× for bits 0..15.\nWhen clr_acc=1, forces acc_in=16\'sd0.', fontsize=7.0, color='#64748b', ha='center', style='italic')

# =========================================================================
# SECTION D: 1-BIT FULL ADDER SLICE (FAk in Ripple Carry Chain)
# =========================================================================
box_d = patches.FancyBboxPatch((5.1, 0.4), 5.7, 4.1, boxstyle="round,pad=0.15", facecolor='#f8fafc', edgecolor='#6366f1', linewidth=1.4, linestyle='--', zorder=1)
ax.add_patch(box_d)
ax.text(5.3, 4.15, 'D. 1-Bit Full Adder Slice (FAk in Ripple Chain)', fontsize=9.5, fontweight='bold', color='#4338ca')
ax.text(5.3, 3.82, 'Sk = Ak ⊕ Bk ⊕ Cin  |  Cout = (Ak·Bk) + (Cin·(Ak ⊕ Bk))', fontsize=7.0, color='#475569', family='monospace')

# Input signals on the left of Box D
ax.text(5.2, 3.3, 'product[k+8]', fontsize=7.5, color='#1e293b', ha='left', va='center')
ax.text(5.2, 2.7, 'acc_in[k]', fontsize=7.5, color='#1e293b', ha='left', va='center')
ax.text(5.2, 1.4, 'Cin[k]', fontsize=7.5, color='#ea580c', fontweight='bold', ha='left', va='center')

# XOR Gate 1: Ak ⊕ Bk
draw_xor_gate(ax, 6.6, 3.0, w=1.0, h=0.9, label='')
ax.plot([6.2, 6.6], [3.3, 3.25], color='#1e293b', linewidth=1.2, zorder=3)
ax.plot([6.2, 6.6], [2.7, 2.75], color='#1e293b', linewidth=1.2, zorder=3)

# XOR Gate 2: (Ak ⊕ Bk) ⊕ Cin
draw_xor_gate(ax, 8.4, 2.7, w=1.0, h=0.9, label='')
# Wire from XOR 1 output (7.6, 3.0) to XOR 2 top input (8.4, 2.95)
ax.plot([7.6, 8.4], [3.0, 2.95], color='#4338ca', linewidth=1.3, zorder=3)
ax.text(7.9, 3.15, 'Pk', fontsize=6.8, color='#4338ca', style='italic', ha='center')

# Cin orthogonal routing to XOR 2 bottom input (8.4, 2.45)
ax.plot([5.8, 8.0], [1.4, 1.4], color='#ea580c', linewidth=1.3, zorder=3)
ax.plot([8.0, 8.0], [1.4, 2.45], color='#ea580c', linewidth=1.3, zorder=3)
ax.plot([8.0, 8.4], [2.45, 2.45], color='#ea580c', linewidth=1.3, zorder=3)

# Sum output mac_result[k]
ax.plot([9.4, 10.3], [2.7, 2.7], color='#4338ca', linewidth=1.6, zorder=3)
ax.text(10.35, 2.7, 'mac_result[k]', fontsize=7.8, fontweight='bold', color='#4338ca', ha='left', va='center')

# Carry Logic:
# AND Gate 1 (Ak · Bk): Generate Gk
draw_and_gate(ax, 6.6, 1.9, w=0.9, h=0.7, label='&')
# Taps from Ak and Bk (orthogonal)
ax.plot([6.3, 6.3], [3.3, 2.1], color='#1e293b', linewidth=1.1, zorder=3)
ax.plot([6.3, 6.6], [2.1, 2.1], color='#1e293b', linewidth=1.1, zorder=3)
ax.plot([6.4, 6.4], [2.7, 1.7], color='#1e293b', linewidth=1.1, zorder=3)
ax.plot([6.4, 6.6], [1.7, 1.7], color='#1e293b', linewidth=1.1, zorder=3)

# AND Gate 2 (Pk · Cin): Propagate Pk · Cin
draw_and_gate(ax, 8.4, 1.4, w=0.9, h=0.7, label='&')
# Tap Pk from wire
ax.plot([7.8, 7.8], [3.0, 1.6], color='#4338ca', linewidth=1.1, zorder=3)
ax.plot([7.8, 8.4], [1.6, 1.6], color='#4338ca', linewidth=1.1, zorder=3)
# Tap Cin from wire
ax.plot([8.0, 8.4], [1.2, 1.2], color='#ea580c', linewidth=1.1, zorder=3)

# OR Gate for Cout = Gk + (Pk · Cin)
draw_or_gate(ax, 9.5, 1.65, w=0.9, h=0.8, label='≥1')
# Wire from AND1 to OR top input
ax.plot([7.5, 9.1], [1.9, 1.9], color='#4338ca', linewidth=1.1, zorder=3)
ax.plot([9.1, 9.5], [1.9, 1.85], color='#4338ca', linewidth=1.1, zorder=3)
# Wire from AND2 to OR bottom input
ax.plot([9.3, 9.5], [1.4, 1.45], color='#4338ca', linewidth=1.1, zorder=3)

# Cout output wire - stays strictly inside Box D!
ax.plot([10.4, 10.7], [1.65, 1.65], color='#ea580c', linewidth=1.5, zorder=3)
ax.text(10.6, 1.9, 'Cout[k]', fontsize=7.5, fontweight='bold', color='#ea580c', ha='center', va='bottom')
ax.text(10.6, 1.35, '(to FAk+1)', fontsize=6.8, color='#ea580c', ha='center', va='top')

# =========================================================================
# SECTION E: TRUNCATION SLICE WIRING MAP [23:8]
# =========================================================================
box_e = patches.FancyBboxPatch((11.1, 0.4), 4.4, 4.1, boxstyle="round,pad=0.15", facecolor='#f8fafc', edgecolor='#0284c7', linewidth=1.4, linestyle='--', zorder=1)
ax.add_patch(box_e)
ax.text(11.3, 4.15, 'E. Truncation Slice Wiring [23:8]', fontsize=9.5, fontweight='bold', color='#0369a1')
ax.text(11.3, 3.82, 'Product[31:0] from 16×16 Multiplier:', fontsize=7.2, color='#334155')

trunc_boxes = [
    ('product[31:24]', '8b Extended Integer\n(Discarded; Headroom Verified)', '#fee2e2', '#b91c1c', 2.9),
    ('product[23:8]', '16b Q7.8 Result\n(Hardwired to Adder Bk[15:0])', '#dbeafe', '#1d4ed8', 2.05),
    ('product[7:0]', '8b Sub-fractional\n(Truncated Floor / Dropped)', '#fef3c7', '#b45309', 1.2)
]

for label, desc, bg, fg, y_box in trunc_boxes:
    r = patches.Rectangle((11.3, y_box - 0.35), 4.0, 0.65, facecolor=bg, edgecolor=fg, linewidth=1.2, zorder=2)
    ax.add_patch(r)
    ax.text(11.45, y_box, label, fontsize=7.5, fontweight='bold', color=fg, va='center')
    ax.text(12.75, y_box, desc, fontsize=6.5, color='#1e293b', va='center')

ax.text(13.3, 0.65, 'Zero Combinational Gates\nPure Wire Slice (Bit Shift by 8)', fontsize=7.2, color='#0284c7', fontweight='bold', ha='center', style='italic')

# Frame and Limits
ax.set_xlim(0, 16)
ax.set_ylim(0, 11)
ax.axis('off')

plt.tight_layout()
out_file = os.path.join(r'C:\Users\SHREYANSH RAJ\DLCD_Neural_Accelerator\docs\mini_project_submission', 'conv_pe_gate_level_diagram.png')
plt.savefig(out_file, facecolor=fig.get_facecolor(), edgecolor='none', dpi=200)
plt.close()

print('Saved perfectly routed gate-level diagram to:', out_file)
