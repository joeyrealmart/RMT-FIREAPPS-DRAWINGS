import ezdxf
import json

doc = ezdxf.readfile('AVILLION Riou.dxf')
msp = doc.modelspace()

# CAD Floorplan Level 2 region: X in [-3000, -2700], Y in [-1300, -1150]
cad_entities = [e for e in msp if any(-3000 <= p[0] <= -2700 and -1300 <= p[1] <= -1150 for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices]))]

# Top Mimic L2 bounds vs Bot CAD L2 bounds for coordinate mapping
# Top Mimic L2 bounds: X=[-523.98, 280.96], Y=[714.38, 1047.04]
# Bot CAD L2 bounds: X=[-3231.67, -2717.16], Y=[-1275.53, -1171.10]

top_min_x, top_max_x = -523.98, 280.96
top_min_y, top_max_y = 714.38, 1047.04

bot_min_x, bot_max_x = -3231.67, -2717.16
bot_min_y, bot_max_y = -1275.53, -1171.10

def cad_to_mimic(cx, cy):
    rx = (cx - bot_min_x) / (bot_max_x - bot_min_x)
    ry = (cy - bot_min_y) / (bot_max_y - bot_min_y)
    mx = top_min_x + rx * (top_max_x - top_min_x)
    my = top_min_y + ry * (top_max_y - top_min_y)
    return round(mx, 2), round(my, 2), round(rx * 100, 2), round((1 - ry) * 100, 2)

# Collect all zone label locations in CAD L2
zone_texts = []
for e in cad_entities:
    if e.dxftype() == 'TEXT':
        txt = e.dxf.text.strip()
        if txt.startswith('Z.'):
            try:
                z_num = int(txt.replace('Z.', ''))
                zone_texts.append((z_num, e.dxf.insert[0], e.dxf.insert[1]))
            except ValueError:
                pass

devices = []
device_id = 1
for e in cad_entities:
    if e.dxftype() == 'TEXT':
        txt = e.dxf.text.strip()
        x, y = round(e.dxf.insert[0], 2), round(e.dxf.insert[1], 2)

        dev_type = None
        desc = ""

        if txt == 'H':
            dev_type = 'HEAT_DETECTOR'
            desc = 'Heat Detector'
        elif txt == 'S':
            dev_type = 'SMOKE_DETECTOR'
            desc = 'Smoke Detector'
        elif txt == 'BG':
            dev_type = 'BREAK_GLASS'
            desc = 'Manual Call Point / Break Glass'
        elif txt == 'DP':
            dev_type = 'FIRE_PANEL'
            desc = 'Fire Alarm Panel / Distribution Point'
        elif txt == 'HR':
            dev_type = 'HOSE_REEL'
            desc = 'Hose Reel Drum'
        elif txt == 'CO2':
            dev_type = 'EXTINGUISHER'
            desc = 'CO2 Fire Extinguisher'

        if dev_type:
            closest_zone = None
            min_dist = 999999
            for z_num, zx, zy in zone_texts:
                dist = ((x - zx)**2 + (y - zy)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    closest_zone = z_num

            if min_dist > 25 or closest_zone is None:
                closest_zone = 5

            mx, my, px, py = cad_to_mimic(x, y)
            devices.append({
                "id": f"DEV-{device_id:03d}",
                "type": dev_type,
                "label": txt,
                "description": desc,
                "zone": closest_zone,
                "cad_x": x,
                "cad_y": y,
                "mimic_x": mx,
                "mimic_y": my,
                "position_pct": {
                    "x": px,
                    "y": py
                }
            })
            device_id += 1

print(f"Extracted {len(devices)} device pins for Level 2.")

json_data = {
    "building": "AVILLION RIOU",
    "level": "Level 2, 3 & 2A",
    "total_devices": len(devices),
    "zones": [
        {"zone": 5, "name": "BG ZONE 5", "description": "Break Glass / Alarm Panel / Hose Reel"},
        {"zone": 6, "name": "HD ZONE 6", "description": "Heat Detectors - Corridor & Room Units"},
        {"zone": 7, "name": "HD/SD ZONE 7", "description": "Heat & Smoke Detectors - Room Units"},
        {"zone": 8, "name": "SD ZONE 8", "description": "Smoke / Heat Detectors - Hallway / Room Units"}
    ],
    "devices": devices
}

with open('avillion_level2_devices.json', 'w') as f:
    json.dump(json_data, f, indent=2)

print("Saved avillion_level2_devices.json")
