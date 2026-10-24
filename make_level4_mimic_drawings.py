import ezdxf
import svgwrite
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Load DXF
doc = ezdxf.readfile('AVILLION Riou.dxf')
msp = doc.modelspace()

# Get all MIMIC_SIZE entities for Level 4: X in [1000, 1900], Y in [550, 1250]
top_entities = [e for e in msp if e.dxf.layer == 'MIMIC_SIZE' and any(1000 <= p[0] <= 1900 and 550 <= p[1] <= 1250 for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices]))]

# Compute bounding box
xs, ys = [], []
for e in top_entities:
    if e.dxftype() == 'LINE':
        xs.extend([e.dxf.start[0], e.dxf.end[0]])
        ys.extend([e.dxf.start[1], e.dxf.end[1]])
    elif e.dxftype() == 'POLYLINE':
        for v in e.vertices:
            xs.append(v.dxf.location[0])
            ys.append(v.dxf.location[1])
    elif e.dxftype() == 'CIRCLE':
        xs.append(e.dxf.center[0])
        ys.append(e.dxf.center[1])

min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)

print(f"Level 4 Top bounds: X=[{min_x:.2f}, {max_x:.2f}], Y=[{min_y:.2f}, {max_y:.2f}]")

# Padding around floorplan
pad = 60
view_min_x = min_x - pad
view_max_x = max_x + pad
view_min_y = min_y - pad - 60
view_max_y = max_y + pad + 40

width = view_max_x - view_min_x
height = view_max_y - view_min_y

# Generate SVG
dwg = svgwrite.Drawing('avillion_level4_mimic.svg', size=(f"{width:.1f}px", f"{height:.1f}px"), viewBox=f"{view_min_x:.1f} {-view_max_y:.1f} {width:.1f} {height:.1f}")

# Background
dwg.add(dwg.rect(insert=(view_min_x, -view_max_y), size=(width, height), fill='#0F172A'))

# Grid overlay
grid_group = dwg.g(id='grid', stroke='#1E293B', stroke_width=0.5, stroke_dasharray='4,4')
for gx in range(int(view_min_x), int(view_max_x), 50):
    grid_group.add(dwg.line((gx, -view_max_y), (gx, -view_min_y)))
for gy in range(int(view_min_y), int(view_max_y), 50):
    grid_group.add(dwg.line((view_min_x, -gy), (view_max_x, -gy)))
dwg.add(grid_group)

# Header
header = dwg.g(id='header')
header.add(dwg.rect(insert=(min_x, -(max_y + 35)), size=(max_x - min_x, 30), fill='#1E293B', rx=5, ry=5, stroke='#38BDF8', stroke_width=1))
header.add(dwg.text('AVILLION RIOU — LEVEL 4 FIRE ALARM MIMIC DIAGRAM', insert=((min_x + max_x)/2, -(max_y + 15)), text_anchor='middle', font_size='16px', font_family='sans-serif', font_weight='bold', fill='#F8FAFC'))
dwg.add(header)

# Floorplan geometry
floorplan = dwg.g(id='floorplan')
for e in top_entities:
    if e.dxftype() == 'LINE':
        p1, p2 = e.dxf.start, e.dxf.end
        floorplan.add(dwg.line((p1[0], -p1[1]), (p2[0], -p2[1]), stroke='#38BDF8', stroke_width=1.5, stroke_linecap='round'))
    elif e.dxftype() == 'POLYLINE':
        pts = [(v.dxf.location[0], -v.dxf.location[1]) for v in e.vertices]
        if e.is_closed:
            floorplan.add(dwg.polygon(pts, fill='#0284C7', fill_opacity=0.2, stroke='#38BDF8', stroke_width=1.8))
        else:
            floorplan.add(dwg.polyline(pts, fill='none', stroke='#38BDF8', stroke_width=1.8))
    elif e.dxftype() == 'CIRCLE':
        c = e.dxf.center
        r = e.dxf.radius
        floorplan.add(dwg.circle(center=(c[0], -c[1]), r=r, fill='#F59E0B', fill_opacity=0.3, stroke='#F59E0B', stroke_width=1.5))
dwg.add(floorplan)

# Labels
labels = dwg.g(id='room_labels', font_family='sans-serif', font_weight='bold')
labels.add(dwg.text('CORRIDOR & ROOM UNITS (ZONE 13 & 14)', insert=(1150, -980), font_size='12px', fill='#38BDF8'))
labels.add(dwg.text('APARTMENT UNITS (ZONE 15 & 16)', insert=(1500, -780), font_size='12px', fill='#94A3B8'))
dwg.add(labels)

# Legend
legend = dwg.g(id='legend', font_family='sans-serif')
leg_x = min_x
leg_y = -(min_y - 15)
legend.add(dwg.rect(insert=(leg_x, leg_y), size=(max_x - min_x, 40), fill='#1E293B', rx=5, ry=5, stroke='#475569', stroke_width=1))

items = [
    ('#EF4444', 'Break Glass (BG)'),
    ('#F59E0B', 'Heat Detector (HD)'),
    ('#3B82F6', 'Smoke Detector (SD)'),
    ('#10B981', 'Hose Reel / DP'),
    ('#A855F7', 'CO2 Extinguisher'),
    ('#EC4899', 'Fire Alarm Panel / Mimic')
]

col_w = (max_x - min_x) / len(items)
for i, (color, label) in enumerate(items):
    ix = leg_x + i * col_w + 15
    iy = leg_y + 24
    legend.add(dwg.circle(center=(ix, iy - 4), r=6, fill=color))
    legend.add(dwg.text(label, insert=(ix + 12, iy), font_size='10px', fill='#E2E8F0'))

dwg.add(legend)
dwg.save()
print("Saved avillion_level4_mimic.svg")

# Render PNG
fig, ax = plt.subplots(figsize=(16, 9), facecolor='#0F172A')
ax.set_facecolor('#0F172A')

for e in top_entities:
    if e.dxftype() == 'LINE':
        p1, p2 = e.dxf.start, e.dxf.end
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#38BDF8', linewidth=1.2)
    elif e.dxftype() == 'POLYLINE':
        pts = [v.dxf.location for v in e.vertices]
        if e.is_closed: pts.append(pts[0])
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#0284C7', linewidth=1.5)
        poly = patches.Polygon([(p[0], p[1]) for p in pts], closed=True, facecolor='#0284C7', alpha=0.2)
        ax.add_patch(poly)
    elif e.dxftype() == 'CIRCLE':
        c = e.dxf.center
        r = e.dxf.radius
        circle = plt.Circle((c[0], c[1]), r, facecolor='#F59E0B', alpha=0.3, edgecolor='#F59E0B', linewidth=1.5)
        ax.add_patch(circle)

ax.set_xlim(view_min_x, view_max_x)
ax.set_ylim(view_min_y, view_max_y)
ax.set_aspect('equal')

plt.title('AVILLION RIOU — LEVEL 4 MIMIC FLOORPLAN', color='#F8FAFC', fontsize=14, pad=15, weight='bold')
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_color('#334155')

plt.savefig('avillion_level4_mimic.png', dpi=300, bbox_inches='tight', facecolor='#0F172A')
plt.close()
print("Saved avillion_level4_mimic.png")
