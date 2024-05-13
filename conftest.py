import sys
import os

# Get the absolute path to the 'src' directory
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add 'src' to the Python path
sys.path.insert(0, src_dir)
