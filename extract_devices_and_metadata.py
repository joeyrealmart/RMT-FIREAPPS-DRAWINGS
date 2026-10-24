import ezdxf
import json
import os

def extract():
    doc = ezdxf.readfile('sources/batch-02/ADMIRAL MARINA CLUB.dxf')
    msp = doc.modelspace()

    floors_config = {
        'lower_ground': {
            'box': (-520, 50, -2100, -1500),
            'title': 'ADMIRAL MARINA CLUB — LOWER GROUND FLOOR',
            'identity': 'Lower Ground Floor',
            'east_title_pos': (6745.7, 567.8),
            'east_box': (6600, 6900, 450, 750)
        },
        'ground': {
            'box': (50, 550, -2100, -1500),
            'title': 'ADMIRAL MARINA CLUB — GROUND FLOOR',
            'identity': 'Ground Floor',
            'east_title_pos': (6962.9, 567.8),
            'east_box': (6850, 7150, 450, 750)
        },
        'level1': {
            'box': (950, 1600, -2100, -1350),
            'title': 'ADMIRAL MARINA CLUB — 1ST FLOOR',
            'identity': '1st Floor / Level 1',
            'east_title_pos': (7256.0, 567.8),
            'east_box': (7150, 7450, 450, 750)
        },
        'upper': {
            'box': (450, 1050, -2100, -1500),
            'title': 'ADMIRAL MARINA CLUB — UPPER FLOOR / PLANT',
            'identity': 'Upper Floor / Plant',
            'east_title_pos': (7173.7, 608.1),
            'east_box': (7050, 7350, 550, 750)
        },
        'roof': {
            'box': (-200, 400, -2400, -1900),
            'title': 'ADMIRAL MARINA CLUB — ROOF PLAN',
            'identity': 'Roof Floor',
            'east_title_pos': (6789.0, 411.6),
            'east_box': (6650, 6950, 300, 500)
        },
        'site_plan': {
            'box': (500, 1300, -2400, -1900),
            'title': 'ADMIRAL MARINA CLUB — SITE PLAN',
            'identity': 'Site Plan',
            'east_title_pos': (7003.2, 411.6),
            'east_box': (6850, 7150, 300, 500)
        }
    }

    # Extract device texts from modelspace
    device_types = {'BG': 'Break Glass', 'SD': 'Smoke Detector', 'HD': 'Heat Detector',
                    'CO2': 'CO2 Extinguisher', 'DP': 'Dry Powder', 'HR': 'Hose Reel',
                    'FS': 'Flow Switch', 'S': 'Smoke Detector', 'H': 'Heat Detector',
                    'A/C': 'Air Con Interlock', 'FL': 'Flow Switch'}

    for name, cfg in floors_config.items():
        x0, x1, y0, y1 = cfg['box']
        mimic_ents = []
        for e in msp:
            if e.dxf.layer != 'MIMIC_SIZE': continue
            t = e.dxftype()
            pts = []
            if t == 'LINE': pts = [(e.dxf.start[0], e.dxf.start[1]), (e.dxf.end[0], e.dxf.end[1])]
            elif hasattr(e.dxf, 'center'): pts = [(e.dxf.center[0], e.dxf.center[1])]
            elif hasattr(e.dxf, 'insert'): pts = [(e.dxf.insert[0], e.dxf.insert[1])]
            elif t == 'POLYLINE': pts = [(v.dxf.location[0], v.dxf.location[1]) for v in e.vertices]

            if pts and all(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in pts):
                mimic_ents.append(e)

        # Get bounds
        xs, ys = [], []
        for e in mimic_ents:
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

        # Extract device references in East box
        ex0, ex1, ey0, ey1 = cfg['east_box']
        devices = []
        dev_id = 1
        for e in msp.query('TEXT MTEXT'):
            txt = e.dxf.text if e.dxftype() == 'TEXT' else e.text
            t_clean = txt.strip()
            px, py = e.dxf.insert[0], e.dxf.insert[1]
            if ex0 <= px <= ex1 and ey0 <= py <= ey1 and t_clean in device_types:
                # Map coordinate normalized relative to floor bounds
                rel_x = (px - ex0) / (ex1 - ex0)
                rel_y = (py - ey0) / (ey1 - ey0)
                mapped_x = min_x + rel_x * (max_x - min_x)
                mapped_y = min_y + rel_y * (max_y - min_y)
                devices.append({
                    'id': f'ADM-{name.upper()}-{dev_id:03d}',
                    'code': t_clean,
                    'type': device_types[t_clean],
                    'dxf_x': round(mapped_x, 2),
                    'dxf_y': round(mapped_y, 2),
                    'layer': e.dxf.layer,
                    'source_cad_x': round(px, 2),
                    'source_cad_y': round(py, 2)
                })
                dev_id += 1

        # Write devices JSON
        devices_path = f'admiral_{name}_devices.json'
        with open(devices_path, 'w') as f:
            json.dump(devices, f, indent=2)

        # Write metadata JSON
        metadata = {
            'site': 'Admiral Marina Club',
            'floor_key': name,
            'floor_identity': cfg['identity'],
            'title': cfg['title'],
            'source_dxf': 'sources/batch-02/ADMIRAL MARINA CLUB.dxf',
            'runtime_inventory_status': 'NOT_IN_MANIFEST',
            'discrepancy_reason': 'Site "Admiral Marina Club" is not present in the current 152-floor runtime manifest; source-supported drawing recovered for review.',
            'review_status': 'REVIEW_REQUIRED',
            'entity_count': len(mimic_ents),
            'device_count': len(devices),
            'bounds': {
                'min_x': round(min_x, 2),
                'max_x': round(max_x, 2),
                'min_y': round(min_y, 2),
                'max_y': round(max_y, 2),
                'width': round(max_x - min_x, 2),
                'height': round(max_y - min_y, 2)
            },
            'identity_evidence': {
                'source_text': cfg['title'],
                'dxf_layer': 'MIMIC_SIZE',
                'cad_region_box': [round(min_x, 2), round(max_x, 2), round(min_y, 2), round(max_y, 2)]
            }
        }
        metadata_path = f'admiral_{name}_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Extracted {name}: {len(mimic_ents)} entities, {len(devices)} devices -> {devices_path}, {metadata_path}")

if __name__ == '__main__':
    extract()
