import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GOV = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(GOV, "..", ".."))
SCEN = os.path.join(GOV, "fixtures", "graph", "scenarios")
if GOV not in sys.path:
    sys.path.insert(0, GOV)
