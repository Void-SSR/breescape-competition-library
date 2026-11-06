# coding: utf-8
"""Replay v1.2 targeted judgments from the sealed submitted v1.1 snapshot.
The original v1.1 replay script is preserved inside the snapshot with its hash.
"""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().with_name('targeted_patch_v1_2.py')), run_name='__main__')
