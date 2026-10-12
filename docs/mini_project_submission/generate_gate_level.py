import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

fig, ax = plt.subplots(figsize=(16, 11), dpi=200)
fig.patch.set_facecolor('#f8f9fa')
ax.set_facecolor('#f8f9fa')

# Helper functions to draw IEEE standard logic gates
def draw_and_gate(ax, x, y, w=1.2, h=1.0, label=''):
    # AND gate: flat left, curved right
    verts = [
        (x, y - h/2),
        (x, y + h/2),
        (x + w/2, y + h/2),
        (x + w, y + h/4),
        (x + w, y - h/4),
        (x + w/2, y - h/2),
        (x, y - h/2)
    ]
    codes = [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.5, zorder=3)
    ax.add_patch(patch)
    if label:
        ax.text(x + w*0.35, y, label, ha='center', va='center', fontsize=9, fontweight='bold', color='#1e293b')

def draw_xor_gate(ax, x, y, w=1.2, h=1.0, label=''):
    verts = [
        (x + 0.15, y - h/2),
        (x + 0.35, y),
        (x + 0.15, y + h/2),
        (x + w/2, y + h/2),
        (x + w, y),
        (x + w/2, y - h/2),
        (x + 0.15, y - h/2)
    ]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.5, zorder=3)
    ax.add_patch(patch)
    # Curved back line
    back_verts = [(x, y - h/2), (x + 0.2, y), (x, y + h/2)]
    back_codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    back_patch = patches.PathPatch(Path(back_verts, back_codes), facecolor='none', edgecolor='#1e293b', linewidth=1.5, zorder=3)
    ax.add_patch(back_patch)
    if label:
        ax.text(x + w*0.45, y, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1e293b')

def draw_or_gate(ax, x, y, w=1.2, h=1.0, label=''):
    verts = [
        (x, y - h/2),
        (x + 0.25, y),
        (x, y + h/2),
        (x + w/2, y + h/2),
        (x + w, y),
        (x + w/2, y - h/2),
        (x, y - h/2)
    ]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.5, zorder=3)
    ax.add_patch(patch)
    if label:
        ax.text(x + w*0.4, y, label, ha='center', va='center', fontsize=9, fontweight='bold', color='#1e293b')

def draw_not_gate(ax, x, y, w=0.8, h=0.6):
    verts = [(x, y - h/2), (x, y + h/2), (x + w*0.7, y), (x, y - h/2)]
    path = Path(verts, [Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])
    patch = patches.PathPatch(path, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.4, zorder=3)
    ax.add_patch(patch)
    bubble = patches.Circle((x + w*0.7 + 0.08, y), 0.08, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.4, zorder=4)
    ax.add_patch(bubble)

def draw_dff(ax, x, y, w=1.3, h=1.6, title='D-FF', q_label='Q', d_label='D'):
    rect = patches.Rectangle((x, y - h/2), w, h, facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.5, zorder=3)
    ax.add_patch(rect)
    # Clock triangle
    ax.plot([x, x + 0.25, x], [y - h/2 + 0.2, y - h/2 + 0.35, y - h/2 + 0.5], color='#1e293b', linewidth=1.4, zorder=4)
    ax.text(x + 0.2, y + 0.35, d_label, fontsize=8.5, fontweight='bold', color='#475569', ha='left', va='center')
    ax.text(x + w - 0.2, y + 0.35, q_label, fontsize=8.5, fontweight='bold', color='#475569', ha='right', va='center')
    ax.text(x + w/2, y - 0.45, title, fontsize=8, fontweight='bold', color='#1e3a8a', ha='center', va='center')

# Title & Metadata Block
ax.text(0.5, 10.4, 'conv_pe & mac_q7_8 : Gate-Level Logic Schematic', fontsize=16, fontweight='bold', color='#0f172a', family='serif')
ax.text(0.5, 10.05, 'Digital Logic & Computer Design (DLCD) | Synchronous Control & Arithmetic Microarchitecture', fontsize=10, color='#475569', style='italic')

# Header Box
meta_box = patches.FancyBboxPatch((11.5, 9.6), 4.0, 1.0, boxstyle="round,pad=0.1", facecolor='#f1f5f9', edgecolor='#94a3b8', linewidth=1)
ax.add_patch(meta_box)
ax.text(11.7, 10.35, 'MODULE: conv_pe.v / mac_q7_8.v', fontsize=7.5, fontweight='bold', color='#1e293b')
ax.text(11.7, 10.05, 'LOGIC FAMILY: CMOS Standard Cells / FPGA LUTs', fontsize=7.5, color='#334155')
ax.text(11.7, 9.75, 'DESIGN TEAM: Shreyansh Raj et al. (PES2UG25CS516)', fontsize=7.5, color='#334155')

# SECTION A: 4-BIT MODULO-9 BINARY UP-COUNTER (tap_idx[3:0]) & CONTROL GATES
box_a = patches.FancyBboxPatch((0.5, 4.8), 7.2, 4.6, boxstyle="round,pad=0.2", facecolor='#f8fafc', edgecolor='#3b82f6', linewidth=1.5, linestyle='--')
ax.add_patch(box_a)
ax.text(0.8, 9.15, 'A. 4-Bit Modulo-9 Synchronous Binary Counter & Next-State Logic', fontsize=10.5, fontweight='bold', color='#1d4ed8')

# 4 D Flip-Flops for tap_idx[0..3]
dff_xs = [1.2, 2.9, 4.6, 6.3]
dff_y = 6.4
for i, x in enumerate(dff_xs):
    draw_dff(ax, x, dff_y, w=1.1, h=1.5, title=f'FF{i}', q_label=f'Q{i}', d_label=f'D{i}')

# Next-state logic representation
ax.text(4.1, 8.4, 'Next-State Equations: Di = (Q + 1) mod 9 when mac_en=1', fontsize=8.5, ha='center', color='#334155', fontweight='bold')
ax.text(4.1, 8.0, 'D0 = ~Q0 · ~Q3 | D1 = (Q1 ⊕ Q0) · ~Q3 | D2 = (Q2 ⊕ (Q1·Q0)) · ~Q3 | D3 = (Q3·~Q0) + (Q2·Q1·Q0)', fontsize=7.2, ha='center', color='#475569', family='monospace')

# Common clock, reset, and mac_en bus
ax.plot([0.8, 7.3], [5.3, 5.3], color='#e11d48', linewidth=1.5) # clk
ax.text(0.7, 5.3, 'clk', color='#e11d48', fontsize=8, fontweight='bold', ha='right', va='center')
ax.plot([0.8, 7.3], [5.0, 5.0], color='#ea580c', linewidth=1.5) # mac_en
ax.text(0.7, 5.0, 'mac_en', color='#ea580c', fontsize=8, fontweight='bold', ha='right', va='center')

for x in dff_xs:
    # clk connection to triangle
    ax.plot([x + 0.25, x + 0.25], [5.3, dff_y - 0.75 + 0.35], color='#e11d48', linewidth=1.2)
    # EN connection
    ax.plot([x + 0.55, x + 0.55], [5.0, dff_y - 0.75], color='#ea580c', linewidth=1.2)

# SECTION B: == 8 COMPARATOR & VALID_OUT GENERATOR
box_b = patches.FancyBboxPatch((8.2, 4.8), 7.3, 4.6, boxstyle="round,pad=0.2", facecolor='#f8fafc', edgecolor='#059669', linewidth=1.5, linestyle='--')
ax.add_patch(box_b)
ax.text(8.5, 9.15, 'B. Terminal Count (== 8) Comparator & valid_out Logic', fontsize=10.5, fontweight='bold', color='#047857')

# 4-input AND for (tap_idx == 8) = Q3 · ~Q2 · ~Q1 · ~Q0
ax.text(8.7, 8.2, 'Inputs from Counter: Q3, Q2, Q1, Q0 (where 8 = 1000b)', fontsize=8, color='#334155')

# Draw Inverters for Q2, Q1, Q0
draw_not_gate(ax, 9.2, 7.6, w=0.6, h=0.45)
ax.text(8.9, 7.6, 'Q2', fontsize=7.5, color='#475569', ha='right', va='center')
draw_not_gate(ax, 9.2, 6.9, w=0.6, h=0.45)
ax.text(8.9, 6.9, 'Q1', fontsize=7.5, color='#475569', ha='right', va='center')
draw_not_gate(ax, 9.2, 6.2, w=0.6, h=0.45)
ax.text(8.9, 6.2, 'Q0', fontsize=7.5, color='#475569', ha='right', va='center')
ax.text(8.9, 8.5, 'Q3', fontsize=7.5, color='#475569', ha='right', va='center')

# 4-input AND gate
draw_and_gate(ax, 10.6, 7.2, w=1.3, h=1.8, label='&')
ax.plot([9.0, 10.6], [8.5, 8.0], color='#0284c7', linewidth=1.2) # Q3 straight
ax.plot([9.9, 10.6], [7.6, 7.5], color='#0284c7', linewidth=1.2) # ~Q2
ax.plot([9.9, 10.6], [6.9, 7.0], color='#0284c7', linewidth=1.2) # ~Q1
ax.plot([9.9, 10.6], [6.2, 6.5], color='#0284c7', linewidth=1.2) # ~Q0

ax.text(12.0, 7.4, 'eq_8\n(tap_idx==8)', fontsize=7.5, color='#047857', fontweight='bold', ha='center')

# 2-input AND gate with mac_en
draw_and_gate(ax, 12.6, 7.0, w=1.1, h=1.1, label='&')
ax.plot([11.9, 12.6], [7.2, 7.3], color='#047857', linewidth=1.4)
ax.plot([12.2, 12.6], [5.0, 6.7], color='#ea580c', linewidth=1.4) # mac_en
ax.text(12.1, 5.4, 'mac_en', color='#ea580c', fontsize=7.5, fontweight='bold')

# D-FF for valid_out
draw_dff(ax, 14.2, 7.0, w=1.0, h=1.4, title='D-FF', q_label='Q', d_label='D')
ax.plot([13.7, 14.2], [7.0, 7.35], color='#059669', linewidth=1.5)
ax.plot([15.2, 15.6], [7.35, 7.35], color='#059669', linewidth=2.0)
ax.text(15.7, 7.35, 'valid_out', color='#059669', fontsize=9, fontweight='bold', va='center')
ax.plot([14.45, 14.45], [5.3, 6.3 + 0.35], color='#e11d48', linewidth=1.2) # clk to valid FF

# SECTION C: FEEDBACK CLEAR MULTIPLEXER GATE SLICE (Bit k)
box_c = patches.FancyBboxPatch((0.5, 0.4), 4.6, 4.0, boxstyle="round,pad=0.2", facecolor='#f8fafc', edgecolor='#d97706', linewidth=1.5, linestyle='--')
ax.add_patch(box_c)
ax.text(0.8, 4.15, 'C. Feedback MUX 1-Bit Gate Slice (k)', fontsize=10, fontweight='bold', color='#b45309')

ax.text(0.8, 3.7, 'Function: acc_in[k] = ~clr_acc · out_acc[k]', fontsize=7.5, color='#475569', family='monospace')
draw_not_gate(ax, 1.4, 2.7, w=0.7, h=0.45)
ax.plot([0.8, 1.4], [2.7, 2.7], color='#d97706', linewidth=1.4)
ax.text(0.7, 2.7, 'clr_acc', color='#d97706', fontsize=7.5, fontweight='bold', ha='right', va='center')

draw_and_gate(ax, 2.8, 2.3, w=1.1, h=1.1, label='&')
ax.plot([2.2, 2.8], [2.7, 2.6], color='#d97706', linewidth=1.4)
ax.plot([0.8, 2.8], [1.9, 1.9], color='#1e293b', linewidth=1.4)
ax.text(0.7, 1.9, 'out_acc[k]', color='#1e293b', fontsize=7.5, fontweight='bold', ha='right', va='center')

ax.plot([3.9, 4.7], [2.3, 2.3], color='#b45309', linewidth=1.6)
ax.text(4.8, 2.3, 'acc_in[k]', color='#b45309', fontsize=8, fontweight='bold', va='center')
ax.text(2.8, 1.1, '(Instantiated 16x for bits 0..15;\nclr_acc=1 forces acc_in=16\'sd0)', fontsize=7.5, color='#64748b', ha='center', style='italic')

# SECTION D: 16-BIT FULL ADDER CARRY CHAIN (mac_q7_8 Adder)
box_d = patches.FancyBboxPatch((5.5, 0.4), 5.4, 4.0, boxstyle="round,pad=0.2", facecolor='#f8fafc', edgecolor='#6366f1', linewidth=1.5, linestyle='--')
ax.add_patch(box_d)
ax.text(5.8, 4.15, 'D. 1-Bit Full Adder Slice (FAk in Ripple Chain)', fontsize=10, fontweight='bold', color='#4338ca')

# 1-Bit Full Adder logic gates
draw_xor_gate(ax, 6.7, 3.2, w=0.9, h=0.7, label='')
ax.text(5.6, 3.4, 'product[k+8]', fontsize=7.2, color='#1e293b', ha='left', va='center')
ax.text(5.6, 3.0, 'acc_in[k]', fontsize=7.2, color='#1e293b', ha='left', va='center')
ax.plot([6.4, 6.8], [3.4, 3.4], color='#1e293b', linewidth=1.1)
ax.plot([6.4, 6.8], [3.0, 3.0], color='#1e293b', linewidth=1.1)

draw_xor_gate(ax, 8.2, 2.9, w=0.9, h=0.7, label='')
ax.plot([7.6, 8.3], [3.2, 3.1], color='#4338ca', linewidth=1.2)
ax.plot([6.4, 8.3], [2.6, 2.7], color='#ea580c', linewidth=1.2) # Cin
ax.text(5.6, 2.6, 'Cin[k]', fontsize=7.2, color='#ea580c', ha='left', va='center')

ax.plot([9.1, 9.8], [2.9, 2.9], color='#4338ca', linewidth=1.5)
ax.text(9.9, 2.9, 'mac_result[k]', fontsize=7.5, color='#4338ca', fontweight='bold', va='center')

# Carry Out Logic
draw_and_gate(ax, 8.0, 1.7, w=0.9, h=0.7, label='&')
draw_or_gate(ax, 9.3, 1.4, w=0.9, h=0.7, label='≥1')
ax.plot([8.9, 9.4], [1.7, 1.6], color='#4338ca', linewidth=1.1)
ax.plot([10.2, 10.5], [1.4, 1.4], color='#ea580c', linewidth=1.4)
ax.text(10.1, 1.75, 'Cout[k] (to FAk+1)', fontsize=7.2, color='#ea580c', fontweight='bold', ha='center', va='bottom')

# SECTION E: TRUNCATION SLICE WIRING MAP
box_e = patches.FancyBboxPatch((11.3, 0.4), 4.2, 4.0, boxstyle="round,pad=0.2", facecolor='#f8fafc', edgecolor='#0284c7', linewidth=1.5, linestyle='--')
ax.add_patch(box_e)
ax.text(11.6, 4.15, 'E. Truncation Slice Wiring [23:8]', fontsize=10, fontweight='bold', color='#0369a1')

ax.text(11.6, 3.65, 'Product[31:0] (from 16x16 Multiplier):', fontsize=7.5, color='#334155')

# Wire map boxes
trunc_boxes = [
    ('product[31:24]', '8b Extended Int\n(Dropped - Headroom Bounded)', '#fee2e2', '#b91c1c'),
    ('product[23:8]', '16b Q7.8 Result\n(Hardwired to Adder B[15:0])', '#dbeafe', '#1d4ed8'),
    ('product[7:0]', '8b Sub-fractional\n(Truncated Floor / Dropped)', '#fef3c7', '#b45309')
]

y_tb = 3.0
for label, desc, bg, fg in trunc_boxes:
    r = patches.Rectangle((11.6, y_tb - 0.5), 3.6, 0.55, facecolor=bg, edgecolor=fg, linewidth=1.2)
    ax.add_patch(r)
    ax.text(11.75, y_tb - 0.22, label, fontsize=7.5, fontweight='bold', color=fg)
    ax.text(12.75, y_tb - 0.22, desc, fontsize=6.5, color='#334155')
    y_tb -= 0.7

ax.text(13.4, 0.8, 'Zero Combinational Gates\nPure Metal Routing / Bus Slice', fontsize=7.2, color='#0284c7', fontweight='bold', ha='center', style='italic')

# Global Axis Settings
ax.set_xlim(0, 16)
ax.set_ylim(0, 11)
ax.axis('off')

plt.tight_layout()
out_file = os.path.join(r'C:\Users\SHREYANSH RAJ\DLCD_Neural_Accelerator\docs\mini_project_submission', 'conv_pe_gate_level_diagram.png')
plt.savefig(out_file, facecolor=fig.get_facecolor(), edgecolor='none', dpi=200)
plt.close()

print('Saved gate level diagram to:', out_file)
