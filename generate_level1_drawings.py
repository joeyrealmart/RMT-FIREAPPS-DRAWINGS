import ezdxf
import svgwrite
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
import math

doc = ezdxf.readfile('AVILLION Riou.dxf')
msp = doc.modelspace()

# Get all MIMIC_SIZE entities in L1 region (-2000 <= X <= -1100, 600 <= Y <= 1050)
mimic_l1 = []
for e in msp:
    if e.dxf.layer == 'MIMIC_SIZE':
        pts = []
        if e.dxftype() == 'LINE': pts = [e.dxf.start, e.dxf.end]
        elif e.dxftype() in ('TEXT', 'CIRCLE', 'INSERT', 'ARC'): pts = [e.dxf.insert if hasattr(e.dxf, 'insert') else e.dxf.center]
        elif e.dxftype() == 'POLYLINE': pts = [v.dxf.location for v in e.vertices]
        if any(-2100 <= p[0] <= -1000 and 600 <= p[1] <= 1050 for p in pts):
            mimic_l1.append(e)

print(f"MIMIC_SIZE Level 1 entities count: {len(mimic_l1)}")

# Get detailed CAD floorplan entities in L1 region (-3300 <= X <= -2700, -1350 <= Y <= -1100)
cad_l1 = []
for e in msp:
    pts = []
    if e.dxftype() == 'LINE': pts = [e.dxf.start, e.dxf.end]
    elif e.dxftype() in ('TEXT', 'CIRCLE', 'INSERT', 'ARC'): pts = [e.dxf.insert if hasattr(e.dxf, 'insert') else e.dxf.center]
    elif e.dxftype() == 'POLYLINE': pts = [v.dxf.location for v in e.vertices]
    if any(-3300 <= p[0] <= -2700 and -1350 <= p[1] <= -1090 for p in pts):
        cad_l1.append(e)

print(f"CAD Level 1 entities count: {len(cad_l1)}")

# Let's inspect layers in cad_l1
from collections import Counter
print("CAD L1 layers:", Counter(e.dxf.layer for e in cad_l1))
