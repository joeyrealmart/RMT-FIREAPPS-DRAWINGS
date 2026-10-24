import ezdxf
import json

doc = ezdxf.readfile('AVILLION Riou.dxf')
msp = doc.modelspace()

cad_entities = [e for e in msp if any(-3680 <= p[0] <= -3520 and -1450 <= p[1] <= -1350 for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices]))]

top_min_x, top_max_x = 5802.58, 6342.60
top_min_y, top_max_y = 662.86, 866.29

bot_min_x, bot_max_x = -3668.27, -3541.49
bot_min_y, bot_max_y = -1428.61, -1364.67

def cad_to_mimic(cx, cy):
    rx = (cx - bot_min_x) / (bot_max_x - bot_min_x)
    ry = (cy - bot_min_y) / (bot_max_y - bot_min_y)
    mx = top_min_x + rx * (top_max_x - top_min_x)
    my = top_min_y + ry * (top_max_y - top_min_y)
    return round(mx, 2), round(my, 2), round(rx * 100, 2), round((1 - ry) * 100, 2)

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
                closest_zone = 26

            mx, my, px, py = cad_to_mimic(x, y)
            devices.append({
                "id": f"DEV-L6B-{device_id:03d}",
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

print(f"Extracted {len(devices)} device pins for Level 6B.")

json_data = {
    "building": "AVILLION RIOU",
    "level": "Level 6B (WTL & LMR)",
    "total_devices": len(devices),
    "zones": [
        {"zone": 23, "name": "SD ZONE 23", "description": "Smoke Detectors - Water Tank Room"},
        {"zone": 24, "name": "SD ZONE 24", "description": "Smoke Detectors - Lift Motor Room"},
        {"zone": 25, "name": "HD ZONE 25", "description": "Heat Detectors - WTL / LMR"},
        {"zone": 26, "name": "HD ZONE 26", "description": "Heat Detectors - WTL / LMR"}
    ],
    "devices": devices
}

with open('avillion_level6b_devices.json', 'w') as f:
    json.dump(json_data, f, indent=2)

print("Saved avillion_level6b_devices.json")
