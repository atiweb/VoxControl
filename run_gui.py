"""
VoxControl GUI Launcher -- Double-click this to start!
(or run: python run_gui.py)
"""

import sys
import os
from pathlib import Path

# Make sure we're in the right directory
os.chdir(Path(__file__).resolve().parent)

# Launch the GUI
from src.gui.__main__ import main

if __name__ == "__main__":
    main()
