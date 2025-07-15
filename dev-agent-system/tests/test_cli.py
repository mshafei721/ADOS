#!/usr/bin/env python3
"""
Simple test for the CLI
"""

import sys
from pathlib import Path

# Add the current directory to the path so we can import runner
sys.path.insert(0, str(Path(__file__).parent))

from runner.main import cli_main

if __name__ == "__main__":
    cli_main()