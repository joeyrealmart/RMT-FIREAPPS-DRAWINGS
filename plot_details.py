import matplotlib.pyplot as plt
import ezdxf

doc = ezdxf.readfile('AVILLION Riou.dxf')
msp = doc.modelspace()

top_entities = []
bot_entities = []

for e in msp:
    pts = []
    if e.dxftype() == 'LINE': pts = [e.dxf.start, e.dxf.end]
    elif e.dxftype() in ('TEXT', 'CIRCLE', 'INSERT', 'ARC'): pts = [e.dxf.insert if hasattr(e.dxf, 'insert') else e.dxf.center]
    elif e.dxftype() == 'POLYLINE': pts = [v.dxf.location for v in e.vertices]

    if any(-2100 <= p[0] <= -1000 and 600 <= p[1] <= 1050 for p in pts):
        top_entities.append(e)
    if any(-3300 <= p[0] <= -2700 and -1350 <= p[1] <= -1090 for p in pts):
        bot_entities.append(e)

# Plot top_entities
fig, ax = plt.subplots(figsize=(18, 10))
for e in top_entities:
    if e.dxftype() == 'LINE':
        p1, p2 = e.dxf.start, e.dxf.end
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='navy', linewidth=1)
    elif e.dxftype() == 'POLYLINE':
        pts = [v.dxf.location for v in e.vertices]
        if e.is_closed: pts.append(pts[0])
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color='darkred', linewidth=1.2)
    elif e.dxftype() == 'CIRCLE':
        c = e.dxf.center
        r = e.dxf.radius
        circle = plt.Circle((c[0], c[1]), r, color='orange', fill=False, linewidth=1.5)
        ax.add_patch(circle)
    elif e.dxftype() == 'TEXT':
        ax.text(e.dxf.insert[0], e.dxf.insert[1], e.dxf.text, fontsize=10, color='black', weight='bold')

ax.set_aspect('equal')
plt.title('Top Mimic Level 1 Geometry')
plt.savefig('top_mimic_detail.png', dpi=300, bbox_inches='tight')
plt.close()

# Plot bot_entities
fig, ax = plt.subplots(figsize=(22, 12))
for e in bot_entities:
    if e.dxftype() == 'LINE':
        p1, p2 = e.dxf.start, e.dxf.end
        c = 'blue' if e.dxf.layer == 'MIMIC_SIZE' else 'gray' if e.dxf.layer == '0' else 'red'
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=c, linewidth=0.6, alpha=0.8)
    elif e.dxftype() == 'POLYLINE':
        pts = [v.dxf.location for v in e.vertices]
        if e.is_closed: pts.append(pts[0])
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color='purple', linewidth=0.8)
    elif e.dxftype() == 'CIRCLE':
        c = e.dxf.center
        r = e.dxf.radius
        circle = plt.Circle((c[0], c[1]), r, color='red', fill=False, linewidth=0.8)
        ax.add_patch(circle)
    elif e.dxftype() == 'TEXT':
        ax.text(e.dxf.insert[0], e.dxf.insert[1], e.dxf.text, fontsize=5, color='black')

ax.set_aspect('equal')
plt.title('Bot CAD Plan Level 1 Geometry')
plt.savefig('bot_mimic_detail.png', dpi=300, bbox_inches='tight')
plt.close()

print('Saved top_mimic_detail.png and bot_mimic_detail.png')
