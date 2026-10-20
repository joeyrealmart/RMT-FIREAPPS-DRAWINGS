import ezdxf

doc = ezdxf.readfile('AVILLION Riou.dxf')
msp = doc.modelspace()

top_entities = [e for e in msp if e.dxf.layer == 'MIMIC_SIZE' and any(-2100 <= p[0] <= -1000 and 600 <= p[1] <= 1050 for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices]))]

# Find horizontal and vertical lines in top_entities
lines = [e for e in top_entities if e.dxftype() == 'LINE']
print(f"Top lines count: {len(lines)}")

# Let's check Y coordinates of top lines
y_coords = sorted(list(set(round(e.dxf.start[1], 1) for e in lines) | set(round(e.dxf.end[1], 1) for e in lines)))
print("Top line Y coords (sample):", y_coords[:10], "...", y_coords[-10:])

# Let's check X coordinates of top lines
x_coords = sorted(list(set(round(e.dxf.start[0], 1) for e in lines) | set(round(e.dxf.end[0], 1) for e in lines)))
print("Top line X coords (sample):", x_coords[:10], "...", x_coords[-10:])
