"""Local CI quality gate for the V4 project."""
from pathlib import Path
import compileall, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
if not compileall.compile_dir(str(ROOT/"backend/app"), quiet=1):
    raise SystemExit("Python compilation failed")
p=subprocess.run([sys.executable,"-m","pytest","-q","backend/tests"],cwd=ROOT)
if p.returncode:
    raise SystemExit(p.returncode)
print("QUALITY GATE PASSED")
