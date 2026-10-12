import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

vcd_file = r'v2/verilog_src/tb_conv_pe.vcd'

# Signal mapping
signals = {
    'clk': '#',
    'reset': '*',
    'load_weight': '\'',
    'mac_en': '(',
    'clr_acc': '$',
    'pixel_in': ')',
    'tap_idx': '3',
    'current_weight': '-',
    'mac_result': '0',
    'out_acc': '2',
    'valid_out': '!'
}
inv_map = {v: k for k, v in signals.items()}

# Parse events
events = {k: [] for k in signals}
with open(vcd_file, 'r') as f:
    cur_time = 0
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            cur_time = int(line[1:]) // 1000  # ns
        elif line.startswith('$'):
            continue
        else:
            if line[0] in ['0', '1', 'x', 'z']:
                val = line[0]
                sym = line[1:]
                if sym in inv_map:
                    events[inv_map[sym]].append((cur_time, int(val) if val in ['0', '1'] else 0))
            elif line.startswith('b'):
                parts = line.split()
                val_bin = parts[0][1:]
                sym = parts[1]
                if sym in inv_map:
                    try:
                        val_int = int(val_bin, 2)
                        if len(val_bin) == 16 and val_bin[0] == '1':
                            val_int -= 65536
                        events[inv_map[sym]].append((cur_time, val_int))
                    except ValueError:
                        events[inv_map[sym]].append((cur_time, 0))

# Window of interest: t = 115 ns to 345 ns (covers full Window 1 + Window 2 + handoffs)
t_start = 115
t_end = 345

# Signals to display in waveform order
display_sigs = [
    ('clk', False),
    ('mac_en', False),
    ('clr_acc', False),
    ('pixel_in [15:0]', True, 'pixel_in'),
    ('tap_idx [3:0]', True, 'tap_idx'),
    ('current_weight [15:0]', True, 'current_weight'),
    ('mac_result [15:0]', True, 'mac_result'),
    ('out_acc [15:0]', True, 'out_acc'),
    ('valid_out', False)
]

fig, ax = plt.subplots(figsize=(15, 8.5), dpi=200)
fig.patch.set_facecolor('#12161f')
ax.set_facecolor('#12161f')

y_step = 1.3
total_sigs = len(display_sigs)

# Grid lines for clock cycles
for t in range(t_start, t_end + 1, 10):
    ax.axvline(t, color='#232a3b', linestyle='--', linewidth=0.8, alpha=0.7)

# Highlight active windows
ax.axvspan(135, 225, color='#1e3a5f', alpha=0.25, label='Window 1 (Interior)')
ax.axvspan(235, 325, color='#2c3e50', alpha=0.25, label='Window 2 (Edge / Pad)')

for idx, sig_info in enumerate(display_sigs):
    sig_name = sig_info[0]
    is_bus = sig_info[1]
    raw_key = sig_info[2] if is_bus else sig_name
    y_base = (total_sigs - 1 - idx) * y_step

    ev_list = events[raw_key]
    # Build continuous state
    times = []
    vals = []
    
    # Initial state before t_start
    last_val = 0
    for t_ev, v_ev in ev_list:
        if t_ev <= t_start:
            last_val = v_ev
        else:
            break
            
    filtered = [(t_ev, v_ev) for t_ev, v_ev in ev_list if t_start <= t_ev <= t_end]
    all_evs = [(t_start, last_val)] + filtered + [(t_end, filtered[-1][1] if filtered else last_val)]

    if not is_bus:
        # 1-bit digital trace
        x_pts = []
        y_pts = []
        for i in range(len(all_evs) - 1):
            t0, v0 = all_evs[i]
            t1, _ = all_evs[i + 1]
            x_pts.extend([t0, t1])
            y_pts.extend([y_base + (0.75 if v0 else 0.05), y_base + (0.75 if v0 else 0.05)])
            
        color = '#00e676' if sig_name != 'valid_out' else '#ff3d00'
        ax.plot(x_pts, y_pts, color=color, linewidth=1.6)
        # Glow effect
        ax.plot(x_pts, y_pts, color=color, linewidth=3.2, alpha=0.25)
    else:
        # Multibit Bus with hex/dec boxes
        for i in range(len(all_evs) - 1):
            t0, v0 = all_evs[i]
            t1, _ = all_evs[i + 1]
            if t1 <= t0:
                continue
            # Draw bus envelope
            dt = min(1.0, (t1 - t0) * 0.15)
            pts = [
                [t0, y_base + 0.4],
                [t0 + dt, y_base + 0.75],
                [t1 - dt, y_base + 0.75],
                [t1, y_base + 0.4],
                [t1 - dt, y_base + 0.05],
                [t0 + dt, y_base + 0.05]
            ]
            poly = patches.Polygon(pts, closed=True, facecolor='#1e293b', edgecolor='#38bdf8', linewidth=1.2)
            ax.add_patch(poly)
            
            # Text label inside bus
            if (t1 - t0) >= 7:
                text_str = f'{v0}'
                if raw_key in ['pixel_in', 'out_acc', 'mac_result'] and abs(v0) > 0:
                    text_str = f'{v0}'
                ax.text((t0 + t1) / 2.0, y_base + 0.4, text_str, color='#f8fafc',
                        fontsize=7.2, fontweight='bold', ha='center', va='center', family='monospace')

    # Label on left axis
    label_color = '#38bdf8' if is_bus else ('#ff3d00' if sig_name == 'valid_out' else '#00e676')
    ax.text(t_start - 2, y_base + 0.4, sig_name, color=label_color,
            fontsize=9.5, fontweight='bold', ha='right', va='center', family='monospace')

# Formatting
ax.set_xlim(t_start - 35, t_end + 5)
ax.set_ylim(-0.3, total_sigs * y_step + 0.2)
ax.set_xlabel('Simulation Time (ns) [Clock Period = 10ns]', color='#94a3b8', fontsize=10.5, labelpad=8)
ax.set_title('GTKWave Logic Simulation Trace: tb_conv_pe.v (Window 1 Interior & Window 2 Edge Verification)',
             color='#f1f5f9', fontsize=12.5, fontweight='bold', pad=12)

# X ticks every 10 ns
ticks = list(range(120, t_end + 1, 10))
ax.set_xticks(ticks)
ax.set_xticklabels([f'{t}' for t in ticks], color='#94a3b8', fontsize=8.5)
ax.tick_params(axis='x', colors='#64748b')
ax.set_yticks([])

# Watermark / Subtitle
ax.text((t_start + t_end) / 2.0, total_sigs * y_step - 0.1,
        'Window 1 Completion: out_acc=104, valid_out=1 pulse  |  Window 2 Completion: out_acc=19, valid_out=1 pulse',
        color='#38bdf8', fontsize=9.5, ha='center', va='center', style='italic')

# Frame aesthetic
for spine in ax.spines.values():
    spine.set_color('#334155')

plt.tight_layout()
out_png = os.path.join(r'C:\Users\SHREYANSH RAJ\DLCD_Neural_Accelerator\docs\mini_project_submission', 'conv_pe_waveform.png')
plt.savefig(out_png, facecolor=fig.get_facecolor(), edgecolor='none', dpi=200)
plt.close()

print('Saved waveform image successfully to:', out_png)
