#!/usr/bin/env python3
"""Validates that every signal listed in all .gtkw files exists in wave.vcd header."""
import sys
import re
from pathlib import Path

def parse_vcd_signals(vcd_path):
    scope_stack = []
    signals = set()
    with open(vcd_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line.startswith("$scope"):
                parts = line.split()
                if len(parts) >= 3:
                    scope_stack.append(parts[2])
            elif line.startswith("$upscope"):
                if scope_stack:
                    scope_stack.pop()
            elif line.startswith("$var"):
                parts = line.split()
                if len(parts) >= 5:
                    var_name = parts[4]
                    full_name = ".".join(scope_stack + [var_name])
                    signals.add(full_name)
            elif line.startswith("$enddefinitions"):
                break
    return signals

def parse_gtkw_signals(gtkw_path):
    signals = []
    with open(gtkw_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(("#", "[", "*", "@", "-", "gtkwave", "GWS")):
                continue
            # Strip trailing radix or range notation
            sig = line.split()[0]
            # Strip bracket range e.g. [8:0] if attached
            base_sig = re.sub(r"\[.*?\]$", "", sig)
            signals.append((line, base_sig))
    return signals

def main():
    root = Path(__file__).resolve().parent.parent.parent.parent
    vcd_path = root / "docs/review/wave/wave.vcd"
    if not vcd_path.exists():
        print(f"Error: {vcd_path} not found.")
        sys.exit(1)
        
    vcd_signals = parse_vcd_signals(vcd_path)
    print(f"Found {len(vcd_signals)} signals in {vcd_path.name}")
    
    gtkw_files = list((root / "docs/review/wave").glob("*.gtkw"))
    all_ok = True
    
    for gtkw in gtkw_files:
        print(f"\nChecking {gtkw.name}...")
        gtkw_signals = parse_gtkw_signals(gtkw)
        missing = []
        for raw, base_sig in gtkw_signals:
            if base_sig not in vcd_signals:
                missing.append(base_sig)
        if missing:
            print(f"  FAILED: {len(missing)} missing signals in {gtkw.name}:")
            for m in missing:
                print(f"    - {m}")
            all_ok = False
        else:
            print(f"  PASSED: All {len(gtkw_signals)} signals verified in VCD header.")
            
    if all_ok:
        print("\nALL GTKWAVE SAVE FILES VERIFIED AGAINST VCD HEADER SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\nERRORS DETECTED IN GTKWAVE SIGNAL PATHS!")
        sys.exit(1)

if __name__ == "__main__":
    main()
