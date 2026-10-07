#!/usr/bin/env python3
"""
Script de compilation PyInstaller pour Melodi Process Manager.
"""
import sys
import shutil
import subprocess
from pathlib import Path

def build():
    root_dir = Path(__file__).resolve().parent
    print(f"Building melodi_process_manager from {root_dir}...")

    # Nettoyage
    for folder in ("build", "dist"):
        p = root_dir / folder
        if p.exists():
            shutil.rmtree(p)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        str(root_dir / "melodi_process_manager.spec")
    ]
    print(f"Executing: {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=root_dir)
    print("Build successful! Executable is in dist/melodi_process_manager")

if __name__ == "__main__":
    build()
