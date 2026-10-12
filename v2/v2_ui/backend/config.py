import os
import shutil
from pathlib import Path

# Paths
BACKEND_DIR = Path(__file__).resolve().parent
VERILOG_SRC_DIR = (BACKEND_DIR / ".." / ".." / "verilog_src").resolve()

def get_iverilog_executable() -> str:
    """Find iverilog on system PATH or fallback to standard Windows install directory."""
    path = shutil.which("iverilog")
    if path:
        return path
    win_default = r"C:\iverilog\bin\iverilog.exe"
    if os.path.exists(win_default):
        return win_default
    raise FileNotFoundError("Icarus Verilog compiler ('iverilog') was not found on PATH or at C:\\iverilog\\bin.")

def get_vvp_executable() -> str:
    """Find vvp on system PATH or fallback to standard Windows install directory."""
    path = shutil.which("vvp")
    if path:
        return path
    win_default = r"C:\iverilog\bin\vvp.exe"
    if os.path.exists(win_default):
        return win_default
    raise FileNotFoundError("Icarus Verilog runtime ('vvp') was not found on PATH or at C:\\iverilog\\bin.")
