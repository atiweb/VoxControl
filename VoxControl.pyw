"""
VoxControl GUI -- Console-free Windows launcher.
Double-click this file to launch VoxControl with no terminal window.
"""

import sys
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)

from src.gui.__main__ import main

if __name__ == "__main__":
    main()
