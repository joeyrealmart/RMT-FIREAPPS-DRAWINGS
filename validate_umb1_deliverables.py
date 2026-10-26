import json
import xml.etree.ElementTree as ET
import os

def validate():
    floors = ['umb_1_p1', 'umb_1_p2', 'umb_1_p3', 'umb_1_p4']

    for fkey in floors:
        svg_file = f"{fkey}_mimic.svg"
        meta_file = f"{fkey}_metadata.json"
        dev_file = f"{fkey}_devices.json"

        # Check file existence
        for f in (svg_file, meta_file, dev_file):
            assert os.path.exists(f), f"File missing: {f}"

        # Parse SVG XML
        try:
            tree = ET.parse(svg_file)
            root = tree.getroot()
            assert root.tag.endswith('svg'), f"Root tag of {svg_file} is not svg"
            print(f"Validated SVG XML: {svg_file}")
        except Exception as e:
            raise AssertionError(f"Failed to parse {svg_file}: {e}")

        # Parse metadata JSON
        with open(meta_file) as f:
            meta = json.load(f)
            assert meta.get('site') == 'UMB-1', f"Invalid site in {meta_file}"
            assert meta.get('review_status') == 'REVIEW_REQUIRED', f"Invalid review_status in {meta_file}"
            assert 'bounds' in meta, f"Missing bounds in {meta_file}"
            print(f"Validated Metadata JSON: {meta_file} (review_status={meta['review_status']})")

        # Parse devices JSON
        with open(dev_file) as f:
            devs = json.load(f)
            assert isinstance(devs, list), f"{dev_file} must be a list"
            for d in devs:
                assert 'device_label' in d and 'cad_location' in d and 'svg_location' in d
            print(f"Validated Devices JSON: {dev_file} ({len(devs)} devices)")

    print("\nAll UMB-1 deliverables validated successfully!")

if __name__ == '__main__':
    validate()
