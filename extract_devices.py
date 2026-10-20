import ezdxf
import json

doc = ezdxf.readfile('AVILLION Riou.dxf')
msp = doc.modelspace()

# CAD Floorplan Level 1 region: X in [-3300, -2700], Y in [-1350, -1090]
cad_entities = [e for e in msp if any(-3300 <= p[0] <= -2700 and -1350 <= p[1] <= -1090 for p in ([e.dxf.start, e.dxf.end] if e.dxftype()=='LINE' else [e.dxf.center] if e.dxftype() in ('CIRCLE','ARC') else [e.dxf.insert] if hasattr(e.dxf, 'insert') else [v.dxf.location for v in e.vertices]))]

devices = []

# Top mimic bounds vs Bot CAD bounds for coordinate mapping
# Top bounds: X=[-1935.14, -1132.02], Y=[657.89, 1028.14]
# Bot CAD bounds: X=[-3231.67, -2661.11], Y=[-1390.41, -1168.51]

top_min_x, top_max_x = -1935.14, -1132.02
top_min_y, top_max_y = 657.89, 1028.14

bot_min_x, bot_max_x = -3231.67, -2661.11
bot_min_y, bot_max_y = -1390.41, -1168.51

def cad_to_mimic(cx, cy):
    rx = (cx - bot_min_x) / (bot_max_x - bot_min_x)
    ry = (cy - bot_min_y) / (bot_max_y - bot_min_y)
    mx = top_min_x + rx * (top_max_x - top_min_x)
    my = top_min_y + ry * (top_max_y - top_min_y)
    return round(mx, 2), round(my, 2), round(rx * 100, 2), round((1 - ry) * 100, 2)

device_id = 1
for e in cad_entities:
    if e.dxftype() == 'TEXT':
        txt = e.dxf.text.strip()
        x, y = round(e.dxf.insert[0], 2), round(e.dxf.insert[1], 2)

        # Check if text is a device type
        dev_type = None
        zone = None
        desc = ""

        if txt in ('H', 'Z.2', 'Z.3'):
            dev_type = 'HEAT_DETECTOR'
            desc = 'Heat Detector'
            zone = 2 if txt in ('H', 'Z.2') else 3
        elif txt == 'S' or txt == 'Z.4':
            dev_type = 'SMOKE_DETECTOR'
            desc = 'Smoke Detector'
            zone = 4
        elif txt == 'BG' or txt == 'Z.1':
            dev_type = 'BREAK_GLASS'
            desc = 'Manual Call Point / Break Glass'
            zone = 1
        elif txt == 'DP':
            dev_type = 'FIRE_PANEL'
            desc = 'Fire Alarm Panel / Distribution Point'
            zone = 1
        elif txt == 'HR':
            dev_type = 'HOSE_REEL'
            desc = 'Hose Reel Drum'
            zone = 1
        elif txt == 'CO2':
            dev_type = 'EXTINGUISHER'
            desc = 'CO2 Fire Extinguisher'
            zone = 1

        if dev_type and not (txt.startswith('Z.') and any(d['cad_x'] == x and d['cad_y'] == y for d in devices)):
            mx, my, px, py = cad_to_mimic(x, y)
            devices.append({
                "id": f"DEV-{device_id:03d}",
                "type": dev_type,
                "label": txt,
                "description": desc,
                "zone": zone,
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

print(f"Extracted {len(devices)} device pins.")

json_data = {
    "building": "AVILLION RIOU",
    "level": "Level 1 & 1A",
    "total_devices": len(devices),
    "zones": [
        {"zone": 1, "name": "BG ZONE 1", "description": "Break Glass / Alarm Panel / Hose Reel"},
        {"zone": 2, "name": "HD ZONE 2", "description": "Heat Detectors - Corridor & Gear Room"},
        {"zone": 3, "name": "HD ZONE 3", "description": "Heat Detectors - Room Units"},
        {"zone": 4, "name": "SD ZONE 4", "description": "Smoke Detectors - Hallway / Utility"}
    ],
    "devices": devices
}

with open('avillion_level1_devices.json', 'w') as f:
    json.dump(json_data, f, indent=2)

print("Saved avillion_level1_devices.json")
