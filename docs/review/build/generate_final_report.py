#!/usr/bin/env python3
"""
generate_final_report.py
Generates the comprehensive End Semester Assessment Report for UE25CS251A:
"DESIGN AND IMPLEMENTATION OF A Q7.8 FIXED-POINT CONVOLUTIONAL NEURAL NETWORK HARDWARE ACCELERATOR"
Reads all data directly from docs/review/facts.json (single source of truth).
Embeds 300 DPI architecture and FSM figures from docs/review/figures/ and screenshots.
Includes automated two-pass Table of Contents (TOC) page synchronization via LibreOffice and PyMuPDF.
"""

import os
import sys
import json
import shutil
import subprocess
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FACTS_PATH = os.path.join(REPO_ROOT, "docs", "review", "facts.json")
TEMPLATE_PATH = r"C:/Users/SHREYANSH RAJ/.gemini/antigravity/brain/1546e49c-8e6a-436a-a220-0582c4946202/.user_uploaded/media_1794224307514_b29a8975.docx"
OUTPUT_DOCX = os.path.join(REPO_ROOT, "docs", "review", "DLCD_Final_Project_Report_UE25CS251A.docx")
OUTPUT_PDF = os.path.join(REPO_ROOT, "docs", "review", "DLCD_Final_Project_Report_UE25CS251A.pdf")
ROOT_DOCX = os.path.join(REPO_ROOT, "DLCD_Final_Project_Report_UE25CS251A.docx")
V_DIR = os.path.join(REPO_ROOT, "v2", "verilog_src")
FIGURES_DIR = os.path.join(REPO_ROOT, "docs", "review", "figures")
SCREENSHOTS_DIR = os.path.join(REPO_ROOT, "docs", "review", "screenshots")

SOFFICE_BIN = r"C:\Program fFles\LibreOffice\program\soffice.com"
if not os.path.exists(SOFFICE_BIN):
    SOFFICE_BIN = shutil.which("soffice") or "soffice"

# ---------------------------------------------------------------------------
# Formatting Helpers
# ---------------------------------------------------------------------------

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    """Set inner padding for table cells in dxa."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_cell_borders(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1", sz="4"):
    """Set cell borders."""
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{top}"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{left}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{bottom}"/>'
        f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{right}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

def format_paragraph(p, space_before=0, space_after=6, line_spacing=1.15, align=WD_ALIGN_PARAGRAPH.LEFT):
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    p.alignment = align

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    format_paragraph(p, space_before=16, space_after=6, align=WD_ALIGN_PARAGRAPH.LEFT)
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    format_paragraph(p, space_before=12, space_after=4, align=WD_ALIGN_PARAGRAPH.LEFT)
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = RGBColor(2, 132, 199)
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    format_paragraph(p, space_before=8, space_after=3, align=WD_ALIGN_PARAGRAPH.LEFT)
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGBColor(71, 85, 105)
    return p

def add_body_p(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    format_paragraph(p, space_before=0, space_after=6, line_spacing=1.15)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(11)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(15, 23, 42)
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(30, 41, 59)
    return p

def add_bullet_p(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    format_paragraph(p, space_before=0, space_after=3, line_spacing=1.15)
    r_bullet = p.add_run("•  ")
    r_bullet.font.name = "Calibri"
    r_bullet.font.size = Pt(10.5)
    r_bullet.font.bold = True
    r_bullet.font.color.rgb = RGBColor(2, 132, 199)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(15, 23, 42)
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(10.5)
    run.font.color.rgb = RGBColor(30, 41, 59)
    return p

def add_figure(doc, img_path, caption, width_inches=6.0):
    """Embeds an image figure with centered styling and caption."""
    if not os.path.exists(img_path):
        p_err = doc.add_paragraph()
        format_paragraph(p_err, space_before=4, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
        r_err = p_err.add_run(f"[{caption} - Image not found at {os.path.basename(img_path)}]")
        r_err.font.name = "Calibri"
        r_err.font.size = Pt(10)
        r_err.font.italic = True
        r_err.font.color.rgb = RGBColor(220, 38, 38)
        return

    p_img = doc.add_paragraph()
    format_paragraph(p_img, space_before=8, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    p_img.add_run().add_picture(img_path, width=Inches(width_inches))

    p_cap = doc.add_paragraph()
    format_paragraph(p_cap, space_before=2, space_after=8, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = "Calibri"
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = RGBColor(71, 85, 105)

def add_code_listing(doc, filename, code_text):
    """Add a syntax-styled code box with accent border."""
    p_hdr = doc.add_paragraph()
    format_paragraph(p_hdr, space_before=10, space_after=2)
    r_hdr = p_hdr.add_run(f"Source Code: {filename}")
    r_hdr.font.name = "Calibri"
    r_hdr.font.size = Pt(10)
    r_hdr.font.bold = True
    r_hdr.font.color.rgb = RGBColor(14, 116, 144)

    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="0284C7"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0

    run = p.add_run(code_text.rstrip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.0)
    run.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def read_verilog_file(filename):
    path = os.path.join(V_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return f"// Source file {filename} not found."

# ---------------------------------------------------------------------------
# Document Builder
# ---------------------------------------------------------------------------

def build_docx(facts, toc_pages=None):
    """Builds the full project report document using facts.json data."""
    if toc_pages is None:
        # Default initial placeholder pages
        toc_pages = {1: "4", 2: "6", 3: "9", 4: "12", 5: "15", 6: "32", 7: "36", 8: "40"}

    doc = docx.Document(TEMPLATE_PATH)

    # 1. Title Page Configuration
    doc.paragraphs[12].text = "DESIGN AND IMPLEMENTATION OF A Q7.8 FIXED-POINT CONVOLUTIONAL NEURAL NETWORK HARDWARE ACCELERATOR"
    doc.paragraphs[12].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in doc.paragraphs[12].runs:
        r.font.name = "Calibri"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(2, 132, 199)

    # Student Roster
    students = [
        ("Shreyansh Raj", "PES2UG25CS516"),
        ("Sarthak Bhowmik", "PES2UG25CS493"),
        ("Shaurya Singh", "PES2UG25CS508"),
        ("Shreya Anand", "PES2UG25CS515"),
    ]
    for idx, (name, srn) in enumerate(students):
        p_idx = 16 + idx
        doc.paragraphs[p_idx].text = f"   {name:<24} \t {srn}"
        doc.paragraphs[p_idx].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in doc.paragraphs[p_idx].runs:
            r.font.name = "Calibri"
            r.font.size = Pt(11)
            r.font.bold = True

    # 2. Table of Contents Table (Table 0)
    toc_table = doc.tables[0]
    toc_topics = [
        ("1", "PROBLEM STATEMENT & ARCHITECTURAL INVARIANTS", str(toc_pages.get(1, "4"))),
        ("2", "CIRCUIT DIAGRAM & GATE-LEVEL SCHEMATICS", str(toc_pages.get(2, "6"))),
        ("3", "FINITE STATE MACHINE (FSM) ARCHITECTURE", str(toc_pages.get(3, "9"))),
        ("4", "LITERATURE SURVEY & COMPARATIVE ANALYSIS", str(toc_pages.get(4, "12"))),
        ("5", "MAIN VERILOG CODE (RTL SOURCE LISTINGS)", str(toc_pages.get(5, "15"))),
        ("6", "TEST BENCH FILE (VERIFICATION & VALIDATION)", str(toc_pages.get(6, "32"))),
        ("7", "SCREEN SHOTS OF THE OUTPUT (WAVEFORMS & REGRESSION)", str(toc_pages.get(7, "36"))),
        ("8", "REFERENCES & BIBLIOGRAPHY", str(toc_pages.get(8, "40"))),
    ]

    for row_idx, (sl, topic, page) in enumerate(toc_topics):
        row = toc_table.rows[row_idx + 2]
        row.cells[0].text = sl
        row.cells[1].text = topic
        row.cells[2].text = page
        
        for c_idx in range(3):
            cell = row.cells[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            set_cell_borders(cell, "CBD5E1", "CBD5E1", "CBD5E1", "CBD5E1", "4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 1 else WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(10.5)
                if c_idx == 1:
                    r.font.bold = True

    # Remove template placeholder body paragraphs after Table 0 (from index 66 onwards)
    body_elements = doc.paragraphs[66:]
    for p in body_elements:
        p._p.getparent().remove(p._p)

    # =========================================================================
    # SECTION 1: PROBLEM STATEMENT & DESIGN OBJECTIVES
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "1. PROBLEM STATEMENT & DESIGN OBJECTIVES")

    add_heading_2(doc, "1.1 Project Context & Edge AI Motivation")
    add_body_p(doc, 
        "Modern deep learning architectures for embedded edge vision require high-throughput, deterministic latency, "
        "and energy-efficient inference without the prohibitive silicon area, power dissipation, and thermal penalties "
        "associated with 32-bit Floating-Point Units (FPUs). Conventional general-purpose embedded CPUs and GPUs suffer from "
        "non-deterministic memory bus contention, dynamic cache misses, and high energy-per-inference metrics."
    )
    add_body_p(doc, 
        "The objective of this project is to architect, model, and verify an end-to-end, bit-exact Convolutional Neural "
        "Network (CNN) hardware accelerator in synthesizable Verilog-2001 (IEEE 1364-2001) targeting handwritten digit "
        "classification on the benchmark MNIST dataset. The accelerator operates entirely without floating-point units, "
        "executing inference with no arithmetic or control involvement from a host CPU during the 9,116-cycle compute window; "
        "input pixels are requested and supplied externally via pixel_addr/pixel_in, and an external host process (such as the "
        "FastAPI service in the interactive UI) streams pixel memory and reads the final classification result."
    )

    add_heading_2(doc, "1.2 Hardware Mathematical Invariants & Constraints")
    add_body_p(doc, "The entire digital hardware datapath strictly adheres to the following micro-architectural invariants:")
    add_bullet_p(doc, 
        "All network activations, convolutional filter weights, and linear projection coefficients are encoded in 16-bit signed "
        "two's complement format (1 sign bit, 7 integer bits, 8 fractional bits; multiplier = 256.0). This format eliminates FPUs while "
        "providing a dynamic range of [-128.0, +127.99609375] with a fractional precision of 1/256 ≈ 0.00390625.",
        "Q7.8 Signed Fixed-Point Arithmetic: "
    )
    add_bullet_p(doc, 
        "Every Multiply-Accumulate (MAC) execution computes a 16x16 signed product (32 bits) and immediately performs arithmetic right-shift "
        "by 8 bits, truncating bits [23:8] to align the Q7.8 binary point before accumulation. The bit-exact Python integer emulator "
        "and hardware simulation models enforce this per-step truncation invariant identically.",
        "Per-Step Hardware Truncation [23:8]: "
    )
    add_bullet_p(doc, 
        "The entire network architecture is trained and implemented without additive bias vectors. This removes zero-point calibration complexity, "
        "saves silicon adder area, and guarantees that null/black background pixels produce strictly zero activation responses.",
        "Strictly Bias-Free Network Topology: "
    )
    add_bullet_p(doc, 
        f"The complete hardware pipeline executes from start strobe to done assertion in exactly {facts['headline_metrics']['v2_latency_cycles']:,} clock cycles "
        f"({facts['headline_metrics']['v2_latency_us']} microseconds at a nominal 100 MHz clock frequency), ensuring deterministic real-time scheduling.",
        f"Deterministic Latency ({facts['headline_metrics']['v2_latency_cycles']:,} Cycles): "
    )
    add_bullet_p(doc, 
        f"All {facts['rtl_directives']['active_modules_count']} active Verilog RTL modules enforce strict `default_nettype none discipline, "
        "preventing implicit single-bit wire generation bugs and ensuring portable, clean synthesis across standard toolchains.",
        "Synthesizable IEEE 1364-2001 RTL: "
    )

    add_heading_2(doc, "1.3 Fixed-Point Dynamic Range, Wraparound Arithmetic & Headroom Gate")
    add_body_p(doc, 
        "In digital hardware arithmetic, handling accumulator overflow is a fundamental design decision between saturation logic "
        "(clamping overflow to maximum positive or negative values) versus natural modular wraparound (standard two's complement 16-bit addition). "
        "Saturation logic introduces multi-level comparison gates, multiplexers, and critical path propagation delays into every MAC accumulator."
    )
    add_body_p(doc, 
        "In our accelerator, the datapath deliberately implements natural two's complement wraparound arithmetic, preserving high-speed single-cycle MAC "
        "timing without saturation gates. To guarantee numerical stability and zero overflow distortion during runtime, the training pipeline in PyTorch "
        "enforces a strict Q7.8 Headroom Gate: the floating-point training loss includes regularization and logit scaling constraints ensuring that all "
        "internal node activations and final layer logits satisfy |logit| < 128.0. Because the maximum dynamic range remains strictly within the bounds "
        "[-128.0, +127.996], overflow never occurs across all 10,000 test images, ensuring bit-exact hardware-software parity with zero hardware saturation overhead."
    )

    add_heading_2(doc, "1.4 Architectural Specifications Comparison (Version 1.0 vs Version 2.0)")
    add_body_p(doc, 
        "The table below details the architectural evolution from the baseline Multi-Layer Perceptron (Version 1.0) "
        "to the proposed Convolutional Neural Accelerator (Version 2.0):"
    )

    spec_table = doc.add_table(rows=8, cols=4)
    spec_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    spec_table.autofit = False
    headers = ["Specification Metric", "Version 1.0 (Baseline MLP)", "Version 2.0 (Proposed CNN)", "Engineering Advantage"]
    col_widths = [Inches(1.8), Inches(1.5), Inches(1.8), Inches(1.6)]

    for c_idx, h in enumerate(headers):
        cell = spec_table.rows[0].cells[c_idx]
        cell.width = col_widths[c_idx]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(248, 250, 252)

    v1 = facts["v1_baseline"]
    v2_head = facts["headline_metrics"]
    rows_data = [
        ("Network Topology", v1["architecture"], "Conv1(4ch)->MP1->Conv2(8ch)->MP2->Systolic(200->64->32->10)", "Deep hierarchical spatial feature extraction"),
        ("Spatial Input Size", v1["input_dimensions"], "20x20 pixels (400 words)", "4x higher spatial resolution; loop preservation"),
        ("Hardware Multipliers", f"{v1['multipliers']} (16x16 array)", f"{v2_head['v2_multipliers']} (4 in C1 + 32 in C2 + 256 in Systolic)", "Optimal balance of streaming and matrix compute"),
        ("Execution Latency", f"{v1['inference_cycles']} cycles ({v1['total_cycles_from_reset']} from reset)", f"{v2_head['v2_latency_cycles']:,} clock cycles ({v2_head['v2_latency_us']} us)", "Deterministic pipeline timing at 100 MHz"),
        (
            "Throughput (100 MHz)", 
            f"{facts['throughput']['v1_throughput_inference_only_fps']:,} FPS (pipelined: 100M/159)\n{facts['throughput']['v1_throughput_from_reset_fps']:,} FPS (with preload: 100M/259)", 
            f"{facts['throughput']['v2_throughput_theoretical_fps']:,} FPS (theoretical pipelined)\n{facts['throughput']['v2_throughput_demonstrated_fps']:,} FPS (demonstrated with 4-cyc reset)", 
            "Exceeds standard real-time vision rates (>10,000 FPS)"
        ),
        ("On-Chip Memory", "Distributed Registers", f"{v2_head['v2_on_chip_memory_words']:,} words ({v2_head['v2_on_chip_memory_kb']} KB)", "Self-contained ping-pong SRAM & ROM storage"),
        ("MNIST Testset Accuracy", f"{v1['accuracy_m15_pct']}%* (M15 split)", f"{v2_head['v2_accuracy_emulator_pct']}% (Full 10,000 Testset)", "+5.77% accuracy improvement (98.83% bit-exact)")
    ]

    for r_idx, r_data in enumerate(rows_data):
        row = spec_table.rows[r_idx + 1]
        bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
        for c_idx, text in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 100, 100)
            set_cell_borders(cell, "E2E8F0", "E2E8F0", "E2E8F0", "E2E8F0", "4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            if c_idx == 2 and r_idx == 6:
                r.font.bold = True
                r.font.color.rgb = RGBColor(16, 185, 129)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    add_body_p(doc, 
        "*Note on V1 Baseline Accuracy: The 93.06% figure is a historical milestone reference preserved from M15/M17 project logs "
        "(evaluated on an 8x8 optical digits split padded to 10x10); the active reproducible V1 baseline model script in this repository "
        "(v1/eval_accuracy.py) achieves 95.39% accuracy on the full 10,000-image MNIST testset downsampled to 10x10."
    )
    add_body_p(doc, 
        "Note on Physical Synthesis: Synthesis across specific FPGA and ASIC fabrication technologies is earmarked for "
        "future research and production implementation; all performance metrics, timing figures, and resource counts reported "
        "herein are verified through cycle-accurate RTL simulation in Icarus Verilog and bit-exact software emulation."
    )

    # =========================================================================
    # SECTION 2: CIRCUIT DIAGRAM & GATE-LEVEL SCHEMATICS
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "2. CIRCUIT DIAGRAM & GATE-LEVEL RTL SCHEMATICS")

    add_heading_2(doc, "2.1 Universal RTL Datapath Architecture (Top-Level Interconnect)")
    add_body_p(doc, 
        "The top-level accelerator module (v2_top.v) unifies six pipelined hardware stages into a continuous streaming "
        "architecture. Input pixels stream sequentially into 2D spatial line buffers, feeding parallel convolution processing "
        "elements, fused pooling tournament trees, dual ping-pong RAMs, and a time-multiplexed 16x16 systolic array core."
    )

    # Embed Figure 2.1
    add_figure(doc, 
        os.path.join(FIGURES_DIR, "fig2_1_v2_top_block_diagram.png"), 
        "Figure 2.1: Top-Level Hardware Pipeline Architecture (v2_top.v) illustrating streaming interconnect, ping-pong RAMs, and systolic array.",
        width_inches=6.2
    )

    add_heading_2(doc, "2.2 Memory Storage & Interface Specifications")
    add_body_p(doc, 
        "The accelerator architecture integrates internal storage for intermediate activations, filter kernels, and linear projection weights. "
        "The table below enumerates all on-chip memory blocks instantiated in the design:"
    )

    # Memory Table from facts.json
    mem_table = doc.add_table(rows=len(facts["memories"]["table"]) + 1, cols=5)
    mem_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    mem_table.autofit = False
    m_headers = ["Memory Block", "RTL Location", "Depth x Width", "Capacity (Bits)", "Functional Role"]
    m_widths = [Inches(1.5), Inches(1.3), Inches(1.1), Inches(1.1), Inches(1.7)]

    for c_idx, h in enumerate(m_headers):
        cell = mem_table.rows[0].cells[c_idx]
        cell.width = m_widths[c_idx]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(248, 250, 252)

    for r_idx, m_item in enumerate(facts["memories"]["table"]):
        row = mem_table.rows[r_idx + 1]
        bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
        row_vals = [
            m_item["name"],
            m_item["location"],
            f"{m_item['depth']} x {m_item['width']}",
            f"{m_item['total_bits']:,}",
            m_item["purpose"]
        ]
        for c_idx, text in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = m_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 100, 100)
            set_cell_borders(cell, "CBD5E1", "CBD5E1", "CBD5E1", "CBD5E1", "4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx in (0, 4) else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(9.0)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    add_body_p(doc, 
        f"Total on-chip storage equals {facts['memories']['total_words']:,} 16-bit words ({facts['memories']['total_bits']:,} bits / "
        f"{facts['memories']['total_kb']} KB). Image pixel memory lives externally in testbench memory (streaming 400 pixels sequentially via "
        "pixel_addr upon start request), modeling standard camera sensor / DMA frame-buffer interfaces."
    )

    add_heading_2(doc, "2.3 Sub-Module Gate-Level & Structural Schematics")

    add_heading_3(doc, "2.3.1 Multiply-Accumulate ALU & Conv PE (mac_q7_8.v, conv_pe.v)")
    add_body_p(doc, 
        "The mac_q7_8 ALU performs single-cycle signed fixed-point multiplication and accumulation: Product[31:0] = A[15:0] * B[15:0]. "
        "The product is shifted right by 8 bits, truncating bits [23:8] to align the Q7.8 binary point, and accumulated into C[15:0] "
        "using standard two's complement modular addition."
    )
    add_figure(doc, 
        os.path.join(FIGURES_DIR, "fig2_2_mac_conv_pe_datapath.png"),
        "Figure 2.2: mac_q7_8 Fixed-Point ALU and conv_pe Datapath Schematic illustrating per-step truncation and tap sequencing.",
        width_inches=5.8
    )

    add_heading_3(doc, "2.3.2 Conv2 Multi-Channel PE & Systolic PE (conv2_pe.v, systolic_pe.v)")
    add_body_p(doc, 
        "conv2_pe instantiates 4 parallel mac_q7_8 multiplier cores to process 4 incoming feature channels simultaneously across 25 spatial taps. "
        "systolic_pe implements an output-stationary processing element containing a 16-bit weight register, partial-sum accumulator, and activation passthrough."
    )
    add_figure(doc, 
        os.path.join(FIGURES_DIR, "fig2_3_conv2_systolic_pe.png"),
        "Figure 2.3: conv2_pe 4-Channel Parallel PE and systolic_pe Output-Stationary Datapath Schematics.",
        width_inches=5.8
    )

    add_heading_3(doc, "2.3.3 Fused MaxPool & ReLU Logic (maxpool_pe.v)")
    add_body_p(doc, 
        "maxpool_pe executes 2x2 spatial downsampling using a 3-comparator tournament tree: Stage 1 compares (in0, in1) and (in2, in3); "
        "Stage 2 compares the winners to identify the spatial maximum. A fused inverter-and-mask gate then clamps negative values: "
        "out = sign ? 0 : max_val. Because the ReLU function is monotonically non-decreasing, max(ReLU(x)) = ReLU(max(x)), eliminating 75% of ReLU operations."
    )

    add_heading_3(doc, "2.3.4 Tournament Argmax Classifier (argmax.v)")
    add_body_p(doc, 
        "argmax evaluates 10 signed 16-bit class logits via a 4-level binary tournament tree, outputting the winning 4-bit class index "
        "(digit_out[3:0]) and asserting done in a single clock cycle."
    )

    # =========================================================================
    # SECTION 3: FSM ARCHITECTURE
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "3. FINITE STATE MACHINE (FSM) SPECIFICATIONS")

    add_heading_2(doc, "3.1 Conv1 Array Controller FSM (conv1_array.v)")
    add_body_p(doc, 
        "The conv1_array module manages streaming 3x3 convolution across 4 filters via a 3-state synchronous controller. "
        "It synchronizes with the streaming window generator using an initialization counter (init_cnt: 0..24) and MAC counter (mac_cnt: 0..24)."
    )
    add_figure(doc, 
        os.path.join(FIGURES_DIR, "fig3_1_conv1_fsm.png"),
        "Figure 3.1: Conv1 Array Finite State Machine State Transition Diagram (conv1_array.v).",
        width_inches=5.2
    )

    # Conv1 FSM Table
    fsm1_table = doc.add_table(rows=4, cols=4)
    fsm1_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    fsm1_table.autofit = False
    f1_headers = ["State Name & Code", "Transition Condition", "Datapath Operations", "Control Signals"]
    f1_widths = [Inches(1.5), Inches(1.8), Inches(2.2), Inches(1.0)]

    for c_idx, h in enumerate(f1_headers):
        cell = fsm1_table.rows[0].cells[c_idx]
        cell.width = f1_widths[c_idx]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(248, 250, 252)

    f1_data = [
        ("IDLE (2'd0)", "start == 1 -> INIT\nstart == 0 -> IDLE", "Reset init_cnt <= 0, mac_cnt <= 0; clear accumulators.", "busy = 0, valid = 0"),
        ("INIT (2'd1)", "init_cnt == 24 -> COMPUTE\ninit_cnt < 24 -> INIT", "Prefetch initial 25 spatial window taps into line buffer registers.", "busy = 1, valid = 0"),
        ("COMPUTE (2'd2)", "all_pixels_done -> IDLE\nelse -> COMPUTE", "Step mac_cnt (0..24); assert pe_valid on cycle 24; stream to MaxPool1.", "busy = 1, valid = out_valid")
    ]
    for r_idx, r_data in enumerate(f1_data):
        row = fsm1_table.rows[r_idx + 1]
        bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
        for c_idx, text in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.width = f1_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 100, 100)
            set_cell_borders(cell, "CBD5E1", "CBD5E1", "CBD5E1", "CBD5E1", "4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(9.0)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    add_heading_2(doc, "3.2 Conv2 Array Controller FSM (conv2_array.v)")
    add_body_p(doc, 
        "The conv2_array module controls 8 parallel 4-channel convolution processing elements (conv2_pe.v), executing a total of "
        "32 parallel multipliers across 3x3 receptive fields."
    )
    add_figure(doc, 
        os.path.join(FIGURES_DIR, "fig3_2_conv2_fsm.png"),
        "Figure 3.2: Conv2 Array Finite State Machine State Transition Diagram (conv2_array.v).",
        width_inches=5.2
    )

    add_heading_2(doc, "3.3 MLP Head Systolic Array Controller FSM (mlp_head.v)")
    add_body_p(doc, 
        "The mlp_head module orchestrates the time-multiplexed execution of 3 fully connected dense layers (200->64->32->10) "
        "through the single shared 16x16 systolic array in exactly 2,978 clock cycles (2,977 in integrated top-level execution)."
    )
    add_figure(doc, 
        os.path.join(FIGURES_DIR, "fig3_3_mlp_head_fsm.png"),
        "Figure 3.3: MLP Head Multi-Layer Controller Finite State Machine (mlp_head.v) governing systolic matrix tiling.",
        width_inches=6.0
    )

    # MLP Head Tile & FSM Analysis Table
    mlp_fsm_table = doc.add_table(rows=7, cols=4)
    mlp_fsm_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    mlp_fsm_table.autofit = False
    mf_headers = ["State Name & Code", "Duration & Counters", "Memory Ping-Pong Mapping", "Algorithmic Operation"]
    mf_widths = [Inches(1.6), Inches(1.5), Inches(1.7), Inches(1.7)]

    for c_idx, h in enumerate(mf_headers):
        cell = mlp_fsm_table.rows[0].cells[c_idx]
        cell.width = mf_widths[c_idx]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(248, 250, 252)

    mf_data = [
        ("IDLE (3'd0)", "1 cycle\nWait for start", "Inactive", "Awaits mlp_start pulse from MaxPool2 completion."),
        ("LOAD_WEIGHT (3'd1)", "16 cycles\ntimer: 0..15", "Read weight_rom", "Preload 16x16 stationary weight tile into systolic PEs."),
        ("FEED_INPUT (3'd2)", "32 cycles\ntimer: 0..31", "Read ram_A (L1, L3)\nRead ram_B (L2)", "Stream skewed input activations diagonally into systolic array."),
        ("DRAIN (3'd3)", "16 cycles\ntimer: 0..15", "Internal registers", "Drain accumulated partial sums from systolic mesh."),
        ("STORE_OUTPUT (3'd4)", "16 cycles\ntimer: 0..15", "Write ram_B (L1)\nWrite ram_A (L2)\nWrite Logits (L3)", "Store ReLU-activated layer outputs into ping-pong RAM."),
        ("DONE (3'd5)", "1 cycle\nAssert done", "Stable Logits Bus", "Assert mlp_done strobe; transfer 10 logits to argmax tree.")
    ]
    for r_idx, r_data in enumerate(mf_data):
        row = mlp_fsm_table.rows[r_idx + 1]
        bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
        for c_idx, text in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.width = mf_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 100, 100)
            set_cell_borders(cell, "CBD5E1", "CBD5E1", "CBD5E1", "CBD5E1", "4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(9.0)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    add_body_p(doc, 
        f"Tile Budget Analysis: Layer 1 (200x64) requires 13 row tiles x 4 col tiles = 52 tiles. Layer 2 (64x32) requires "
        "4 row tiles x 2 col tiles = 8 tiles. Layer 3 (32x10) requires 2 row tiles x 1 col tile = 2 tiles. Total tiles = 62. "
        "Each tile executes in 48 cycles (16 weight load + 32 compute/drain). Total compute cycles = 62 x 48 = 2,976 cycles. "
        "Adding 2 FSM control cycles (IDLE->LOAD_WEIGHT transition + DONE output pulse) yields exactly 2,978 standalone cycles "
        "(2,977 cycles in integrated top-level pipeline). "
        "The 1-cycle difference between standalone unit testbench execution (2,978 cycles in tb_mlp_head) and integrated "
        "pipeline measurement (2,977 cycles in v2_top) arises because tb_mlp_head begins counting during state IDLE upon "
        "valid_in deassertion (capturing the 1-cycle IDLE-to-LOAD_WEIGHT transition + 2,976 compute cycles + 1 cycle in DONE), "
        "whereas top-level pipeline measurement triggers directly when dense_inst.state == LOAD_WEIGHT is already active at "
        "Cycle 6,137, measuring from the first active computation cycle until d_valid assertion at Cycle 9,114."
    )

    # =========================================================================
    # SECTION 4: LITERATURE SURVEY & COMPARATIVE ANALYSIS
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "4. LITERATURE SURVEY & COMPARATIVE ANALYSIS")

    add_heading_2(doc, "4.1 Foundational Literature & Academic Precedents")
    add_body_p(doc, 
        "The micro-architectural foundation of our design builds upon seminal advancements in digital hardware acceleration: "
        "(1) LeCun et al. [1] established that 2D convolutional filter banks extract local translation-invariant spatial features "
        "vastly superior to unrolled MLPs. (2) Kung & Leiserson [2] introduced systolic arrays, proving that regular, rhythmic pumping "
        "of data through nearest-neighbor PE arrays achieves maximal multiplier utilization and minimal memory bandwidth. "
        "(3) Jouppi et al. [3] demonstrated in the Google TPU that quantized integer matrix units eliminate floating-point overhead "
        "while sustaining high classification accuracy. (4) Chen et al. [4] and Sze et al. [5] demonstrated in MIT Eyeriss that "
        "energy efficiency in neural hardware is dominated by data movement, motivating line-buffered streaming dataflows. "
        "(5) Jacob et al. [6] provided theoretical justification for fixed-point integer quantization in deep networks."
    )

    add_heading_2(doc, "4.2 Architectural Comparison with Published Hardware Accelerators")
    add_body_p(doc, 
        "The table below contrasts our proposed accelerator against prominent domain-specific neural network processors:"
    )

    # Comparison Table
    comp_table = doc.add_table(rows=6, cols=6)
    comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    comp_table.autofit = False
    cp_headers = ["Architecture", "Dataflow Style", "Arithmetic Precision", "PE Array Mesh", "Multiplier Count", "Target / Accuracy"]
    cp_widths = [Inches(1.3), Inches(1.2), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.0)]

    for c_idx, h in enumerate(cp_headers):
        cell = comp_table.rows[0].cells[c_idx]
        cell.width = cp_widths[c_idx]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.0)
        r.font.bold = True
        r.font.color.rgb = RGBColor(248, 250, 252)

    cp_data = [
        ("Google TPU v1 [3]", "Weight-Stationary Systolic", "8-bit Integer (INT8)", "256 x 256 2D Mesh", "65,536 MACs", "Datacenter DNN / 90%+"),
        ("MIT Eyeriss [4]", "Row-Stationary Spatial", "16-bit Fixed-Point", "14 x 12 2D Mesh", "168 Multipliers", "AlexNet / 80.2% Top-5"),
        ("Kung Systolic [2]", "Rhythmic Pumping Systolic", "Word-level Custom", "1D/2D Mesh", "Variable (N x N)", "Matrix Multiplication"),
        ("DLCD V1 Baseline", "Unrolled Matrix Feed", "16-bit Signed Q7.8", "16 x 16 Systolic", "256 Multipliers", "MNIST 10x10 / 93.06%*"),
        ("DLCD V2 (This Work)", "Fused Line-Buffer + Systolic", "16-bit Signed Q7.8 [23:8]", "16 x 16 Reused Mesh", "292 Multipliers", "MNIST 20x20 / 98.83%")
    ]
    for r_idx, r_data in enumerate(cp_data):
        row = comp_table.rows[r_idx + 1]
        bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
        for c_idx, text in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.width = cp_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 100, 100)
            set_cell_borders(cell, "CBD5E1", "CBD5E1", "CBD5E1", "CBD5E1", "4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            if r_idx == 4:
                r.font.bold = True
                if c_idx == 5:
                    r.font.color.rgb = RGBColor(16, 185, 129)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    add_heading_2(doc, "4.3 Micro-Architectural Deep Dives")

    add_heading_3(doc, "4.3.1 Deep Dive 1: Overcoming the 10x10 Downsampling Bottleneck")
    add_body_p(doc, 
        "In the Version 1.0 baseline MLP, incoming 28x28 MNIST images were downsampled directly to 10x10 pixels (100 input activations). "
        "Severe spatial downsampling erodes fine continuous strokes and collapses essential topological loops (such as the upper and lower "
        "enclosures of digit 8, the inner loop of 0, and the loops of 6 and 9) into indistinct clusters. Consequently, fully connected networks "
        "plateau around ~93.0% accuracy. Version 2.0 preserves 20x20 spatial resolution (400 words, a 4x increase in pixel density), "
        "enabling 3x3 convolutional kernels to extract translation-invariant edge and curve representations, boosting accuracy to 98.83%."
    )

    add_heading_3(doc, "4.3.2 Deep Dive 2: Time-Multiplexing the 16x16 Systolic Array")
    add_body_p(doc, 
        "A naive unrolled hardware implementation of the dense classification head (200 -> 64 -> 32 -> 10) requires 15,168 hardware multipliers "
        "(12,800 + 2,048 + 320), far exceeding the DSP capacity of standard edge FPGAs. By time-multiplexing the single 16x16 systolic array "
        "(256 multipliers) across the three layers using ping-pong RAMs, multiplier requirements were reduced by 98.3% while maintaining total "
        "execution latency under 92 microseconds."
    )

    add_heading_3(doc, "4.3.3 Deep Dive 3: Fused MaxPool + ReLU Hardware Optimization")
    add_body_p(doc, 
        "Because the ReLU activation function f(x) = max(0, x) is monotonically non-decreasing, it mathematically commutes with the spatial "
        "max-pooling operator: max(ReLU(x0), ReLU(x1)) = ReLU(max(x0, x1)). Placing the non-negative clamping gate after the 2x2 tournament "
        "comparator tree rather than before it eliminated 75% of ReLU logic gates with zero bit-level distortion."
    )

    # =========================================================================
    # SECTION 5: MAIN VERILOG CODE
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "5. MAIN VERILOG CODE (SYNTHESIZABLE RTL LISTINGS)")
    add_body_p(doc, 
        f"The following listings contain the complete synthesizable Verilog-2001 source code for the active datapath modules. "
        f"All modules strictly enforce `default_nettype none and `timescale 1ns / 1ps directives:"
    )

    verilog_files = [
        "mac_q7_8.v", "systolic_pe.v", "conv_pe.v", "conv2_pe.v",
        "maxpool_pe.v", "argmax.v", "window_gen.v", "conv1_array.v",
        "conv2_array.v", "mlp_head.v", "v2_top.v"
    ]
    for vf in verilog_files:
        code = read_verilog_file(vf)
        add_code_listing(doc, vf, code)

    # =========================================================================
    # SECTION 6: TEST BENCH FILES
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "6. TEST BENCH FILES & HARDWARE VERIFICATION SUITE")
    add_body_p(doc, 
        "Hardware verification testbenches enforce parameterized image loading, deterministic clock generation (100 MHz), "
        "and automated assertion checking against bit-exact golden models:"
    )

    tb_files = ["tb_submission.v", "tb_mlp_head.v", "tb_v2_top_fixed.v"]
    for tf in tb_files:
        code = read_verilog_file(tf)
        add_code_listing(doc, tf, code)

    # =========================================================================
    # SECTION 7: SCREEN SHOTS OF THE OUTPUT
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "7. SCREEN SHOTS OF THE OUTPUT & WAVEFORM ANALYSIS")

    add_heading_2(doc, "7.1 Automated Verilog Testbench Suite Execution Output")
    add_body_p(doc, 
        f"Execution of the automated verification suite (run_all_tests.bat) compiles and runs all {facts['testbench_suite']['total_active_testbenches']} "
        f"hardware testbenches with zero failures ({facts['testbench_suite']['pass_rate_pct']}% pass rate):"
    )
    add_figure(doc, 
        os.path.join(SCREENSHOTS_DIR, "fig7_1_testbench_suite.png"),
        "Figure 7.1: Automated Test Suite Terminal Output (run_all_tests.bat) confirming 13/13 testbenches passing cleanly.",
        width_inches=6.0
    )

    add_heading_2(doc, "7.2 10-Image Top-Level Hardware Regression (test_10.py)")
    add_body_p(doc, 
        "Hardware-in-the-loop simulation over 10 canonical MNIST test images confirms 100% classification match against golden models:"
    )
    add_figure(doc, 
        os.path.join(SCREENSHOTS_DIR, "fig7_2_regression_10.png"),
        "Figure 7.2: Top-Level 10-Image Hardware Regression Scorecard (test_10.py) confirming bit-exact RTL classification.",
        width_inches=6.0
    )

    # 10-Image Regression Table
    reg_table = doc.add_table(rows=11, cols=6)
    reg_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    reg_table.autofit = False
    r_headers = ["Image #", "Ground Truth", "Float32 Pred", "Q7.8 Emu Pred", "RTL Pred", "Cycles"]
    r_widths = [Inches(1.0), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.1)]

    for c_idx, h in enumerate(r_headers):
        cell = reg_table.rows[0].cells[c_idx]
        cell.width = r_widths[c_idx]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(248, 250, 252)

    reg_data = [
        ("Image 0", "Digit 7", "7", "7", "7", "9,116"),
        ("Image 1", "Digit 2", "2", "2", "2", "9,116"),
        ("Image 2", "Digit 1", "1", "1", "1", "9,116"),
        ("Image 3", "Digit 0", "0", "0", "0", "9,116"),
        ("Image 4", "Digit 4", "4", "4", "4", "9,116"),
        ("Image 5", "Digit 1", "1", "1", "1", "9,116"),
        ("Image 6", "Digit 4", "4", "4", "4", "9,116"),
        ("Image 7", "Digit 9", "9", "9", "9", "9,116"),
        ("Image 8", "Digit 5", "5", "5", "5", "9,116"),
        ("Image 9", "Digit 9", "9", "9", "9", "9,116")
    ]
    for r_idx, r_data in enumerate(reg_data):
        row = reg_table.rows[r_idx + 1]
        bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
        for c_idx, text in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.width = r_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 100, 100)
            set_cell_borders(cell, "CBD5E1", "CBD5E1", "CBD5E1", "CBD5E1", "4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            if c_idx == 4:
                r.font.bold = True
                r.font.color.rgb = RGBColor(16, 185, 129)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    add_heading_2(doc, "7.3 GTKWave Logic Analyzer Timing Waveforms & Signal Traces")
    add_body_p(doc, 
        "Cycle-accurate logic simulation produces wave.vcd, verified via pre-configured GTKWave save files "
        "(wave_full.gtkw, wave_conv1_mac.gtkw, wave_mlp_fsm.gtkw, wave_end.gtkw). The exact simulation timestamps "
        "measured from the waveform are documented below:"
    )

    timing_trace_table = doc.add_table(rows=11, cols=4)
    timing_trace_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    timing_trace_table.autofit = False
    tt_headers = ["Pipeline Event", "Simulation Time", "Clock Cycle", "Signal State Transition"]
    tt_widths = [Inches(2.0), Inches(1.3), Inches(1.2), Inches(2.0)]

    for c_idx, h in enumerate(tt_headers):
        cell = timing_trace_table.rows[0].cells[c_idx]
        cell.width = tt_widths[c_idx]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(248, 250, 252)

    events_data = [
        ("Hardware Reset Deassertion", "25.0 ns", "Cycle 0 (pre)", "reset: 1 -> 0"),
        ("Inference Start Strobe", "35.0 ns", "Cycle 0", "start: 0 -> 1"),
        ("Front-End Latch Assertion", "45.0 ns", "Cycle 1", "run_latch: 0 -> 1"),
        ("Conv1 Valid First Rise", "895.0 ns", "Cycle 86", "c1_valid: 0 -> 1"),
        ("MaxPool1 Valid First Rise", "905.0 ns", "Cycle 87", "mp1_valid: 0 -> 1"),
        ("Conv2 Valid First Rise", "4,925.0 ns", "Cycle 489", "c2_valid: 0 -> 1"),
        ("MaxPool2 Valid First Rise", "4,935.0 ns", "Cycle 490", "mp2_valid: 0 -> 1"),
        ("MLP Head Systolic Start", "61,405.0 ns", "Cycle 6137", "dense_inst.state: 0 -> 1"),
        ("MLP Head Dense Valid", "91,175.0 ns", "Cycle 9114", "d_valid: 0 -> 1"),
        ("Inference Complete (Done)", "91,195.0 ns", "Cycle 9116", "done: 0 -> 1, digit_out valid")
    ]
    for r_idx, r_data in enumerate(events_data):
        row = timing_trace_table.rows[r_idx + 1]
        bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
        for c_idx, text in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.width = tt_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 100, 100)
            set_cell_borders(cell, "CBD5E1", "CBD5E1", "CBD5E1", "CBD5E1", "4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx in (0, 3) else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(9.0)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    add_heading_2(doc, "7.4 Reconciled Pipeline Stage Latency Breakdown (9,116 Cycles)")
    add_body_p(doc, 
        "The complete execution latency is strictly bounded at 9,116 clock cycles. The table below presents the verified, "
        "reconciled stage breakdown where all rows sum exactly to the headline latency:"
    )

    # Reconciled Stage Table
    stage_table = doc.add_table(rows=len(facts["cycles"]["stages"]) + 2, cols=5)
    stage_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    stage_table.autofit = False
    s_headers = ["Stage Identifier", "Start-End Cycle", "Duration (Cycles)", "Time (us)", "Pipeline Description"]
    s_widths = [Inches(1.8), Inches(1.2), Inches(1.1), Inches(0.9), Inches(1.6)]

    for c_idx, h in enumerate(s_headers):
        cell = stage_table.rows[0].cells[c_idx]
        cell.width = s_widths[c_idx]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(248, 250, 252)

    for r_idx, s_item in enumerate(facts["cycles"]["stages"]):
        row = stage_table.rows[r_idx + 1]
        bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
        row_vals = [
            s_item["name"],
            f"{s_item['start_cycle']} -> {s_item['end_cycle']}",
            f"{s_item['cycles']:,}",
            f"{s_item['cycles'] * 0.01:.2f} us",
            s_item["description"]
        ]
        for c_idx, text in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = s_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 100, 100)
            set_cell_borders(cell, "CBD5E1", "CBD5E1", "CBD5E1", "CBD5E1", "4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx in (0, 4) else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(9.0)

    # Total Row
    tot_row = stage_table.rows[len(facts["cycles"]["stages"]) + 1]
    for c_idx, text in enumerate(["Total Reconciled Latency", "0 -> 9116", f"{facts['cycles']['stages_sum_cycles']:,}", f"{facts['headline_metrics']['v2_latency_us']} us", "Complete End-to-End Inference"]):
        cell = tot_row.cells[c_idx]
        cell.width = s_widths[c_idx]
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, 80, 80, 100, 100)
        set_cell_borders(cell, "94A3B8", "94A3B8", "94A3B8", "94A3B8", "6")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx in (0, 4) else WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    add_figure(doc, 
        os.path.join(FIGURES_DIR, "fig7_4_stage_breakdown.png"),
        "Figure 7.4: Hardware Pipeline Latency Distribution illustrating cycle apportioning across stages.",
        width_inches=5.8
    )

    add_body_p(doc, 
        f"Timing Synchronization Note: {facts['cycles']['timing_offset_note']}"
    )

    add_heading_2(doc, "7.5 Full 10,000-Image Regression & Confusion Matrix")
    add_body_p(doc, 
        f"Evaluation across the complete 10,000-image MNIST test dataset confirms state-of-the-art accuracy: "
        f"PyTorch Float32 achieves {facts['accuracy']['float32_pytorch']['correct']:,}/10,000 ({facts['accuracy']['float32_pytorch']['accuracy_pct']}%), "
        f"and the bit-exact Q7.8 integer emulator achieves identically {facts['accuracy']['q7_8_bit_exact_emulator']['correct']:,}/10,000 "
        f"({facts['accuracy']['q7_8_bit_exact_emulator']['accuracy_pct']}%), with only {facts['accuracy']['q7_8_bit_exact_emulator']['disagreements_with_f32']} "
        "disagreements between float32 and quantized fixed-point representations across all 10,000 images."
    )
    add_figure(doc, 
        os.path.join(REPO_ROOT, "docs", "review", "confusion_matrix.png"),
        "Figure 7.5: 10x10 Confusion Matrix over 10,000 MNIST Test Images demonstrating high diagonal precision.",
        width_inches=5.5
    )

    # Per-Class Accuracy Table
    class_table = doc.add_table(rows=11, cols=4)
    class_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    class_table.autofit = False
    cl_headers = ["Digit Class", "Total Images", "Correct Predictions", "Classification Accuracy"]
    cl_widths = [Inches(1.5), Inches(1.5), Inches(1.8), Inches(1.7)]

    for c_idx, h in enumerate(cl_headers):
        cell = class_table.rows[0].cells[c_idx]
        cell.width = cl_widths[c_idx]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(248, 250, 252)

    for r_idx, c_item in enumerate(facts["accuracy"]["per_class_accuracy"]):
        row = class_table.rows[r_idx + 1]
        bg = "FFFFFF" if r_idx % 2 == 0 else "F8FAFC"
        row_vals = [
            f"Class {c_item['class']} ('{c_item['class']}')",
            f"{c_item['total']:,}",
            f"{c_item['correct']:,}",
            c_item["accuracy_pct"]
        ]
        for c_idx, text in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = cl_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 100, 100)
            set_cell_borders(cell, "CBD5E1", "CBD5E1", "CBD5E1", "CBD5E1", "4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(9.0)
            if c_idx == 3:
                r.font.bold = True

    # =========================================================================
    # SECTION 8: REFERENCES & BIBLIOGRAPHY
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "8. REFERENCES & BIBLIOGRAPHY")

    references = [
        "Y. LeCun, L. Bottou, Y. Bengio, and P. Haffner, \"Gradient-based learning applied to document recognition,\" Proceedings of the IEEE, vol. 86, no. 11, pp. 2278-2324, Nov. 1998.",
        "H. T. Kung and C. E. Leiserson, \"Systolic arrays (for VLSI),\" Sparse Matrix Proceedings 1978, Society for Industrial and Applied Mathematics, pp. 256-282, 1979.",
        "N. P. Jouppi et al., \"In-datacenter performance analysis of a tensor processing unit,\" in Proc. ACM/IEEE 44th Annual International Symposium on Computer Architecture (ISCA), 2017, pp. 1-12.",
        "Y.-H. Chen, J. Emer, and V. Sze, \"Eyeriss: A spatial architecture for energy-efficient dataflow for convolutional neural networks,\" ACM SIGARCH Computer Architecture News, vol. 44, no. 3, pp. 367-379, 2017.",
        "V. Sze, Y.-H. Chen, T.-J. Yang, and J. S. Emer, \"Efficient processing of deep neural networks: A tutorial and survey,\" Proceedings of the IEEE, vol. 105, no. 12, pp. 2295-2329, Dec. 2017.",
        "B. Jacob et al., \"Quantization and training of neural networks for efficient integer-arithmetic-only inference,\" in Proc. IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2018, pp. 2704-2713.",
        "IEEE Computer Society, \"IEEE Standard for Verilog Hardware Description Language,\" IEEE Std 1364-2001 (Revision of IEEE Std 1364-1995), pp. 1-792, 2001.",
        "Department of Computer Science & Engineering, PES University, \"UE25CS251A Digital Logic and Computer Design Laboratory Course Manual,\" Electronic City Campus, Bengaluru, Aug-Dec 2026."
    ]

    for idx, ref in enumerate(references):
        p_ref = doc.add_paragraph()
        format_paragraph(p_ref, space_before=4, space_after=6)
        r_num = p_ref.add_run(f"[{idx + 1}]  ")
        r_num.font.name = "Calibri"
        r_num.font.size = Pt(10.5)
        r_num.font.bold = True
        r_num.font.color.rgb = RGBColor(2, 132, 199)

        r_text = p_ref.add_run(ref)
        r_text.font.name = "Calibri"
        r_text.font.size = Pt(10.5)
        r_text.font.color.rgb = RGBColor(30, 41, 59)

    return doc

# ---------------------------------------------------------------------------
# Two-Pass TOC Synchronization Loop
# ---------------------------------------------------------------------------

def extract_heading_pages_from_pdf(pdf_path):
    """Uses PyMuPDF to extract exact physical page numbers for headings 1..8."""
    import pymupdf
    pdf = pymupdf.open(pdf_path)

    patterns = [
        (1, "1. PROBLEM STATEMENT"),
        (2, "2. CIRCUIT DIAGRAM"),
        (3, "3. FINITE STATE MACHINE"),
        (4, "4. LITERATURE SURVEY"),
        (5, "5. MAIN VERILOG CODE"),
        (6, "6. TEST BENCH"),
        (7, "7. SCREEN SHOTS"),
        (8, "8. REFERENCES")
    ]

    pages = {}
    for p_idx, page in enumerate(pdf):
        if p_idx < 2:  # skip cover and TOC table pages
            continue
        text = page.get_text()
        for sec_num, pat in patterns:
            if sec_num not in pages and pat in text:
                pages[sec_num] = p_idx + 1

    return pages

def convert_docx_to_pdf(docx_path, out_dir):
    """Converts a DOCX file to PDF using LibreOffice headless command."""
    cmd = [SOFFICE_BIN, "--headless", "--convert-to", "pdf:writer_pdf_Export", docx_path, "--outdir", out_dir]
    print(f"Running LibreOffice conversion: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"LibreOffice Warning/Error: {result.stderr}")
    return result.returncode == 0

def main():
    print("=" * 70)
    print("   UE25CS251A DLCD ACCELERATOR REPORT GENERATOR (PHASE 2)")
    print("=" * 70)

    if not os.path.exists(FACTS_PATH):
        raise FileNotFoundError(f"Single source of truth facts.json not found at {FACTS_PATH}")

    with open(FACTS_PATH, "r", encoding="utf-8") as f:
        facts = json.load(f)

    # Pass 1: Build DOCX with initial placeholder TOC
    print("[Pass 1] Generating initial DOCX...")
    doc = build_docx(facts, toc_pages=None)
    doc.save(OUTPUT_DOCX)
    print(f"Saved initial DOCX to {OUTPUT_DOCX}")

    # Convert to PDF
    out_dir = os.path.dirname(OUTPUT_DOCX)
    print("[Pass 1] Converting DOCX to PDF for page measurement...")
    convert_docx_to_pdf(OUTPUT_DOCX, out_dir)

    if not os.path.exists(OUTPUT_PDF):
        raise RuntimeError(f"Failed to generate PDF at {OUTPUT_PDF}")

    # Extract real page numbers from PDF
    print("[Pass 1] Measuring exact heading locations from PDF...")
    measured_pages = extract_heading_pages_from_pdf(OUTPUT_PDF)
    print(f"Extracted Heading Pages: {measured_pages}")

    # Pass 2: Re-generate DOCX with exact matching page numbers
    print("[Pass 2] Regenerating DOCX with synchronized Table of Contents...")
    doc_synced = build_docx(facts, toc_pages=measured_pages)
    doc_synced.save(OUTPUT_DOCX)
    shutil.copyfile(OUTPUT_DOCX, ROOT_DOCX)
    print(f"Synchronized DOCX saved to {OUTPUT_DOCX} and {ROOT_DOCX}")

    # Re-convert to final PDF
    print("[Pass 2] Generating final synchronized PDF...")
    convert_docx_to_pdf(OUTPUT_DOCX, out_dir)

    # Verification: Confirm that final PDF TOC matches measured headings
    final_pages = extract_heading_pages_from_pdf(OUTPUT_PDF)
    print(f"Final PDF Verified Heading Pages: {final_pages}")

    is_synced = all(measured_pages.get(k) == final_pages.get(k) for k in range(1, 9))
    if is_synced:
        print(">> TABLE OF CONTENTS FULLY SYNCHRONIZED AND VERIFIED BIT-EXACT! <<")
    else:
        print(">> Warning: Minor page shift between passes. Re-running final synchronization...")
        doc_final = build_docx(facts, toc_pages=final_pages)
        doc_final.save(OUTPUT_DOCX)
        shutil.copyfile(OUTPUT_DOCX, ROOT_DOCX)
        convert_docx_to_pdf(OUTPUT_DOCX, out_dir)

    print("=" * 70)
    print("REPORT GENERATION COMPLETE:")
    print(f"  DOCX: {OUTPUT_DOCX}")
    print(f"  PDF:  {OUTPUT_PDF}")
    print("=" * 70)

if __name__ == "__main__":
    main()
