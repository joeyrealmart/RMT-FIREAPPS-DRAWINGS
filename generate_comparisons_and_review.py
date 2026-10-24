import ezdxf
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import json
import os

def generate_comparisons_and_review():
    doc = ezdxf.readfile('sources/batch-02/ADMIRAL MARINA CLUB.dxf')
    msp = doc.modelspace()

    floors = ['lower_ground', 'ground', 'level1', 'upper', 'roof', 'site_plan']

    for name in floors:
        # Load metadata and devices
        with open(f'admiral_{name}_metadata.json') as f:
            metadata = json.load(f)
        with open(f'admiral_{name}_devices.json') as f:
            devices = json.load(f)

        x0, x1 = metadata['bounds']['min_x'], metadata['bounds']['max_x']
        y0, y1 = metadata['bounds']['min_y'], metadata['bounds']['max_y']
        pad = 50
        view_min_x, view_max_x = x0 - pad, x1 + pad
        view_min_y, view_max_y = y0 - pad - 60, y1 + pad + 50

        # --- 1. Render Raw CAD View ---
        raw_fig, ax = plt.subplots(figsize=(10, 8), facecolor='#111827')
        ax.set_facecolor('#111827')

        # Find entities in this region
        ents = []
        for e in msp:
            if e.dxf.layer != 'MIMIC_SIZE': continue
            t = e.dxftype()
            pts = []
            if t == 'LINE': pts = [(e.dxf.start[0], e.dxf.start[1]), (e.dxf.end[0], e.dxf.end[1])]
            elif hasattr(e.dxf, 'center'): pts = [(e.dxf.center[0], e.dxf.center[1])]
            elif hasattr(e.dxf, 'insert'): pts = [(e.dxf.insert[0], e.dxf.insert[1])]
            elif t == 'POLYLINE': pts = [(v.dxf.location[0], v.dxf.location[1]) for v in e.vertices]

            if pts and all(x0 - 20 <= p[0] <= x1 + 20 and y0 - 20 <= p[1] <= y1 + 20 for p in pts):
                ents.append(e)

        for e in ents:
            t = e.dxftype()
            if t == 'LINE':
                p1, p2 = e.dxf.start, e.dxf.end
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#6B7280', linewidth=0.8)
            elif t == 'POLYLINE':
                pts = [v.dxf.location for v in e.vertices]
                if e.is_closed: pts.append(pts[0])
                ax.plot([p[0] for p in pts], [p[1] for p in pts], color='#6B7280', linewidth=1.0)
            elif t in ('CIRCLE', 'ARC'):
                c = e.dxf.center
                r = e.dxf.radius
                circle = plt.Circle((c[0], c[1]), r, facecolor='none', edgecolor='#6B7280', linewidth=0.8)
                ax.add_patch(circle)

        ax.set_xlim(view_min_x, view_max_x)
        ax.set_ylim(view_min_y, view_max_y)
        ax.set_aspect('equal')
        plt.title('RAW CAD SOURCE GEOMETRY', color='#9CA3AF', fontsize=12, weight='bold')
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values(): spine.set_color('#374151')

        raw_png_path = f'admiral_{name}_raw.png'
        plt.savefig(raw_png_path, dpi=200, bbox_inches='tight', facecolor='#111827')
        plt.close()

        # --- 2. Side-by-side Visual Comparison PNG ---
        img_raw = Image.open(raw_png_path)
        img_final = Image.open(f'admiral_{name}_mimic.png')

        # Resize raw image to match final image height
        h = img_final.height
        w_raw = int(img_raw.width * (h / img_raw.height))
        img_raw_resized = img_raw.resize((w_raw, h), Image.Resampling.LANCZOS)

        comp_width = w_raw + img_final.width + 20
        comp_img = Image.new('RGB', (comp_width, h), '#0F172A')
        comp_img.paste(img_raw_resized, (0, 0))
        comp_img.paste(img_final, (w_raw + 20, 0))

        comp_filename = f'admiral_{name}_visual_comparison.png'
        comp_img.save(comp_filename)
        os.remove(raw_png_path) # clean up temporary raw img

        # --- 3. Review HTML ---
        dev_rows = ''
        for dev in devices[:20]: # sample up to 20 devices in table
            dev_rows += f"""<tr>
                <td style="padding: 6px 12px; border-bottom: 1px solid #334155;">{dev['id']}</td>
                <td style="padding: 6px 12px; border-bottom: 1px solid #334155;"><span style="background: #1E293B; color: #38BDF8; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{dev['code']}</span></td>
                <td style="padding: 6px 12px; border-bottom: 1px solid #334155;">{dev['type']}</td>
                <td style="padding: 6px 12px; border-bottom: 1px solid #334155;">({dev['dxf_x']}, {dev['dxf_y']})</td>
            </tr>"""

        if not dev_rows:
            dev_rows = '<tr><td colspan="4" style="padding: 12px; color: #94A3B8; text-align: center;">No standalone devices mapped on this floor plan layout.</td></tr>'

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Review: Admiral Marina Club — {metadata['floor_identity']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0F172A;
            color: #F8FAFC;
            margin: 0;
            padding: 24px;
        }}
        .header {{
            background: #1E293B;
            border-radius: 8px;
            padding: 20px 24px;
            margin-bottom: 24px;
            border-left: 6px solid #F59E0B;
        }}
        .badge-review {{
            display: inline-block;
            background-color: #D97706;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 9999px;
            margin-bottom: 8px;
        }}
        .title {{
            font-size: 22px;
            font-weight: bold;
            margin: 0 0 8px 0;
        }}
        .reason {{
            background: #451A03;
            color: #FDBA74;
            border: 1px solid #92400E;
            padding: 12px;
            border-radius: 6px;
            font-size: 14px;
            margin-top: 12px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .card {{
            background: #1E293B;
            border-radius: 8px;
            padding: 16px;
            border: 1px solid #334155;
        }}
        .card h3 {{
            margin-top: 0;
            font-size: 14px;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .stat {{
            font-size: 24px;
            font-weight: bold;
            color: #38BDF8;
        }}
        .img-container {{
            background: #1E293B;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 24px;
            border: 1px solid #334155;
        }}
        .img-container h2 {{
            margin-top: 0;
            font-size: 16px;
            color: #F8FAFC;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th {{
            background: #0F172A;
            text-align: left;
            padding: 8px 12px;
            color: #94A3B8;
            border-bottom: 2px solid #334155;
        }}
    </style>
</head>
<body>
    <div class="header">
        <span class="badge-review">REVIEW_REQUIRED</span>
        <h1 class="title">Admiral Marina Club — {metadata['floor_identity']}</h1>
        <div>Source File: <code>{metadata['source_dxf']}</code></div>
        <div class="reason">
            <strong>Discrepancy / Review Reason:</strong> {metadata['discrepancy_reason']}
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Floor Identity</h3>
            <div class="stat">{metadata['floor_identity']}</div>
        </div>
        <div class="card">
            <h3>CAD Geometry Entities</h3>
            <div class="stat">{metadata['entity_count']}</div>
        </div>
        <div class="card">
            <h3>Device Pins Extracted</h3>
            <div class="stat">{metadata['device_count']}</div>
        </div>
        <div class="card">
            <h3>Bounding Extents</h3>
            <div style="font-size: 14px; color: #E2E8F0; margin-top: 6px;">
                X: [{metadata['bounds']['min_x']}, {metadata['bounds']['max_x']}]<br>
                Y: [{metadata['bounds']['min_y']}, {metadata['bounds']['max_y']}]
            </div>
        </div>
    </div>

    <div class="img-container">
        <h2>1. Side-by-Side Source vs Final Comparison</h2>
        <img src="admiral_{name}_visual_comparison.png" alt="Visual Comparison">
    </div>

    <div class="img-container">
        <h2>2. High-Resolution Mimic Floorplan PNG</h2>
        <img src="admiral_{name}_mimic.png" alt="High Res Mimic PNG">
    </div>

    <div class="card">
        <h3>Extracted Source Device Pins (Sample)</h3>
        <table>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Code</th>
                    <th>Type</th>
                    <th>DXF Coordinates</th>
                </tr>
            </thead>
            <tbody>
                {dev_rows}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        html_filename = f'admiral_{name}_review.html'
        with open(html_filename, 'w') as f:
            f.write(html_content)

        print(f"Generated comparison and review HTML for {name} -> {comp_filename}, {html_filename}")

if __name__ == '__main__':
    generate_comparisons_and_review()
