# -*- coding: utf-8 -*-
"""
Initialisation for crossword hints controller
"""

import os
import glob

__all__ = [
    os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py")
]
