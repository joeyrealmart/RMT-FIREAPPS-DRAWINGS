import ezdxf
import matplotlib.pyplot as plt
import matplotlib.patches as patches

doc = ezdxf.readfile('AVILLION Riou.dxf')
msp = doc.modelspace()

top_entities = [e for e in msp if e.dxf.layer == 'MIMIC_SIZE' and any(4700 <= p[0] <= 5500 and 600 <= p[1] <= 950 for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices]))]

bot_entities = [e for e in msp if any(-3830 <= p[0] <= -3680 and -1430 <= p[1] <= -1350 for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices]))]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9), facecolor='#0F172A')

ax1.set_facecolor('#0F172A')
for e in bot_entities:
    if e.dxftype() == 'LINE':
        p1, p2 = e.dxf.start, e.dxf.end
        c = '#64748B' if e.dxf.layer == '0' else '#38BDF8' if e.dxf.layer == 'MIMIC_SIZE' else '#94A3B8'
        ax1.plot([p1[0], p2[0]], [p1[1], p2[1]], color=c, linewidth=0.6, alpha=0.8)
    elif e.dxftype() == 'POLYLINE':
        pts = [v.dxf.location for v in e.vertices]
        if e.is_closed: pts.append(pts[0])
        ax1.plot([p[0] for p in pts], [p[1] for p in pts], color='#818CF8', linewidth=0.8)
    elif e.dxftype() == 'CIRCLE':
        c = e.dxf.center
        r = e.dxf.radius
        circle = plt.Circle((c[0], c[1]), r, color='#F59E0B', fill=False, linewidth=0.8)
        ax1.add_patch(circle)
    elif e.dxftype() == 'TEXT':
        if any(k in e.dxf.text for k in ['LEVEL', 'BG', 'HD', 'SD', 'ZONE', 'Z.']):
            ax1.text(e.dxf.insert[0], e.dxf.insert[1], e.dxf.text, fontsize=6, color='#F8FAFC', weight='bold')

ax1.set_aspect('equal')
ax1.set_title('ORIGINAL CAD GEOMETRY (AVILLION RIOU.DXF — LEVEL 6A)', color='#F8FAFC', fontsize=12, pad=12, weight='bold')
ax1.set_xticks([])
ax1.set_yticks([])
for spine in ax1.spines.values(): spine.set_color('#334155')

ax2.set_facecolor('#0F172A')
for e in top_entities:
    if e.dxftype() == 'LINE':
        p1, p2 = e.dxf.start, e.dxf.end
        ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#38BDF8', linewidth=1.2)
    elif e.dxftype() == 'POLYLINE':
        pts = [v.dxf.location for v in e.vertices]
        if e.is_closed: pts.append(pts[0])
        ax2.plot([p[0] for p in pts], [p[1] for p in pts], color='#0284C7', linewidth=1.5)
        poly = patches.Polygon([(p[0], p[1]) for p in pts], closed=True, facecolor='#0284C7', alpha=0.2)
        ax2.add_patch(poly)
    elif e.dxftype() == 'CIRCLE':
        c = e.dxf.center
        r = e.dxf.radius
        circle = plt.Circle((c[0], c[1]), r, facecolor='#F59E0B', alpha=0.3, edgecolor='#F59E0B', linewidth=1.5)
        ax2.add_patch(circle)

ax2.text(4920, 820, 'CORRIDOR & HEAT DETECTORS (ZONE 21)', color='#38BDF8', fontsize=9, weight='bold')
ax2.text(5150, 730, 'STAIRWELL & SMOKE DETECTOR (ZONE 22)', color='#94A3B8', fontsize=9, weight='bold')

ax2.set_aspect('equal')
ax2.set_title('CONVERTED LEVEL 6A MIMIC FLOORPLAN', color='#F8FAFC', fontsize=12, pad=12, weight='bold')
ax2.set_xticks([])
ax2.set_yticks([])
for spine in ax2.spines.values(): spine.set_color('#334155')

plt.suptitle('AVILLION RIOU — LEVEL 6A VISUAL COMPARISON', color='#F8FAFC', fontsize=14, y=0.98, weight='bold')
plt.tight_layout()
plt.savefig('level6a_visual_comparison.png', dpi=300, bbox_inches='tight', facecolor='#0F172A')
plt.close()

print("Saved level6a_visual_comparison.png")
