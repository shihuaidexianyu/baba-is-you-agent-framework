#!/usr/bin/env python3
"""
Main script for playing Baba Is You.

This is a simple wrapper that imports and runs the main play module.
All command-line arguments are passed through to the play module.
"""

import sys

from baba.play import main

if __name__ == "__main__":
    sys.exit(main())
