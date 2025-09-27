#!/usr/bin/env python3
"""
Convenience script to run the main analysis from any directory.
This handles the path setup automatically.
"""

import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent
core_analysis_dir = project_root / "core_analysis"

# Add core_analysis to Python path
sys.path.insert(0, str(core_analysis_dir))

# Change to core_analysis directory 
os.chdir(core_analysis_dir)

# Import and run the main analysis
if __name__ == "__main__":
    # Import the main script
    import Minuit_main
    
    print(f"Running analysis from: {os.getcwd()}")
    print("Analysis complete!")
