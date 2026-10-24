import json

with open('avillion_penthouse_lower_devices.json', 'r') as f:
    devices_data = json.load(f)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AVILLION PENTHOUSE LOWER (LEVEL 6) MIMIC DRAWING REVIEW</title>
    <style>
        :root {{
            --bg-color: #0F172A;
            --card-bg: #1E293B;
            --text-color: #F8FAFC;
            --text-muted: #94A3B8;
            --accent-blue: #38BDF8;
            --border-color: #334155;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}

        h1 {{
            font-size: 24px;
            margin: 0;
            color: var(--text-color);
        }}

        .status-badge {{
            background-color: #EF4444;
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            letter-spacing: 0.5px;
        }}

        .section {{
            background-color: var(--card-bg);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
            border: 1px solid var(--border-color);
        }}

        .section h2 {{
            font-size: 18px;
            margin-top: 0;
            margin-bottom: 15px;
            color: var(--accent-blue);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }}

        .image-container {{
            width: 100%;
            overflow: hidden;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background-color: #020617;
            text-align: center;
        }}

        .image-container img {{
            width: 100%;
            height: auto;
            display: block;
        }}

        .device-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}

        .summary-card {{
            background-color: #0F172A;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}

        .summary-card h3 {{
            margin: 0 0 5px 0;
            font-size: 14px;
            color: var(--text-muted);
        }}

        .summary-card .value {{
            font-size: 20px;
            font-weight: bold;
            color: var(--accent-blue);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 14px;
        }}

        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            background-color: #0F172A;
            color: var(--accent-blue);
        }}

        tr:hover {{
            background-color: #1E293B;
        }}

        .zone-pill {{
            background-color: #0284C7;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>AVILLION PENTHOUSE LOWER (LEVEL 6) MIMIC DRAWING REVIEW</h1>
                <p style="margin: 5px 0 0 0; color: var(--text-muted);">AVILLION Riou.dxf — Penthouse Lower (Level 6) Mimic Floorplan & Device Extraction</p>
            </div>
            <div class="status-badge">
                REVIEW_REQUIRED
            </div>
        </header>

        <div class="section">
            <h2>1. Original vs. Converted Visual Comparison</h2>
            <div class="image-container">
                <img src="penthouse_lower_visual_comparison.png" alt="Visual Comparison Original vs Converted Penthouse Lower">
            </div>
        </div>

        <div class="section">
            <h2>2. Vector SVG Floorplan (Penthouse Lower Level 6 Mimic)</h2>
            <div class="image-container">
                <object data="avillion_penthouse_lower_mimic.svg" type="image/svg+xml" style="width:100%; max-height:600px;"></object>
            </div>
        </div>

        <div class="section">
            <h2>3. Device Pins & Zones Summary</h2>
            <div class="device-summary">
                <div class="summary-card">
                    <h3>Building</h3>
                    <div class="value">{devices_data['building']}</div>
                </div>
                <div class="summary-card">
                    <h3>Level</h3>
                    <div class="value">{devices_data['level']}</div>
                </div>
                <div class="summary-card">
                    <h3>Total Extracted Devices</h3>
                    <div class="value">{devices_data['total_devices']}</div>
                </div>
                <div class="summary-card">
                    <h3>Zones Represented</h3>
                    <div class="value">Zone 18, 19, 20</div>
                </div>
            </div>

            <h3>Device Pin Table (Sample Devices)</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Type</th>
                        <th>Label</th>
                        <th>Description</th>
                        <th>Zone</th>
                        <th>CAD Position (X, Y)</th>
                        <th>Mimic Position (X, Y)</th>
                    </tr>
                </thead>
                <tbody>
"""

for dev in devices_data['devices'][:20]:
    html_content += f"""
                    <tr>
                        <td><strong>{dev['id']}</strong></td>
                        <td>{dev['type']}</td>
                        <td>{dev['label']}</td>
                        <td>{dev['description']}</td>
                        <td><span class="zone-pill">Zone {dev['zone']}</span></td>
                        <td>({dev['cad_x']}, {dev['cad_y']})</td>
                        <td>({dev['mimic_x']}, {dev['mimic_y']})</td>
                    </tr>
"""

html_content += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

with open('penthouse_lower_review.html', 'w') as f:
    f.write(html_content)

print("Saved penthouse_lower_review.html")
