import ezdxf
import svgwrite
import json
import os
import math

def process_umb1_floors():
    doc = ezdxf.readfile('sources/batch-02/UMB MIMIC.dxf')
    msp = doc.modelspace()

    floors = [
        {
            'floor_key': 'umb_1_p1',
            'candidate_key': 'lib-umb-1-p1',
            'floor_identity': 'Page 1 / Ground Floor Plan',
            'title': 'UMB-1 — PAGE 1 (GROUND FLOOR PLAN)',
            'cad_title': 'GROUND FLOOR PLAN',
            'crop_box': (285.0, 425.0, -10.0, 180.0),
            'padding': 10.0,
        },
        {
            'floor_key': 'umb_1_p2',
            'candidate_key': 'lib-umb-1-p2',
            'floor_identity': 'Page 2 / First Floor Plan',
            'title': 'UMB-1 — PAGE 2 (FIRST FLOOR PLAN)',
            'cad_title': 'FIRST FLOOR PLAN',
            'crop_box': (425.0, 645.0, -10.0, 185.0),
            'padding': 10.0,
        },
        {
            'floor_key': 'umb_1_p3',
            'candidate_key': 'lib-umb-1-p3',
            'floor_identity': 'Page 3 / Second Floor Plan',
            'title': 'UMB-1 — PAGE 3 (SECOND FLOOR PLAN)',
            'cad_title': 'SECOND FLOOR PLAN',
            'crop_box': (645.0, 855.0, -10.0, 185.0),
            'padding': 10.0,
        },
        {
            'floor_key': 'umb_1_p4',
            'candidate_key': 'lib-umb-1-p4',
            'floor_identity': 'Page 4 / Third Floor Plan',
            'title': 'UMB-1 — PAGE 4 (THIRD FLOOR PLAN)',
            'cad_title': 'THIRD FLOOR PLAN',
            'crop_box': (280.0, 405.0, -55.0, 42.0),
            'padding': 10.0,
        },
    ]

    for config in floors:
        fkey = config['floor_key']
        x1, x2, y1, y2 = config['crop_box']

        # Collect entities strictly inside or centered in crop_box
        floor_ents = []
        for e in msp:
            if e.dxftype() == 'LINE':
                p1, p2 = e.dxf.start, e.dxf.end
                if (x1 <= p1[0] <= x2 and y1 <= p1[1] <= y2) or (x1 <= p2[0] <= x2 and y1 <= p2[1] <= y2):
                    # Filter out title block / zone text headers lines if needed or outer framing lines far away
                    floor_ents.append(e)
            elif e.dxftype() == 'ARC':
                c = e.dxf.center
                if x1 <= c[0] <= x2 and y1 <= c[1] <= y2:
                    floor_ents.append(e)
            elif e.dxftype() in ('LWPOLYLINE', 'POLYLINE'):
                pts = [v.dxf.location if hasattr(v.dxf, 'location') else v for v in e.vertices] if e.dxftype() == 'POLYLINE' else list(e.get_points())
                if any(x1 <= p[0] <= x2 and y1 <= p[1] <= y2 for p in pts):
                    floor_ents.append(e)
            elif hasattr(e.dxf, 'insert'):
                p = e.dxf.insert
                if x1 <= p[0] <= x2 and y1 <= p[1] <= y2:
                    floor_ents.append(e)

        # Calculate bounding box of MIMIC_SIZE & key geometry for framing
        geom_xs, geom_ys = [], []
        for e in floor_ents:
            if e.dxf.layer in ('MIMIC_SIZE', '0', 'BUILD'):
                if e.dxftype() == 'LINE':
                    p1, p2 = e.dxf.start, e.dxf.end
                    if x1 <= p1[0] <= x2 and y1 <= p1[1] <= y2 and x1 <= p2[0] <= x2 and y1 <= p2[1] <= y2:
                        geom_xs.extend([p1[0], p2[0]])
                        geom_ys.extend([p1[1], p2[1]])
                elif e.dxftype() == 'ARC':
                    c = e.dxf.center
                    r = e.dxf.radius
                    if x1 <= c[0] <= x2 and y1 <= c[1] <= y2:
                        geom_xs.extend([c[0]-r, c[0]+r])
                        geom_ys.extend([c[1]-r, c[1]+r])

        min_x = min(geom_xs) - config['padding'] if geom_xs else x1
        max_x = max(geom_xs) + config['padding'] if geom_xs else x2
        min_y = min(geom_ys) - config['padding'] if geom_ys else y1
        max_y = max(geom_ys) + config['padding'] if geom_ys else y2

        width = max_x - min_x
        height = max_y - min_y

        # Target SVG canvas dimensions (e.g. 1000px width aspect scale)
        svg_w = 1200.0
        scale = svg_w / width
        svg_h = height * scale

        def transform(x, y):
            # DXF Y is upward, SVG Y is downward
            sx = (x - min_x) * scale
            sy = (max_y - y) * scale
            return round(sx, 2), round(sy, 2)

        # Create SVG drawing
        svg_filename = f"{fkey}_mimic.svg"
        dwg = svgwrite.Drawing(svg_filename, size=(f"{svg_w:.1f}px", f"{svg_h:.1f}px"), viewBox=f"0 0 {svg_w:.1f} {svg_h:.1f}")

        # Add background rect
        dwg.add(dwg.rect(insert=(0, 0), size=(svg_w, svg_h), fill='#12161f'))

        # Add title banner
        dwg.add(dwg.text(config['title'], insert=(20, 30), fill='#e2e8f0', font_size='18px', font_family='sans-serif', font_weight='bold'))

        # Group for geometry
        geom_group = dwg.g(id='architecture')

        # Devices list
        devices = []

        for e in floor_ents:
            layer = e.dxf.layer
            color = '#94a3b8' # default light gray
            stroke_width = 1.5

            if layer == 'MIMIC_SIZE':
                color = '#cbd5e1' # architectural lines
                stroke_width = 1.8
            elif layer == 'FF_GRID_LINE':
                color = '#334155' # grid lines
                stroke_width = 0.8
            elif layer == 'BUILD':
                color = '#f59e0b' # headers/title text
            elif layer == 'TEXT':
                color = '#94a3b8'

            if e.dxftype() == 'LINE':
                p1, p2 = e.dxf.start, e.dxf.end
                if x1 <= p1[0] <= x2 and y1 <= p1[1] <= y2 and x1 <= p2[0] <= x2 and y1 <= p2[1] <= y2:
                    sx1, sy1 = transform(p1[0], p1[1])
                    sx2, sy2 = transform(p2[0], p2[1])
                    geom_group.add(dwg.line(start=(sx1, sy1), end=(sx2, sy2), stroke=color, stroke_width=stroke_width))

            elif e.dxftype() == 'ARC':
                c = e.dxf.center
                r = e.dxf.radius
                if x1 <= c[0] <= x2 and y1 <= c[1] <= y2:
                    start_angle = math.radians(e.dxf.start_angle)
                    end_angle = math.radians(e.dxf.end_angle)
                    # SVG path arc
                    x_start = c[0] + r * math.cos(start_angle)
                    y_start = c[1] + r * math.sin(start_angle)
                    x_end = c[0] + r * math.cos(end_angle)
                    y_end = c[1] + r * math.sin(end_angle)

                    sx_s, sy_s = transform(x_start, y_start)
                    sx_e, sy_e = transform(x_end, y_end)
                    s_r = r * scale

                    large_arc = 1 if (e.dxf.end_angle - e.dxf.start_angle) % 360 > 180 else 0
                    path_data = f"M {sx_s} {sy_s} A {s_r:.2f} {s_r:.2f} 0 {large_arc} 0 {sx_e} {sy_e}"
                    geom_group.add(dwg.path(d=path_data, fill='none', stroke=color, stroke_width=stroke_width))

            elif e.dxftype() in ('TEXT', 'MTEXT'):
                txt = e.dxf.text if e.dxftype() == 'TEXT' else e.text
                txt_clean = txt.strip()
                p = e.dxf.insert
                if x1 <= p[0] <= x2 and y1 <= p[1] <= y2:
                    sx, sy = transform(p[0], p[1])

                    # Check if text is a device indicator (S, H, BG, DP, HR, CO2) or zone label
                    if txt_clean in ('S', 'H', 'BG', 'DP', 'HR', 'CO2'):
                        devices.append({
                            'device_label': txt_clean,
                            'cad_location': [round(p[0], 2), round(p[1], 2)],
                            'svg_location': [sx, sy],
                            'layer': layer
                        })
                        # Render device symbol in SVG
                        dev_color = '#ef4444' if txt_clean in ('S', 'H', 'CO2') else '#3b82f6'
                        geom_group.add(dwg.circle(center=(sx, sy), r=4, fill=dev_color))
                        geom_group.add(dwg.text(txt_clean, insert=(sx + 6, sy + 3), fill='#f8fafc', font_size='10px', font_weight='bold'))
                    elif txt_clean.startswith('Z.') or 'ZONE' in txt_clean:
                        # Zone labels
                        geom_group.add(dwg.text(txt_clean, insert=(sx, sy), fill='#f59e0b', font_size='10px', font_family='sans-serif'))
                    elif len(txt_clean) > 1 and not txt_clean.startswith('GROUND') and not txt_clean.startswith('FIRST') and not txt_clean.startswith('SECOND') and not txt_clean.startswith('THIRD'):
                        # Room / location labels
                        geom_group.add(dwg.text(txt_clean, insert=(sx, sy), fill='#cbd5e1', font_size='11px', font_family='sans-serif', font_weight='500'))

        dwg.add(geom_group)
        dwg.save()

        # Save metadata JSON
        meta_filename = f"{fkey}_metadata.json"
        metadata = {
            "site": "UMB-1",
            "floor_key": fkey,
            "candidate_key": config['candidate_key'],
            "floor_identity": config['floor_identity'],
            "title": config['title'],
            "source_dxf": "sources/batch-02/UMB MIMIC.dxf",
            "runtime_inventory_status": "RECONCILED_CANDIDATE",
            "discrepancy_reason": f"Canonical UMB-1 runtime candidate reconciled against CAD {config['cad_title']} geometry.",
            "review_status": "REVIEW_REQUIRED",
            "entity_count": len(floor_ents),
            "device_count": len(devices),
            "bounds": {
                "min_x": round(min_x, 2),
                "max_x": round(max_x, 2),
                "min_y": round(min_y, 2),
                "max_y": round(max_y, 2),
                "width": round(width, 2),
                "height": round(height, 2)
            },
            "identity_evidence": {
                "source_text": config['title'],
                "dxf_layer": "BUILD",
                "cad_region_box": [round(min_x, 2), round(max_x, 2), round(min_y, 2), round(max_y, 2)]
            }
        }
        with open(meta_filename, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Save editable devices JSON
        dev_filename = f"{fkey}_devices.json"
        with open(dev_filename, 'w') as f:
            json.dump(devices, f, indent=2)

        print(f"Generated {fkey}: SVG ({svg_filename}), Metadata ({meta_filename}), Devices ({dev_filename}, {len(devices)} devices)")

if __name__ == '__main__':
    process_umb1_floors()
