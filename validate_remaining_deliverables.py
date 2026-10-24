import os
import json
import xml.etree.ElementTree as ET

FLOORS = [
    ('level4', 'Level 4'),
    ('level5', 'Level 5'),
    ('penthouse_lower', 'Penthouse Lower (Level 6)'),
    ('level6a', 'Level 6A'),
    ('level6b', 'Level 6B (WTL & LMR)')
]

def validate_floor(key, name):
    print(f"\n--- Validating {name} ---")

    # SVG validation
    svg_path = f"avillion_{key}_mimic.svg"
    assert os.path.exists(svg_path), f"Missing {svg_path}"
    assert os.path.getsize(svg_path) > 1000, f"{svg_path} size too small"
    tree = ET.parse(svg_path)
    root = tree.getroot()
    assert 'svg' in root.tag, f"{svg_path} invalid SVG root tag"
    print(f"  ✓ {svg_path} valid ({os.path.getsize(svg_path)} bytes)")

    # PNG validation
    png_path = f"avillion_{key}_mimic.png"
    assert os.path.exists(png_path), f"Missing {png_path}"
    assert os.path.getsize(png_path) > 10000, f"{png_path} size too small"
    print(f"  ✓ {png_path} valid ({os.path.getsize(png_path)} bytes)")

    # JSON validation
    json_path = f"avillion_{key}_devices.json"
    assert os.path.exists(json_path), f"Missing {json_path}"
    with open(json_path, 'r') as f:
        data = json.load(f)
    assert 'building' in data and data['building'] == 'AVILLION RIOU'
    assert 'devices' in data
    assert len(data['devices']) > 0
    print(f"  ✓ {json_path} valid ({len(data['devices'])} devices)")

    # Comparison PNG validation
    comp_path = f"{key}_visual_comparison.png"
    assert os.path.exists(comp_path), f"Missing {comp_path}"
    assert os.path.getsize(comp_path) > 10000, f"{comp_path} size too small"
    print(f"  ✓ {comp_path} valid ({os.path.getsize(comp_path)} bytes)")

    # Review HTML validation
    html_path = f"{key}_review.html"
    assert os.path.exists(html_path), f"Missing {html_path}"
    with open(html_path, 'r') as f:
        content = f.read()
    assert 'REVIEW_REQUIRED' in content, f"REVIEW_REQUIRED missing in {html_path}"
    assert comp_path in content, f"Comparison image reference missing in {html_path}"
    assert svg_path in content, f"SVG reference missing in {html_path}"
    print(f"  ✓ {html_path} valid (contains REVIEW_REQUIRED flag & media refs)")

if __name__ == '__main__':
    for key, name in FLOORS:
        validate_floor(key, name)
    print("\n=======================================================")
    print("ALL REMAINING AVILLION FLOORS QA VALIDATIONS PASSED!")
    print("=======================================================")
