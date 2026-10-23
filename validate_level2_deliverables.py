import os
import json
import xml.etree.ElementTree as ET

def test_svg():
    path = 'avillion_level2_mimic.svg'
    assert os.path.exists(path), f"{path} missing"
    assert os.path.getsize(path) > 1000, f"{path} too small"
    tree = ET.parse(path)
    root = tree.getroot()
    assert 'svg' in root.tag, f"{path} is not valid SVG"
    print("✓ Level 2 SVG deliverable valid")

def test_png():
    path = 'avillion_level2_mimic.png'
    assert os.path.exists(path), f"{path} missing"
    assert os.path.getsize(path) > 10000, f"{path} too small"
    print("✓ Level 2 PNG deliverable valid")

def test_json():
    path = 'avillion_level2_devices.json'
    assert os.path.exists(path), f"{path} missing"
    with open(path, 'r') as f:
        data = json.load(f)
    assert 'building' in data
    assert 'devices' in data
    assert len(data['devices']) > 0
    print(f"✓ Level 2 JSON deliverable valid ({len(data['devices'])} devices)")

def test_comparison_image():
    path = 'level2_visual_comparison.png'
    assert os.path.exists(path), f"{path} missing"
    assert os.path.getsize(path) > 10000, f"{path} too small"
    print("✓ Level 2 visual comparison image deliverable valid")

def test_html_review():
    path = 'level2_review.html'
    assert os.path.exists(path), f"{path} missing"
    with open(path, 'r') as f:
        content = f.read()
    assert 'REVIEW_REQUIRED' in content, "REVIEW_REQUIRED flag missing in level2_review.html"
    assert 'level2_visual_comparison.png' in content
    assert 'avillion_level2_mimic.svg' in content
    print("✓ Level 2 HTML review page deliverable valid")

if __name__ == '__main__':
    test_svg()
    test_png()
    test_json()
    test_comparison_image()
    test_html_review()
    print("\nALL LEVEL 2 DELIVERABLE VALIDATIONS PASSED SUCCESSFULLY!")
