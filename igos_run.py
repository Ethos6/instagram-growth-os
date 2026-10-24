#!/usr/bin/env python3
"""Run igos without installing: python3 igos.py <command> ..."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from igos.cli import main  # noqa: E402

sys.exit(main())
