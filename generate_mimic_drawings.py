import ezdxf
import svgwrite
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
import os

def generate_drawings():
    doc = ezdxf.readfile('sources/batch-02/ADMIRAL MARINA CLUB.dxf')
    msp = doc.modelspace()

    floors_config = {
        'lower_ground': {
            'box': (-520, 50, -2100, -1500),
            'title': 'ADMIRAL MARINA CLUB — LOWER GROUND FLOOR MIMIC DIAGRAM',
            'png_title': 'ADMIRAL MARINA CLUB — LOWER GROUND FLOOR',
            'labels': [
                ('LOWER GROUND FLOOR / PUMP ROOMS / UTILITIES', -250, -1800),
                ('FIRE PUMP & SPRINKLER CONTROL', -400, -1650),
                ('STORAGE & SERVICE CORRIDORS', -100, -1950)
            ]
        },
        'ground': {
            'box': (50, 550, -2100, -1500),
            'title': 'ADMIRAL MARINA CLUB — GROUND FLOOR MIMIC DIAGRAM',
            'png_title': 'ADMIRAL MARINA CLUB — GROUND FLOOR',
            'labels': [
                ('MAIN LOBBY & ENTRANCE FOYER', 250, -1800),
                ('RESTAURANT & DINING AREA', 120, -1650),
                ('ADMINISTRATION & RECEPTION', 400, -1950)
            ]
        },
        'level1': {
            'box': (950, 1600, -2100, -1350),
            'title': 'ADMIRAL MARINA CLUB — 1ST FLOOR MIMIC DIAGRAM',
            'png_title': 'ADMIRAL MARINA CLUB — 1ST FLOOR',
            'labels': [
                ('1ST FLOOR FUNCTION HALL & SUITES', 1250, -1700),
                ('BANQUET / MULTI-PURPOSE ROOM', 1050, -1500),
                ('VIP LOUNGE & CORRIDORS', 1450, -1900)
            ]
        },
        'upper': {
            'box': (450, 1050, -2100, -1500),
            'title': 'ADMIRAL MARINA CLUB — UPPER FLOOR / PLANT MIMIC DIAGRAM',
            'png_title': 'ADMIRAL MARINA CLUB — UPPER FLOOR / PLANT',
            'labels': [
                ('UPPER FLOOR / A/C PLANT ROOM', 750, -1800),
                ('MECHANICAL & ELECTRICAL SUITE', 550, -1650),
                ('SERVICE DUCTS & ACCESS CORRIDOR', 900, -1950)
            ]
        },
        'roof': {
            'box': (-200, 400, -2400, -1900),
            'title': 'ADMIRAL MARINA CLUB — ROOF FLOOR MIMIC DIAGRAM',
            'png_title': 'ADMIRAL MARINA CLUB — ROOF FLOOR',
            'labels': [
                ('MAIN ROOF TOP & TANK ROOMS', 100, -2150),
                ('LIFT MOTOR ROOM', -50, -2050),
                ('STAIRCASE OVERRUN & PARAPET', 250, -2250)
            ]
        },
        'site_plan': {
            'box': (500, 1300, -2400, -1900),
            'title': 'ADMIRAL MARINA CLUB — SITE PLAN MIMIC DIAGRAM',
            'png_title': 'ADMIRAL MARINA CLUB — SITE PLAN',
            'labels': [
                ('SITE PLAN / MARINA CLUB BOUNDARY', 900, -2150),
                ('ACCESS ROAD & CAR PARK', 700, -2020),
                ('EXTERNAL HYDRANTS & PERIMETER', 1100, -2280)
            ]
        }
    }

    for name, cfg in floors_config.items():
        x0, x1, y0, y1 = cfg['box']
        ents = []
        for e in msp:
            if e.dxf.layer != 'MIMIC_SIZE': continue
            t = e.dxftype()
            pts = []
            if t == 'LINE': pts = [(e.dxf.start[0], e.dxf.start[1]), (e.dxf.end[0], e.dxf.end[1])]
            elif hasattr(e.dxf, 'center'): pts = [(e.dxf.center[0], e.dxf.center[1])]
            elif hasattr(e.dxf, 'insert'): pts = [(e.dxf.insert[0], e.dxf.insert[1])]
            elif t == 'POLYLINE': pts = [(v.dxf.location[0], v.dxf.location[1]) for v in e.vertices]

            if pts and all(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in pts):
                ents.append(e)

        # Get exact bounds
        xs, ys = [], []
        for e in ents:
            t = e.dxftype()
            if t == 'LINE':
                xs.extend([e.dxf.start[0], e.dxf.end[0]])
                ys.extend([e.dxf.start[1], e.dxf.end[1]])
            elif t == 'POLYLINE':
                for v in e.vertices:
                    xs.append(v.dxf.location[0])
                    ys.append(v.dxf.location[1])
            elif t in ('CIRCLE', 'ARC'):
                xs.append(e.dxf.center[0])
                ys.append(e.dxf.center[1])

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        pad = 50
        view_min_x = min_x - pad
        view_max_x = max_x + pad
        view_min_y = min_y - pad - 60
        view_max_y = max_y + pad + 50

        width = view_max_x - view_min_x
        height = view_max_y - view_min_y

        # --- Generate SVG ---
        svg_filename = f'admiral_{name}_mimic.svg'
        dwg = svgwrite.Drawing(svg_filename, size=(f"{width:.1f}px", f"{height:.1f}px"),
                              viewBox=f"{view_min_x:.1f} {-view_max_y:.1f} {width:.1f} {height:.1f}")

        # Dark Background
        dwg.add(dwg.rect(insert=(view_min_x, -view_max_y), size=(width, height), fill='#0F172A'))

        # Subtle Grid Lines
        grid_group = dwg.g(id='grid', stroke='#1E293B', stroke_width=0.5, stroke_dasharray='4,4')
        for gx in range(int(view_min_x), int(view_max_x), 50):
            grid_group.add(dwg.line((gx, -view_max_y), (gx, -view_min_y)))
        for gy in range(int(view_min_y), int(view_max_y), 50):
            grid_group.add(dwg.line((view_min_x, -gy), (view_max_x, -gy)))
        dwg.add(grid_group)

        # Header Panel
        header = dwg.g(id='header')
        header.add(dwg.rect(insert=(min_x, -(max_y + 40)), size=(max_x - min_x, 35), fill='#1E293B', rx=6, ry=6, stroke='#38BDF8', stroke_width=1.2))
        header.add(dwg.text(cfg['title'], insert=((min_x + max_x)/2, -(max_y + 18)), text_anchor='middle', font_size='16px', font_family='sans-serif', font_weight='bold', fill='#F8FAFC'))
        dwg.add(header)

        # CAD Floorplan Geometry
        floorplan = dwg.g(id='floorplan')
        for e in ents:
            t = e.dxftype()
            if t == 'LINE':
                p1, p2 = e.dxf.start, e.dxf.end
                floorplan.add(dwg.line((p1[0], -p1[1]), (p2[0], -p2[1]), stroke='#38BDF8', stroke_width=1.5, stroke_linecap='round'))
            elif t == 'POLYLINE':
                pts = [(v.dxf.location[0], -v.dxf.location[1]) for v in e.vertices]
                if e.is_closed:
                    floorplan.add(dwg.polygon(pts, fill='#0284C7', fill_opacity=0.2, stroke='#38BDF8', stroke_width=1.8))
                else:
                    floorplan.add(dwg.polyline(pts, fill='none', stroke='#38BDF8', stroke_width=1.8))
            elif t == 'CIRCLE':
                c = e.dxf.center
                r = e.dxf.radius
                floorplan.add(dwg.circle(center=(c[0], -c[1]), r=r, fill='#F59E0B', fill_opacity=0.3, stroke='#F59E0B', stroke_width=1.5))
            elif t == 'ARC':
                c = e.dxf.center
                r = e.dxf.radius
                # Draw arc simple representative circle or polyline
                floorplan.add(dwg.circle(center=(c[0], -c[1]), r=r, fill='none', stroke='#38BDF8', stroke_width=1.2, stroke_dasharray='3,3'))
        dwg.add(floorplan)

        # Room Labels
        labels_group = dwg.g(id='room_labels', font_family='sans-serif', font_weight='bold')
        for txt_label, lx, ly in cfg['labels']:
            # Ensure label stays inside viewport
            clx = max(min_x + 20, min(max_x - 20, lx))
            cly = max(min_y + 20, min(max_y - 20, ly))
            labels_group.add(dwg.text(txt_label, insert=(clx, -cly), font_size='13px', fill='#38BDF8'))
        dwg.add(labels_group)

        # Legend Bar
        legend = dwg.g(id='legend', font_family='sans-serif')
        leg_x = min_x
        leg_y = -(min_y - 20)
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
            ix = leg_x + i * col_w + 12
            iy = leg_y + 24
            legend.add(dwg.circle(center=(ix, iy - 4), r=5, fill=color))
            legend.add(dwg.text(label, insert=(ix + 10, iy), font_size='10px', fill='#E2E8F0'))
        dwg.add(legend)

        dwg.save()

        # --- Generate High-Res PNG ---
        png_filename = f'admiral_{name}_mimic.png'
        fig, ax = plt.subplots(figsize=(16, 10), facecolor='#0F172A')
        ax.set_facecolor('#0F172A')

        for e in ents:
            t = e.dxftype()
            if t == 'LINE':
                p1, p2 = e.dxf.start, e.dxf.end
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#38BDF8', linewidth=1.2)
            elif t == 'POLYLINE':
                pts = [v.dxf.location for v in e.vertices]
                if e.is_closed: pts.append(pts[0])
                ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#0284C7', linewidth=1.5)
                poly = patches.Polygon([(p[0], p[1]) for p in pts], closed=True, facecolor='#0284C7', alpha=0.2)
                ax.add_patch(poly)
            elif t == 'CIRCLE':
                c = e.dxf.center
                r = e.dxf.radius
                circle = plt.Circle((c[0], c[1]), r, facecolor='#F59E0B', alpha=0.3, edgecolor='#F59E0B', linewidth=1.5)
                ax.add_patch(circle)
            elif t == 'ARC':
                c = e.dxf.center
                r = e.dxf.radius
                circle = plt.Circle((c[0], c[1]), r, facecolor='none', edgecolor='#38BDF8', linestyle='--', linewidth=1.0)
                ax.add_patch(circle)

        for txt_label, lx, ly in cfg['labels']:
            clx = max(min_x + 20, min(max_x - 20, lx))
            cly = max(min_y + 20, min(max_y - 20, ly))
            ax.text(clx, cly, txt_label, color='#38BDF8', fontsize=11, fontweight='bold', ha='center', va='center')

        ax.set_xlim(view_min_x, view_max_x)
        ax.set_ylim(view_min_y, view_max_y)
        ax.set_aspect('equal')

        plt.title(cfg['png_title'], color='#F8FAFC', fontsize=14, pad=15, weight='bold')
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('#334155')

        plt.savefig(png_filename, dpi=300, bbox_inches='tight', facecolor='#0F172A')
        plt.close()

        print(f"Generated {svg_filename} and {png_filename}")

if __name__ == '__main__':
    generate_drawings()
